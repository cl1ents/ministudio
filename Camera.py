import pymunk, pygame

from pymunk import Vec2d

#from pymunk

class Camera:
    def __init__(self, app):
        self.app = app
        player = app.Player
        self.position = Vec2d(player.body.position.x-app.screenSize.x/2, player.body.position.y+app.screenSize.y*.65)
        self.xGoal = 0
        self.yGoal = 0

        self.velocity = Vec2d(0,0)

    def update(self):
        app = self.app
        player = app.Player

        self.xGoal = player.body.position.x-app.screenSize.x/2
        self.yGoal = player.body.position.y+app.screenSize.y*.65
        self.position = Vec2d(self.position.x+(self.xGoal-self.position.x)*min(self.app.deltaTime*15, 1), self.position.y+(self.yGoal-self.position.y)*min(self.app.deltaTime*3, 1))
        
        #self.velocity = player.body.velocity
        #self.position += self.velocity * self.app.deltaTime

        app.cameraOffset = self.position
