import pymunk
from pymunk import Body

import pygame
import pygame.draw as draw

from constants import *
from PhysicsObject import PhysicsObject

from pymunk.autogeometry import convex_decomposition

from random import randint

class Baseplate(PhysicsObject): # SANDBOX!
    def __init__(self, app):
        super().__init__(app)
        self.body.body_type=Body.STATIC
        self.app.space.add(self.body)

        self.polygons = []
        self.pointList = []
        self.x = -100
        self.filter = pymunk.ShapeFilter(categories = MAP_CATEGORY)
        self.floor = [[(self.x, 0) ,(self.x, 25), (self.x + 2000 , 25), (self.x + 2000 , 0)], 
        [(self.x + 2500 , 0) ,(self.x+ 2500 , 25), (self.x + 4000  , 25), (self.x + 4000 , 0)], 
        [(self.x + 2600 , 25) ,(self.x+ 2700, 150), (self.x + 3800, 150), (self.x + 3900, 25)], 
        [(self.x + 4300 , 0) ,(self.x+ 4300 , 300), (self.x + 6000 , 300), (self.x + 6000 , 0)], 
        [(self.x + 6500 , 0) ,(self.x+ 6500 , 300), (self.x + 7000 , 300), (self.x + 7000, 0)], 
        [(self.x + 7000 , 0) ,(self.x + 7000 , 300), (self.x + 9000, 25), (self.x + 9000, 0)],
        [(self.x + 10000 , 0) ,(self.x + 10000 , 25), (self.x + 15000, 25), (self.x + 15000, 0)],
        [(self.x + 13000 , 0) ,(self.x + 13000 , 25), (self.x + 15000, 150), (self.x + 15000, 0)]]
        self.speed = 1

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
            pointList.append(pointList[0])
            pointList.reverse()
            triangleList = [pointList]
            try:
                triangleList = convex_decomposition(pointList, 1)
            except:
                try:
                    pointList.reverse()
                    triangleList = convex_decomposition(pointList, 1)
                except:
                    pass

            for tri in triangleList:
                poly = pymunk.Poly(self.body, tri)
                poly.mass = 1
                poly.friction = 1
                poly.filter = self.filter
                self.polygons.append(poly)
                self.app.space.add(poly)

    def clear(self):
        self.app.space.remove(*self.polygons)
        self.polygons = []
        for poly in self.floor:
            self.createPoly(poly)

    def update(self):
        super().update()

    def render(self):
        for poly in self.polygons:
            draw.polygon(self.app.screen, (0, 0, 0),[(self.app.convertCoordinates(i)) for i in poly.get_vertices()])
        # draw.rect(self.app.screen, "Blue", self.getRect())

    """
    def getRect(self):
        x, y = self.app.convertCoordinates((self.body.position[0]-self.size[0]/2, self.body.position[1]+self.size[1]/2))
        w, h = self.size
        return pygame.Rect(x, y, w, h)
    """