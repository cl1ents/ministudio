import pygame, pymunk

import pygame.display as display
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

import pygame.draw as draw
import pygame.font as font
from pygame.image import load
from pygame.locals import *
from pygame import Vector2, Rect

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
        iconSurf = load("res/img/rageon.png")
        display.set_icon(iconSurf)

        self.comicsans = font.SysFont("Comic Sans MS", 20)

        self.cameraOffset = Vec2d(0,0)
        
        self.realScreen = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), WINDOW_FLAGS)
        self.screen = pygame.Surface(RENDER_SIZE).convert()
        self.screenSize = Vector2(self.screen.get_size())
        self.screenRect = Rect(0, 0, self.screenSize.x, self.screenSize.y)
        self.realScreenSize = Vector2(display.get_window_size())

        self.fovScale = 1

        self.space = pymunk.Space()
        self.space.gravity = 0, -1800
        self.clock = pygame.time.Clock()

        self.deltaTime = 1/FPS
        self.time = 0
        self.running = True
        self.gaming = False
        
        #self.Baseplate = Baseplate(self)
        self.Player = Player(self)
        self.EnemyHandler = EnemyHandler(self)
        self.Camera = Camera(self)
        self.background = pygame.image.load("res/img/bg.png")
        self.logo = pygame.transform.scale(pygame.image.load("res/img/rageon.png"), (1280, 500))
        self.play = pygame.transform.scale(pygame.image.load("res/img/UI_play.png"), (500, 200))
        self.background.convert()
        self.logo.convert()
        self.play.convert()
        self.logoRect = self.logo.get_rect()
        self.playRect = self.play.get_rect()
        self.playRect.center = 640, 600


        self.LevelLoader = LevelLoader(self, "Level #3.json")
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
        x, y = (point[0]-self.screenRect.x)/(self.screenRect.w/self.screenSize.x), (point[1]-self.screenRect.y)/(self.screenRect.h/self.screenSize.y)

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
        
        sizeTarget = Vector2(RENDER_SIZE)*self.fovScale
        if self.screenSize != sizeTarget:
            self.screen = pygame.transform.scale(self.screen, sizeTarget) # pygame.Surface(sizeTarget).convert()
            self.screenSize = Vector2(self.screen.get_size())
    
    def render(self):
        self.screen.fill('white')
        #self.screen.blit(self.background, pygame.rect.Rect(0,0, 1280, 720))
        #self.Baseplate.render()
        self.Player.render()
        self.EnemyHandler.render()
        self.LevelLoader.render()

        size = (self.realScreenSize.x, self.realScreenSize.x / 16 * 9)
        if self.realScreenSize.y > size[1]:
            size = (self.realScreenSize.y / 9 * 16, self.realScreenSize.y)
        
        screen_scaled = pygame.transform.smoothscale(self.screen, size)
        self.screenRect = screen_scaled.get_rect(center=self.realScreenSize/2)
        self.realScreen.blit(screen_scaled, self.screenRect)
        
    def run(self):
        while self.running:
            screen = self.screen
            self.realScreenSize = Vector2(display.get_window_size())

            if self. gaming:
                self.events()
                self.update()
                self.render()

            if not self.gaming:
                self.realScreen.blit(self.logo, self.logoRect)
                self.realScreen.blit(self.play, self.playRect)
                for event in pygame.event.get():
                    match event.type:
                        case pygame.KEYDOWN:
                            match event.key:
                                case pygame.K_SPACE:
                                    self.gaming = True

          

            # self.surf.fill("White")
            # self.space.debug_draw(self.options)
            # self.screen.blit(self.surf, (0,0))
            
            # Dump screen
            display.flip()

            self.deltaTime = self.clock.tick(FPS) / 1000  # limits FPS to 60
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()