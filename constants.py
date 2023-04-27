from pygame.locals import *

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

RENDER_SIZE = (1920, 1080)

WINDOW_FLAGS = RESIZABLE | SHOWN

FPS = 120

PLAYER_CATEGORY = 0b00001
ENEMY_CATEGORY = 0b00010
MAP_CATEGORY = 0b00100

MAX_BULLET_LIFETIME = 12

COLLTYPE_PLAYER = 1
COLLTYPE_ENEMY = 2
COLLTYPE_BULLET = 3
COLLTYPE_ENV = 4

DEBUG = False