import pymunk, pygame

from pymunk import Vec2d
from constants import *

from pygame.image import load

from Helpers import lerp, clamp01
from easing_functions import *

#from pymunk

class Camera:
    mask = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS()^PLAYER_CATEGORY^ENEMY_CATEGORY)
    minFov = 0.9
    maxFov = 1.3
    maxSpeed = 2500
    scrollSpeed = 600

    def __init__(self, app):
        self.app = app
        player = app.Player
        self.position = player.body.position
        self.goal = player.body.position
        self.xScrollPos = 0

        self.fovGoal = 1

        self.velocity = Vec2d(0,0)

    def update(self):
        app = self.app
        player = app.Player



        self.xScrollPos = max(self.xScrollPos + (self.scrollSpeed * app.gaming) * self.app.deltaTime, player.body.position.x)

        scrollPos = Vec2d(self.xScrollPos, player.body.position.y)
        seg = app.space.segment_query_first(scrollPos, scrollPos+Vec2d(0, -500), 2, self.mask)

        position = seg.point if seg else scrollPos+Vec2d(0, -500)
        self.goal = Vec2d(position.x, position.y+app.screenSize.y/4)
        self.goal += Vec2d(player.body.velocity.x * .2, player.body.velocity.y * .01)
        self.position = Vec2d(self.position.x+(self.goal.x-self.position.x)*min(self.app.deltaTime*15, 1), self.position.y+(self.goal.y-self.position.y)*min(self.app.deltaTime*10, 1))
        self.fovGoal = self.CalculateFOV(int(player.body.velocity.get_distance((0,0))))
        
        app.fovScale = app.fovScale + (self.fovGoal-app.fovScale)*min(self.app.deltaTime*6, 1)
        #targetVelocity = 
        #self.velocity = self.velocity+(player.body.velocity-self.velocity)*min(self.app.deltaTime*15, 1)
        #self.position += self.velocity * self.app.deltaTime

        app.cameraOffset = Vec2d(self.position.x-app.screenSize.x/2, self.position.y+app.screenSize.y/2) # self.position

        self.playerInCameraView()

    def CalculateFOV(self, speed):
        alpha = clamp01(speed / self.maxSpeed)
        return lerp(self.minFov, self.maxFov, alpha, QuinticEaseIn)
    
    def playerInCameraView(self):
        plr = self.app.Player
        coords = self.app.convertCoordinates(plr.body.position)
        if coords[0] <= 0:
            self.app.retry()