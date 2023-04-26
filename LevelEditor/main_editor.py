import pygame
import pygame.display as display
import pygame.time as time
import pygame.cursors as cursors
import pygame.mouse as mouse
from pygame.image import load

from editor_constants import *

from Editor import Editor

class Main:
    def __init__(self):
        pygame.init()
        self.displaySurface = display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.clock = time.Clock()

        self.editor = Editor()

        surf = load('res/img/mouse.png').convert_alpha()
        cursor = cursors.Cursor((0,0), surf)
        mouse.set_cursor(cursor)

    def run(self):
        while True:
            dt = self.clock.tick(MAX_FRAMERATE) / 1000

            self.editor.run(dt)
            display.update()

if __name__ == '__main__':
    main = Main().run()