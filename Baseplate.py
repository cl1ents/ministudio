from BaseLevel import BaseLevel
import pygame
from pygame import draw

class Baseplate(BaseLevel):
    def __init__(self, app):
        self.x = -100
        self.floor = [[(self.x, -50) ,(self.x, -25), (self.x + 2000 , -25), (self.x + 2000 , -50)], 
        [(self.x + 2500 , -50) ,(self.x+ 2500 , -25), (self.x + 4000  , -25), (self.x + 4000 , -50)], 
        [(self.x + 2600 , -25) ,(self.x+ 2700, 125), (self.x + 3800, 125), (self.x + 3900, -25)], 
        [(self.x + 4300 , -50) ,(self.x+ 4300 , 250), (self.x + 6500 , 250), (self.x + 6500 , -50)], 
        [(self.x + 6500 , -50) ,(self.x+ 6500 , 250), (self.x + 7000 , 250), (self.x + 7000, -50)], 
        [(self.x + 7000 , -50) ,(self.x + 7000 , 250), (self.x + 9000, -25), (self.x + 9000, -25)],
        [(self.x + 9500 , -50) ,(self.x + 9500 , -25), (self.x + 12000, -25), (self.x + 12000, -50)],
        [(self.x + 10000 , -50) ,(self.x + 10000 , -25), (self.x + 12000, 250), (self.x + 12000, -50)]]

        super().__init__(app)
    
    def event(self, event):
        match event.type:
            case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LSHIFT:
                            self.clear()
            case pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        self.pointList.append(self.app.convertCoordinatesFromScreen(pygame.mouse.get_pos()))
                    case 3:
                        print(self.pointList)
                        self.createPoly(self.pointList)
                        self.pointList = []

    def clear(self):
        super().clear()
        for poly in self.floor:
            self.createPoly(poly)

    def render(self):
        super().render()
        if len(self.Baseplate.pointList) > 2:
            draw.polygon(self.app.screen, "Navy", [(self.convertCoordinates(i)) for i in self.Baseplate.pointList])