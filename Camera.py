import pymunk, pygame

from pymunk import Vec2d

#from pymunk

class Camera:
    def __init__(self, app):
        self.app = app
        self.position = 0, 0

    def update(self):
        app = self.app
        player = app.Player

        app.cameraOffset = Vec2d(player.body.position.x-app.screenSize.x/2, player.body.position.y+app.screenSize.y*.75)
