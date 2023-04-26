import pymunk, pygame

from pymunk import Vec2d
from constants import *

#from pymunk

class Camera:
    mask = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS()^PLAYER_CATEGORY^ENEMY_CATEGORY)

    def __init__(self, app):
        self.app = app
        player = app.Player
        self.position = player.body.position
        self.xGoal = 0
        self.yGoal = 0

        self.velocity = Vec2d(0,0)

    def update(self):
        app = self.app
        player = app.Player

        seg = app.space.segment_query_first(player.body.position, player.body.position+Vec2d(0, -500), 2, self.mask)

        position = seg.point if seg else player.body.position+Vec2d(0, -500)
        self.xGoal = position.x
        self.yGoal = position.y+app.screenSize.y/4
        self.position = Vec2d(self.position.x+(self.xGoal-self.position.x)*min(self.app.deltaTime*15, 1), self.position.y+(self.yGoal-self.position.y)*min(self.app.deltaTime*10, 1))
        
        #targetVelocity = 
        #self.velocity = self.velocity+(player.body.velocity-self.velocity)*min(self.app.deltaTime*15, 1)
        #self.position += self.velocity * self.app.deltaTime

        app.cameraOffset = Vec2d(self.position.x-app.screenSize.x/2, self.position.y+app.screenSize.y/2) # self.position
