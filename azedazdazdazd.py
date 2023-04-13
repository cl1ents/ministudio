import pygame
import pymunk
import pymunk.pygame_util

pygame.init()

space = pymunk.Space()
space.gravity = 0, 1000
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

options = pymunk.pygame_util.DrawOptions(screen)

try:
    body = pymunk.Body()
    body.position = 250, 250
    circle = pymunk.Circle(body, 50)
    circle.density = 1
    space.add(body, circle)
except:
    pass

try:
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    # body.position = 250, 250
    segment = pymunk.Segment(body, (0, 400), (500, 400), 10)
    space.add(body, segment)
except:
    pass

playing = True
while playing:
    for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    playing = False
    
    screen.fill("White")
    space.debug_draw(options)
    pygame.display.flip()
    space.step(clock.tick(60)/1000)