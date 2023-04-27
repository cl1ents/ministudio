import pygame, pymunk, time

import pygame.display as display
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
import pygame.mixer as mixer

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
from Button import Button

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
        
        self.Player = Player(self)
        self.EnemyHandler = EnemyHandler(self)
        self.Camera = Camera(self)
        self.bgSize = Vector2(2964, 1080)*self.Camera.maxFov
        self.bgRect = Rect(0, 0, self.bgSize.x, self.bgSize.y)
        self.background = pygame.transform.smoothscale(pygame.image.load("res/img/bg.png").convert(), self.bgSize)

        self.logo = pygame.image.load("res/img/rageon.png").convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, Vector2(self.logo.get_size())*.5)
        self.playButton = Button("res/img/UI_play.png", Rect(self.realScreenSize.x * 0.5, self.realScreenSize.y * 0.5,1197,348))
        self.playButton.realSprite = self.playButton.sprite
        self.playButton.bind(self.play)
        self.logoRect = self.logo.get_rect()

        self.startTime = 0

        self.LevelLoader = LevelLoader(self, "Level #5.json")
        self.LevelLoader.loadSave()

        self.Background = load("res/img/bg.png")

        try:
            mixer.init()
            mixer.music.load("res/music.mp3")
            mixer.music.play()
            mixer.music.set_volume(0.1)
        except:
            pass

    def play(self):
        if not self.gaming:
            self.gaming = True
            self.startTime = self.time

    def retry(self):
        self.Player.body.position = 0,0
        self.Player.body.angle = 0
        self.Player.body.angular_velocity = 0
        self.Camera.xScrollPos = 0
        self.Player.stun(0.4)
        for bullet in self.EnemyHandler.Bullets:
            self.space.remove(bullet.body, bullet.boundingBox)
        for enemy in self.EnemyHandler.Enemies:
            self.space.remove(enemy.body, enemy.boundingBox)
        self.EnemyHandler.Bullets.clear()
        self.LevelLoader.spawnEnemies()
        try:
            mixer.music.play()
        except:
            pass

    def events(self):
        global pointlist
        
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.retry()
                case pygame.K_SPACE:
                    self.play()
            if self.gaming:
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
        #self.Baseplate.render()
        self.screen.fill((66, 68, 87))

        self.bgRect.center = Vector2(((-self.Player.body.position.x/5)%self.bgSize.x), self.screenSize.y/2)
        self.screen.blit(self.background, (self.bgRect.x, self.bgRect.y))
        self.screen.blit(self.background, (self.bgRect.x-self.bgSize.x, self.bgRect.y))
        self.Player.render()
        self.EnemyHandler.render()
        self.LevelLoader.render()

        size = (self.realScreenSize.x, self.realScreenSize.x / 16 * 9)
        if self.realScreenSize.y > size[1]:
            size = (self.realScreenSize.y / 9 * 16, self.realScreenSize.y)
        
        screen_scaled = pygame.transform.scale(self.screen, size)
        self.screenRect = screen_scaled.get_rect(center=self.realScreenSize/2)
        self.realScreen.blit(screen_scaled, self.screenRect)
        
    def run(self):
        while self.running:
            self.realScreenSize = Vector2(display.get_window_size())

            
            self.events()
            self.update()
            self.render()

            if not self.gaming:
                logo = pygame.transform.scale(self.logo, Vector2(self.logo.get_size())*.5)
                logoRect = logo.get_rect()
                logoRect.center = self.realScreenSize/2
                self.realScreen.blit(logo, logoRect)
                self.playButton.sprite = pygame.transform.scale(self.playButton.realSprite, Vector2(self.playButton.realSprite.get_size())*.25)
                self.playButton.dest = self.playButton.sprite.get_rect(center = Vector2(self.realScreenSize.x/2, self.realScreenSize.y*.8))
                self.playButton.draw()
            else:
                self.realScreen.blit(self.comicsans.render(time.strftime("%M:%S", time.gmtime(self.time-self.startTime)), False, 'White'), (0,0))
            
            # Dump screen
            display.flip()

            self.deltaTime = self.clock.tick(FPS) / 1000
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()