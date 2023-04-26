import pygame, pymunk

import pygame.display as display
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

import pygame.draw as draw
import pygame.font as font
from pygame.locals import *
from pygame import Vector2

from Player import Player
from Camera import Camera
from EnemyHandler import EnemyHandler
from Baseplate import Baseplate
from constants import *

from LevelLoader import LevelLoader

pointlist = []
class App:
    def __init__(self):
        pygame.init()
        font.init()

        display.set_caption("Rageon")

        self.comicsans = font.SysFont("Comic Sans MS", 20)

        self.cameraOffset = Vec2d(0,0)
        
        self.screen = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), WINDOW_FLAGS)
        self.screenSize = Vector2(display.get_window_size())

        self.space = pymunk.Space()
        self.space.gravity = 0, -1500
        self.clock = pygame.time.Clock()
        
        self.surf = pygame.Surface(display.get_window_size())
        self.options = pymunk.pygame_util.DrawOptions(self.surf)

        self.deltaTime = 1/FPS
        self.time = 0
        self.running = True
        
        #self.Baseplate = Baseplate(self)
        self.Player = Player(self)
        self.EnemyHandler = EnemyHandler(self)
        self.EnemyHandler.instantiateEnemy((300, 500), 64)
        self.Camera = Camera(self)

        self.LevelLoader = LevelLoader(self)
        self.LevelLoader.loadSave()

    def events(self):
        global pointlist
        
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
            self.Player.event(event)
            #self.Baseplate.event(event)

    def convertCoordinates(self, point):
        x, y = point[0], (self.screenSize.y-point[1])

        x -= self.cameraOffset[0]
        y -= self.screenSize.y-self.cameraOffset[1]

        return x, y
    
    def convertCoordinatesFromScreen(self, point):
        x, y = point[0], point[1]

        x += self.cameraOffset[0]
        y += self.screenSize.y-self.cameraOffset[1]

        y = self.screenSize.y-y

        return x, y

    def update(self):
        #self.Baseplate.update()
        self.Player.update()
        self.EnemyHandler.update()
        self.LevelLoader.update()

        self.space.step(self.deltaTime)

        self.Camera.update()
    
    def render(self):
        self.screen.fill('white')
        #self.Baseplate.render()
        self.Player.render()
        self.EnemyHandler.render()
        self.LevelLoader.render()
        
    def run(self):
        while self.running:
            screen = self.screen
            self.screenSize = Vector2(screen.get_width(), screen.get_height())

            self.events()
            self.update()
            self.render()

            # self.surf.fill("White")
            # self.space.debug_draw(self.options)
            # self.screen.blit(self.surf, (0,0))
            
            # Dump screen
            display.flip()

            self.deltaTime = self.clock.tick(FPS) / 1000  # limits FPS to 60
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()