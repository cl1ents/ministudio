import pymunk
from pymunk import Body

import pygame
import pygame.draw as draw

from constants import *
from PhysicsObject import PhysicsObject

from pymunk.autogeometry import convex_decomposition

from random import randint

class BaseLevel(PhysicsObject): # SANDBOX!
    def __init__(self, app):
        super().__init__(app)
        self.body.body_type=Body.STATIC
        self.app.space.add(self.body)

        self.polygons = []
        self.pointList = []
        self.filter = pymunk.ShapeFilter(categories = MAP_CATEGORY)
        
        self.clear()

    def event(self, event):
        super.event(event)

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
                poly.collision_type = COLLTYPE_ENV
                poly.color = (0, 0, 0)
                self.polygons.append(poly)
                self.app.space.add(poly)

    def clear(self):
        self.app.space.remove(*self.polygons)
        self.polygons = []

    def update(self):
        super().update()

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