import pygame
from pygame.locals import *
import math
import sys

class App:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))

        self.clock = pygame.time.Clock()
        self.deltaTime = 0
        self.time = 0
        self.running = True

    def run(self):
        img = pygame.image.load('licorne.png')
        img.convert()
        rect = img.get_rect()
        x = 1280/2
        y = 720-rect[2]//2
        jump = False
        v = 10
        m = 1
        dash = False
        while self.running:
            screen = self.screen

            # Handle quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Clear screen
            rect.center = x, y
            screen.fill("white")
            screen.blit(img, rect)

            # DRAW STUFF
            # pygame.draw.circle(screen, "Red", pygame.Vector2((x, y)), 40)
            
            for event in pygame.event.get():
           
                # if event object type is QUIT 
                # then quitting the pygame 
                # and program both. 
                if event.type == pygame.QUIT:
                    
                    # it will make exit the while loop
                    run = False
            
            # stores keys pressed
            keys = pygame.key.get_pressed()
            if jump == False:
                if keys[pygame.K_SPACE]:    
                
        
                # if space bar is pressed
                
                  
            # make isjump equal to True
                    jump = True
                elif keys[pygame.K_LEFT]:
                    if x > 0 + rect[2]//2:
                        x-=v
                elif keys[pygame.K_RIGHT]:
                    if x < 1280 - rect[2]//2:
                        x+=v
        
            # Dump screen
            if jump :
                F =(1 / 2)*m*(v**2)
                
                # change in the y co-ordinate
                y-= F
                
                # decreasing velocity while going up and become negative while coming down
                v = v-1
                if keys[pygame.K_LEFT]:
                    if x > 0 + rect[2]//2:
                        x-=10
                elif keys[pygame.K_RIGHT]:
                    if x < 1280 - rect[2]//2:
                        x+=10 
                
                # object reached its maximum height
                if v<0:
                    
                    # negative sign is added to counter negative velocity
                    m =-1
        
                # objected reaches its original state
                if v ==-11:
        
                    # making isjump equal to false 
                    jump = False
        
            
                    # setting original values to v and m
                    v = 10
                    m = 1
            
            # creates time delay of 10ms
            pygame.time.delay(10)
        
            # it refreshes the window
            pygame.display.update() 
            pygame.display.flip()

            self.deltaTime = self.clock.tick(144) / 1000  # limits FPS to 60
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()