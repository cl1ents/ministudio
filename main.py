import pygame

import pygame.display as display
import pygame.draw as draw
from pygame.locals import *
from pygame import Vector2

from Helpers import raycast
from Player import Player
from constants import *
import math

class Baseplate:
    def __init__(self, app):
        self.box = pygame.Rect(0,0,0,0)
    
    def update(self, app):
        self.box.x = 0
        self.box.y = app.screenSize.y - 50
        self.box.h = 50
        self.box.w = app.screenSize.x

    def render(self, app):
        draw.rect(app.screen, "Blue", self.box)

class App:
    def __init__(self):
        pygame.init()

        self.screen = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), WINDOW_FLAGS)
        self.screenSize = Vector2(display.get_window_size())
        
        self.clock = pygame.time.Clock()

        self.deltaTime = 0
        self.time = 0
        self.running = True
        
        self.Baseplate = Baseplate(self)
        self.Player = Player(self)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.Baseplate.update(self)
        self.Player.update(self)
    
    def render(self):
        self.screen.fill("white")
        self.Baseplate.render(self)
        self.Player.render(self)

        point = pygame.Vector2(pygame.mouse.get_pos())
        
        draw.circle(self.screen, "Yellow", raycast(point, point+Vector2(0,500), [self.Baseplate.box]) or point+Vector2(0,500), 40)

    def run(self):
        while self.running:
            screen = self.screen
            self.screenSize = Vector2(screen.get_width(), screen.get_height())

            self.events()
            self.update()
            self.render()
            
            # Dump screen
            display.flip()

            self.deltaTime = self.clock.tick(144) / 1000  # limits FPS to 60
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()