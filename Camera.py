import pymunk, pygame

from pymunk import Vec2d

#from pymunk

class Camera:
    def __init__(self, app):
        self.app = app
        self.position = Vec2d(0,0)
        self.xGoal = 0
        self.yGoal = 0

    def update(self):
        app = self.app
        player = app.Player

        self.xGoal = player.body.position.x-app.screenSize.x/2
        self.yGoal = player.body.position.y+app.screenSize.y*.75
        self.position = Vec2d(self.position.x+(self.xGoal-self.position.x)*min(self.app.deltaTime*15, 1), self.position.y+(self.yGoal-self.position.y)*min(self.app.deltaTime*2, 1))
        
        app.cameraOffset = self.position
