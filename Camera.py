import pymunk, pygame

from pymunk import Vec2d
from constants import *

from Helpers import lerp, clamp01
from easing_functions import *

#from pymunk

class Camera:
    mask = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS()^PLAYER_CATEGORY^ENEMY_CATEGORY)
    minFov = 0.9
    maxFov = 1.4
    maxSpeed = 2500

    def __init__(self, app):
        self.app = app
        player = app.Player
        self.position = player.body.position
        self.xGoal = 0
        self.yGoal = 0

        self.fovGoal = 1

        self.velocity = Vec2d(0,0)

    def update(self):
        app = self.app
        player = app.Player

        seg = app.space.segment_query_first(player.body.position, player.body.position+Vec2d(0, -500), 2, self.mask)

        position = seg.point if seg else player.body.position+Vec2d(0, -500)
        self.xGoal = position.x
        self.yGoal = position.y+app.screenSize.y/4
        self.position = Vec2d(self.position.x+(self.xGoal-self.position.x)*min(self.app.deltaTime*15, 1), self.position.y+(self.yGoal-self.position.y)*min(self.app.deltaTime*10, 1))
        
        self.fovGoal = self.CalculateFOV(int(player.body.velocity.get_distance((0,0))))
        
        app.fovScale = app.fovScale + (self.fovGoal-app.fovScale)*min(self.app.deltaTime*6, 1)
        #targetVelocity = 
        #self.velocity = self.velocity+(player.body.velocity-self.velocity)*min(self.app.deltaTime*15, 1)
        #self.position += self.velocity * self.app.deltaTime

        app.cameraOffset = Vec2d(self.position.x-app.screenSize.x/2, self.position.y+app.screenSize.y/2) # self.position

    def CalculateFOV(self, speed):
        alpha = clamp01(speed / self.maxSpeed)
        return lerp(self.minFov, self.maxFov, alpha, QuinticEaseIn)