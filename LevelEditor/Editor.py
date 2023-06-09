import sys, os, json, time, math

import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.transform as transform

from pygame import Surface, Rect, Color
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.key import get_pressed as key_pressed
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load

from random import randint

from editor_constants import *

from editor_helpers import clamp
from Button import Button

CW_SAVE = "Level #5.json"

class Editor:
    enemy_types_images = ["enemyA.png", "enemyB.png", "enemyC.png", "enemyD.png"]

    def __init__(self)->None:
        self.displaySurface = display.get_surface()
        
        # Navigation
        self.origin = vector()
        self.panActivate = False
        self.panOffset = vector()

        # Support lines
        self.supportLinesSurf = Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.supportLinesSurf.set_colorkey('green')
        self.supportLinesSurf.set_alpha(30)

        # tileSize
        self.tileSize = 64
        self.zoomFactor = 1
        self.clicked = False

        self.tiles = {}
        
        self.physicsEnabled = False
        self.physicsPoints = [[]]
        self.physicsDrawIndex = 0
        self.physicsStraightLines = False
        
        self.offGridEnabled = False
        self.offGridElements = []

        self.enemiesEnabled = False
        self.enemies = []
        self.enemyDrawIndex = 0

        self.drawDelay = 0.2
        self.lastDraw = time.time() - self.drawDelay

        self.originSprite = load("./res/img/idle.png").convert_alpha()

        # Buttons
        self.saveButton = Button("res/img/btn/save_button.png", (30,50))
        self.saveButton.bind(self.performSave)
        
        self.loadButton = Button("res/img/btn/load_button.png", (30, 125))
        self.loadButton.bind(self.loadSave)
        
        self.physicsEnabledButton = Button("res/img/btn/physics_button.png", (30,200))
        self.physicsEnabledButton.bind(self.enablePhysics)
        
        self.offGridButton = Button("res/img/btn/off_grid_button.png", (30, 275))
        self.offGridButton.bind(self.enableOffGrid)

        self.enemiesButton = Button("res/img/btn/enemies_button.png", (30, 350))
        self.enemiesButton.bind(self.enableEnemies)

        self.playerSprite = load("res/img/idle.png").convert_alpha()
        
        self.loadSave()

    def enablePhysics(self):
        self.physicsEnabled = not self.physicsEnabled
        
    def enableOffGrid(self):
        self.offGridEnabled = not self.offGridEnabled

    def enableEnemies(self):
        self.enemiesEnabled = not self.enemiesEnabled

    ### Tiling ###
    # pos: the gridbased x and y coordinates
    
    def getScaledTileSize(self, tileSize=DEFAULT_TILE_SIZE)->float:
        return int(tileSize * self.zoomFactor)
    
    def getCell(self, pos:tuple)->tuple:
        distanceToOrigin = vector(pos) - self.origin
        scaledTileSize = self.getScaledTileSize(self.tileSize)
        
        if distanceToOrigin.x > 0:
            col = int(distanceToOrigin.x / scaledTileSize)
        else:
            col = int(distanceToOrigin.x / scaledTileSize) - 1
        if distanceToOrigin.y > 0:
            row = int(distanceToOrigin.y / scaledTileSize)
        else:
            row = int(distanceToOrigin.y / scaledTileSize) - 1
    
        return col, row
    
    def getCurrentCell(self)->tuple:
        return self.getCell(mouse_pos())
    
    def eventLoop(self)->None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.panInput(event)
            self.changeEnemyIndex(event)
            self.draw()

    def panInput(self, event:pygame.event.Event)->None:
        # Middle mouse button pressed / released
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
            self.panActive = True
            self.panOffset = vector(mouse_pos()) - self.origin
        if not mouse_buttons()[1]:
            self.panActive = False
        
        # Mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if key_pressed()[pygame.K_LCTRL]:
                self.tileSize = int(clamp(self.tileSize + event.y * (self.tileSize / 2), MIN_TILE_SIZE, MAX_TILE_SIZE))
            else:
                self.zoomFactor = clamp(self.zoomFactor + event.y * ZOOM_STEP, MIN_ZOOM, MAX_ZOOM)
        
        # Panning update
        if self.panActive:
            self.origin = vector(mouse_pos()) - self.panOffset

    def changeEnemyIndex(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.enemyDrawIndex = (self.enemyDrawIndex + 1) % 4

    def loadSave(self, saveName:str=CW_SAVE)->None:
        path = os.path.join("saves/", saveName)
        self.tiles.clear()
        self.enemies.clear()
        self.offGridElements.clear()
        self.physicsPoints = [[]]
        self.physicsDrawIndex = 0
        
        if not os.path.exists(path):
            print("The save file wasn't found!")
            return
        
        with open(path, 'r') as f:
            data = json.load(f)
            
        self.physicsDrawIndex = data['drawIndex'] + 1

        for key, value in data['tiles'].items():
            # Formatting & converting coords to int
            coords = key.split(',')
            coords[0], coords[1] = int(coords[0]), int(coords[1])
            
            self.tiles[tuple(coords)] = {
                'surf': load(value['sprite_surf']).convert_alpha(),
                'path': value['sprite_surf'],
                'tiling': value['tiling']
            }
            
        for value in data['off-grid']:
            position = value['position'].split(',')
            position[0], position[1] = float(position[0]), float(position[1])
            self.offGridElements.append({
                'surf': load(value['sprite_surf']).convert_alpha(),
                'path': value['sprite_surf'],
                'position': tuple(position)
            })
        
        for pointCloud in data['physics']:
            tempPhysics = []
            for point in pointCloud:
                splittedPoint = point.split(',')
                tempPhysics.append((float(splittedPoint[0]), float(splittedPoint[1])))
            self.physicsPoints.append(tempPhysics)

        for enemy in data['enemies']:
            position = enemy['position'].split(',')
            position[0], position[1] = float(position[0]), float(position[1])
            self.enemies.append({
                'position': position,
                'type': enemy['type']
            })
    
    def performSave(self, saveName:str=CW_SAVE, name:str="Save #1")->None:
        path = path = os.path.join("saves/", saveName)
        
        with open(path, 'w') as f:
            save = {
                "name": name,
                "tiles": {},
                "off-grid": [],
                "physics": [],
                "enemies": [],
                "drawIndex": self.physicsDrawIndex
            }
            
            for key, value in self.tiles.items():
                coords = str(key[0]) + ',' + str(key[1])
                save['tiles'][coords] = {
                    'sprite_surf': value['path'],
                    'tiling': value['tiling']
                }
            
            for value in self.offGridElements:
                position = str(value['position'][0]) + ',' + str(value['position'][1])
                save['off-grid'].append({
                    'sprite_surf': value['path'],
                    'position': position
                })
            
            for i in range(len(self.physicsPoints)):
                pointCloud = []
                for point in self.physicsPoints[i]:
                    pointCloud.append(str(point[0])+ ',' + str(point[1]))
                save["physics"].append(pointCloud)

            for enemy in self.enemies:
                position = str(enemy['position'][0]) + ',' + str(enemy['position'][1])
                save['enemies'].append({
                    'position': position,
                    'type': enemy['type']
                })
            
            json.dump(save, f, indent=6)
            print("Successfully saved!")

        # Drawing
    def drawTileBorders(self)->None:
        scaledTileSize = self.getScaledTileSize(self.tileSize)
        cols = WINDOW_WIDTH // scaledTileSize
        rows = WINDOW_HEIGHT // scaledTileSize
        
        originOffset = vector(
            x = self.origin.x - int(self.origin.x / scaledTileSize) * scaledTileSize,
            y = self.origin.y - int(self.origin.y / scaledTileSize) * scaledTileSize
        )
        
        self.supportLinesSurf.fill('green')
        
        for col in range(cols+1):
            x = originOffset.x + col * scaledTileSize
            draw.line(self.supportLinesSurf, LINE_COLOR, (x,0), (x,WINDOW_HEIGHT))
            
        for row in range(rows+1):
            y = originOffset.y + row * scaledTileSize
            draw.line(self.supportLinesSurf, LINE_COLOR, (0,y), (WINDOW_WIDTH,y))
        
        self.displaySurface.blit(self.supportLinesSurf, (0,0))
    
    def physicsDraw(self):
        self.physicsStraightLines = key_pressed()[pygame.K_LSHIFT]

        if key_pressed()[pygame.K_x]:
            self.physicsPoints[self.physicsDrawIndex] = []
            print("LOL!")
        if mouse_buttons()[0] and not self.clicked:
            self.clicked = True
            if key_pressed()[pygame.K_LCTRL]:
                if len(self.physicsPoints[self.physicsDrawIndex]) > 2:
                    self.physicsDrawIndex += 1
                    self.physicsPoints.append([])
                    print("New Physics Shape")
            else:
                mousePoint = (vector(mouse_pos()) - self.origin) * (1 / self.zoomFactor)
                if len(self.physicsPoints[self.physicsDrawIndex]) >= 1 and self.physicsStraightLines:
                    point = vector(self.physicsPoints[self.physicsDrawIndex][len(self.physicsPoints[self.physicsDrawIndex])-1])

                    localPoint = mousePoint-point
                    if abs(localPoint.x) > abs(localPoint.y):
                        mousePoint = vector(mousePoint.x, point.y)
                    elif abs(localPoint.y) > abs(localPoint.x):
                        mousePoint = vector(point.x, mousePoint.y)
                self.physicsPoints[self.physicsDrawIndex].append(mousePoint)
        elif not mouse_buttons()[0]:
            self.clicked = False
        if mouse_buttons()[2]:
            for cloudPoint in self.physicsPoints:
                if len(cloudPoint) <= 2: continue
                minX, maxX, minY, maxY, w, h = math.inf, -math.inf, math.inf, -math.inf, None, None
                for point in cloudPoint:
                    offset = (vector(point) + self.origin) * self.zoomFactor
                    minX = min(minX, offset.x)
                    maxX = max(maxX, offset.x)
                    minY = min(minY, offset.y)
                    maxY = max(maxY, offset.y)
                w = maxX - minX
                h = maxY - minY
                polygon_rect = Rect(minX, minY, w, h)
                if polygon_rect.collidepoint(mouse_pos()):
                    self.physicsPoints.remove(cloudPoint)
                    self.physicsDrawIndex -= 1
                    print("Successfully removed!")
                    break
        
    
    def gridDraw(self):
        if mouse_buttons()[0]:
            self.tiles[self.getCurrentCell()] = {
                'surf': load('res/img/enemyA.png').convert_alpha(),
                'path': 'res/img/enemyA.png',
                'tiling': self.tileSize
            }
        if mouse_buttons()[2]: # Right click
            currentCell = self.getCurrentCell()
            if currentCell in self.tiles.keys():
                del self.tiles[currentCell]

    def offGridDraw(self):
        if time.time() - self.lastDraw < self.drawDelay: return
        if mouse_buttons()[0]:
            self.lastDraw = time.time()
            loaded_surf = load('res/img/enemyA.png').convert_alpha()
            rescaled = transform.scale(loaded_surf, vector(DEFAULT_TILE_SIZE,DEFAULT_TILE_SIZE) * self.zoomFactor)
            self.offGridElements.append({
                'surf': loaded_surf,
                'path': 'res/img/enemyA.png',
                'position': vector(mouse_pos()) - self.origin - vector(rescaled.get_size()) * 0.5
            })
        if mouse_buttons()[2]:
            for i in range(len(self.offGridElements)):
                value = self.offGridElements[i]
                rect = Rect(value['position'], value['surf'].get_size())
                if rect.collidepoint(mouse_pos()):
                    self.lastDraw = time.time()
                    del self.offGridElements[i]
                    break
                    
    def enemiesDraw(self):
        if time.time() - self.lastDraw < self.drawDelay: return
        if mouse_buttons()[0]:
            self.lastDraw = time.time()
            loaded_surf = load("res/img/"+self.enemy_types_images[self.enemyDrawIndex]).convert_alpha()
            rescaled = transform.scale(loaded_surf, vector(1,1) * DEFAULT_TILE_SIZE * self.zoomFactor)
            print(vector(1,1) * DEFAULT_TILE_SIZE * self.zoomFactor)
            self.enemies.append({
                "position": (vector(mouse_pos()) - self.origin - vector(DEFAULT_TILE_SIZE) * 0.5) * (1 / self.zoomFactor),
                "type": self.enemyDrawIndex
            })
        if mouse_buttons()[2]:
            for i in range(len(self.enemies)):
                enemy = self.enemies[i]
                rect = Rect(enemy['position'], (vector(1,1) * DEFAULT_TILE_SIZE))
                print(rect)
                print((vector(mouse_pos()) - self.origin - vector(DEFAULT_TILE_SIZE) * 0.5) * (1 / self.zoomFactor))
                if rect.collidepoint((vector(mouse_pos()) - self.origin - vector(DEFAULT_TILE_SIZE) * 0.5) * (1 / self.zoomFactor)):
                    self.lastDraw = time.time()
                    del self.enemies[i]
                    break

    def draw(self)->None:
        if self.saveButton.rect.collidepoint(mouse_pos()) or self.loadButton.rect.collidepoint(mouse_pos()) or self.physicsEnabledButton.rect.collidepoint(mouse_pos()) or self.offGridButton.rect.collidepoint(mouse_pos()) or self.enemiesButton.rect.collidepoint(mouse_pos()):
            return
        
        if self.enemiesEnabled:
            self.enemiesDraw()
        elif self.physicsEnabled:
            self.physicsDraw()
        elif self.offGridEnabled:
            self.offGridDraw()
        else:
            self.gridDraw()

    def drawTiles(self)->None:
        for value in self.offGridElements:
            pos = self.origin + vector(value['position']) * self.zoomFactor
            surf = transform.scale(value['surf'], vector(1,1) * DEFAULT_TILE_SIZE * self.zoomFactor)
            self.displaySurface.blit(surf, pos)
        
        for key, value in self.tiles.items():
            scaledTileSize = self.getScaledTileSize(value['tiling'])
            pos = self.origin + vector(key) * scaledTileSize
            surf = transform.scale(value['surf'], (scaledTileSize,scaledTileSize))
            self.displaySurface.blit(surf, pos)
            
        for enemy in self.enemies:
            pos = self.origin + vector(enemy['position']) * self.zoomFactor
            surf = transform.scale(load('res/img/'+self.enemy_types_images[enemy['type']]), vector(1,1) * DEFAULT_TILE_SIZE * self.zoomFactor)
            self.displaySurface.blit(surf, pos)

        if self.physicsEnabled:
            physicsSurf = Surface(self.displaySurface.get_size())
            physicsSurf.set_colorkey('green')
            physicsSurf.fill('green')
            for pointCloud in self.physicsPoints:
                if len(pointCloud) > 2:
                    offsetPointCloud = []
                    for point in pointCloud:
                        offsetPointCloud.append(self.origin + vector(point)  * self.zoomFactor)
                    rect = draw.polygon(physicsSurf, Color(255,0,0), offsetPointCloud)
            physicsSurf.set_alpha(155)

            mousePoint = (vector(mouse_pos()) - self.origin) * (1 / self.zoomFactor)
            if len(self.physicsPoints[self.physicsDrawIndex]) >= 1 and self.physicsStraightLines:
                point = vector(self.physicsPoints[self.physicsDrawIndex][len(self.physicsPoints[self.physicsDrawIndex])-1])

                localPoint = mousePoint-point
                if abs(localPoint.x) > abs(localPoint.y):
                    mousePoint = vector(mousePoint.x, point.y)
                elif abs(localPoint.y) > abs(localPoint.x):
                    mousePoint = vector(point.x, mousePoint.y)

                draw.circle(physicsSurf, 'red', self.origin + mousePoint  * self.zoomFactor, 10)


            if len(self.physicsPoints[self.physicsDrawIndex]) > 1:
                pointCloud = self.physicsPoints[self.physicsDrawIndex]
                offsetPointCloud = []
                for point in pointCloud:
                    offsetPointCloud.append(self.origin + vector(point)  * self.zoomFactor)
                
                offsetPointCloud.append(self.origin + mousePoint  * self.zoomFactor)

                rect = draw.polygon(physicsSurf, Color(255,255,0), offsetPointCloud)

            self.displaySurface.blit(physicsSurf, (0,0))
    
    def run(self, dt:float)->None:
        self.displaySurface.fill('white')
                
        # drawing
        self.eventLoop()
        self.drawTileBorders()
        self.drawTiles()
        self.saveButton.draw()
        self.loadButton.draw()
        self.physicsEnabledButton.draw()
        self.offGridButton.draw()
        self.enemiesButton.draw()
        draw.circle(self.displaySurface, 'red', self.origin, 10)

        playerSprite = pygame.transform.smoothscale(self.playerSprite, vector(175,175) * self.zoomFactor)
        playerRect = playerSprite.get_rect(center = self.origin+vector(0,-75*self.zoomFactor))
        self.displaySurface.blit(playerSprite, playerRect)
        