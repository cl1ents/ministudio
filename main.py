import pygame
import pymunk

import pygame.display as display
import pymunk.pygame_util
import pygame.draw as draw
from pygame.locals import *
from pygame import Vector2

from pymunk import Body

from Player import Player
from Baseplate import Baseplate
from constants import *
import math

pointlist = []
class App:
    def __init__(self):
        pygame.init()

        self.screen = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), WINDOW_FLAGS)
        self.screenSize = Vector2(display.get_window_size())

        self.space = pymunk.Space()
        self.space.gravity = 0, -1000
        self.space.add()
        self.clock = pygame.time.Clock()
        
        self.surf = pygame.Surface(display.get_window_size())
        self.options = pymunk.pygame_util.DrawOptions(self.surf)

        self.deltaTime = 1/FPS
        self.time = 0
        self.running = True
        
        self.Baseplate = Baseplate(self)
        self.Player = Player(self)

    def events(self):
        global pointlist
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_SPACE:
                            self.Player.jump()
                        case pygame.K_q:
                            self.Player.moveVector.x -= 1
                        case pygame.K_d:
                            self.Player.moveVector.x += 1
                        case pygame.K_r:
                            self.Player.body.position = self.convertCoordinates(pygame.mouse.get_pos())
                            self.Player.body.angle = 0
                        case pygame.K_LSHIFT:
                            self.Baseplate.clear()
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_q:
                            self.Player.moveVector.x += 1
                        case pygame.K_d:
                            self.Player.moveVector.x -= 1
                case pygame.MOUSEBUTTONDOWN:
                    print(event)
                    match event.button:
                        case 1:
                            pointlist.append(self.convertCoordinates(pygame.mouse.get_pos()))
                        case 3:
                            print(pointlist)
                            self.Baseplate.createPoly(pointlist)
                            pointlist = []
                # TODO, make keybinds modular!!

    def convertCoordinates(self, point):
        return point[0], self.screenSize.y-point[1]

    def update(self):
        self.Baseplate.update()
        self.Player.update()
        self.space.step(self.deltaTime)
    
    def render(self):
        self.screen.fill("white")
        self.Baseplate.render()
        self.Player.render()
        
        #point = self.convertCoordinates(pygame.mouse.get_pos())

        #seg = self.space.segment_query_first(point, (point[0], point[1]-500), 1, pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS()^PLAYER_CATEGORY))
        
        #draw.circle(self.screen, "Yellow", self.convertCoordinates((seg.point.x, seg.point.y)) if seg else self.convertCoordinates((point[0], point[1]-500)), 40)

    def run(self):
        while self.running:
            screen = self.screen
            self.screenSize = Vector2(screen.get_width(), screen.get_height())

            self.events()
            self.update()
            self.render()

            if len(pointlist) > 2:
                draw.polygon(screen, "Navy", [(self.convertCoordinates(i)) for i in pointlist])

            # self.surf.fill("White")
            # self.space.debug_draw(self.options)
            # self.screen.blit(self.surf, (0,0))
            
            # Dump screen
            display.flip()

            self.deltaTime = self.clock.tick(FPS) / 1000  # limits FPS to 60
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()