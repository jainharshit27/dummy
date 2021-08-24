import pygame, pymunk
import pymunk.pygame_util

def create_arrow():
    vs = [(-80, 0), (0, 2), (2, 0), (0, -2)]
    arrow_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    arrow_shape = pymunk.Poly(arrow_body, vs)
    arrow_shape.collision_type = 1
    arrow_shape.density = 0.1   
    return arrow_body, arrow_shape

def stick_arrow_to_target(space, arrow_body, target_body, position, flying_arrows):
    pivot_joint = pymunk.PivotJoint(arrow_body, target_body, position)
    phase = target_body.angle - arrow_body.angle
    gear_joint = pymunk.GearJoint(arrow_body, target_body, phase, 1)
    space.add(pivot_joint)
    space.add(gear_joint)
    try:
        flying_arrows.remove(arrow_body)
    except:
        pass

def post_solve_arrow_hit(arbiter, space, data):
    if arbiter.total_impulse.length > 10:
        a, b = arbiter.shapes
        position = arbiter.contact_point_set.points[0].point_a
        b.collision_type = 0
        b.group = 1
        other_body = a.body
        arrow_body = b.body
        space.add_post_step_callback(
            stick_arrow_to_target,
            arrow_body,
            other_body,
            position,
            data["flying_arrows"],
        )

pygame.init()
screen = pygame.display.set_mode((690, 600))
clock = pygame.time.Clock()

bg = pygame.image.load("bg.png")
bg = pygame.transform.scale(bg, (690,600))

space = pymunk.Space()
space.gravity = 0,1000
draw_options = pymunk.pygame_util.DrawOptions(screen)

vs_rect = [(1, -80), (1, 80), (-1, 80), (-1, -80)]
target_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
target_shape = pymunk.Poly(target_body, vs_rect)
target_body.position = 600,300
target_img = pygame.image.load("target.png")
target_img = pygame.transform.scale(target_img, (25,200))
space.add(target_body, target_shape)

cannon_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
cannon_shape = pymunk.Circle(cannon_body, 25)
cannon_img = pygame.image.load("bow.png")
cannon_img = pygame.transform.scale(cannon_img, (100,150))
cannon_shape.sensor = True
cannon_shape.color = (255, 50, 50, 255)
cannon_body.position = 100, 150
space.add(cannon_body, cannon_shape)

target_body_y = 5

arrow_body, arrow_shape = create_arrow()
space.add(arrow_body, arrow_shape)

arrow_img = pygame.image.load("arrow.png")
arrow_img = pygame.transform.scale(arrow_img, (80,5))

flying_arrows = []
handler = space.add_collision_handler(0, 1)
handler.data["flying_arrows"] = flying_arrows
handler.post_solve = post_solve_arrow_hit

while True:
    screen.blit(bg, (0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            start_time = pygame.time.get_ticks()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            end_time = pygame.time.get_ticks()

            diff = end_time - start_time
            power = min(diff, 1000) * 13.5
            impulse = (power*1, 0)
            arrow_body.body_type = pymunk.Body.DYNAMIC
            arrow_body.apply_impulse_at_world_point(impulse, arrow_body.position)

            flying_arrows.append(arrow_body)
            arrow_body, arrow_shape = create_arrow()
            space.add(arrow_body, arrow_shape)
            screen.blit(arrow_img, (round(arrow_shape.body.position.x-100), round(arrow_shape.body.position.y-100)))
            
    if target_body.position.y > 550:
        target_body_y = -5
    if target_body.position.y < 0:
        target_body_y = 5

    target_body.position = 600, target_body.position.y + target_body_y
    arrow_body.position = cannon_body.position #+ Vec2d(cannon_shape.radius + 40, 0).rotated(cannon_body.angle)
    #arrow_body.angle = cannon_body.angle
    
    space.debug_draw(draw_options)
    
    screen.blit(cannon_img, (round(cannon_shape.body.position.x-100), round(cannon_shape.body.position.y-100)))
    screen.blit(target_img, (round(target_body.position.x-10), round(target_body.position.y-80)))
    screen.blit(arrow_img, (round(arrow_shape.body.position.x), round(arrow_shape.body.position.y)))
    
    if pygame.mouse.get_pressed()[0]:
        current_time = pygame.time.get_ticks()
        diff = current_time - start_time
        power = min(diff, 1000)
        h = power / 2
        pygame.draw.line(screen, pygame.Color("red"), (30, 550), (30, 550 - h), 10)

    pygame.display.update()

    space.step(1/60)
    clock.tick(60)