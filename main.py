import pygame
from pygame.locals import *
import math

class App:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720), RESIZABLE)

        self.clock = pygame.time.Clock()
        self.deltaTime = 0
        self.time = 0
        self.running = True

    def run(self):
        while self.running:
            screen = self.screen

            # Handle quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Clear screen
            screen.fill("white")

            # DRAW STUFF
            # pygame.draw.circle(screen, "Red", pygame.Vector2(pygame.mouse.get_pos()), 40)

            # Dump screen
            pygame.display.flip()

            self.deltaTime = self.clock.tick(144) / 1000  # limits FPS to 60
            self.time += self.deltaTime

if __name__ == "__main__":
    App().run()