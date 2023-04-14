import pymunk
from pymunk import Body

import pygame
import pygame.draw as draw

from constants import *
from PhysicsObject import PhysicsObject

from random import randint

class Baseplate(PhysicsObject): # SANDBOX!
    def __init__(self, app):
        super().__init__(app)
        self.body.body_type=Body.STATIC
        self.app.space.add(self.body)

        self.polygons = []
        self.pointList = []

        self.filter = pymunk.ShapeFilter(categories = MAP_CATEGORY)

        self.createPoly([(0, 0) ,(0, 50), (1920, 50), (1920, 0)])

    def event(self, event):
        match event.type:
            case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LSHIFT:
                            self.clear()
            case pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        self.pointList.append(self.app.convertCoordinates(pygame.mouse.get_pos()))
                    case 3:
                        print(self.pointList)
                        self.createPoly(self.pointList)
                        self.pointList = []

    def createPoly(self, pointList):
        if len(pointList) > 2:
            poly = pymunk.Poly(self.body, pointList)
            poly.mass = 1
            poly.friction = 1
            poly.color = (randint(0, 255), randint(0, 255), randint(0, 255))
            poly.filter = self.filter
            self.polygons.append(poly)
            self.app.space.add(poly)

    def clear(self):
        self.app.space.remove(*self.polygons)
        self.polygons = []
        self.createPoly([(0, 0) ,(0, 50), (1920, 50), (1920, 0)])


    def render(self):
        for poly in self.polygons:
            draw.polygon(self.app.screen, poly.color, [(self.app.convertCoordinates(i)) for i in poly.get_vertices()])
        # draw.rect(self.app.screen, "Blue", self.getRect())

    """
    def getRect(self):
        x, y = self.app.convertCoordinates((self.body.position[0]-self.size[0]/2, self.body.position[1]+self.size[1]/2))
        w, h = self.size
        return pygame.Rect(x, y, w, h)
    """