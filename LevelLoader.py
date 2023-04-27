import json, os, time

from pygame.image import load
import pygame.draw as draw
from pygame import Color

from BaseLevel import BaseLevel

from random import randint
from Helpers import  clamp01, colorLerp, isOffScreen
from easing_functions import *
from EnemyHandler import Enemy, EnemyConfig

class LevelLoader:
    enemy_types_images = ["enemyA.png", "enemyB.png", "enemyC.png", "enemyD.png"]

    def __init__(self, app, saveName="Level #1.json"):
        self.app = app
        self.saveName = saveName
        self.data = self.loadSave()
        self.BaseLevel = None

        if not self.data: return
        print("Save data successfully loaded!")
        
        self.BaseLevel = BaseLevel(app)
        self.color = self.generate_random_color()
        self.previousColor = self.color
        self.targetColor = self.color
        self.colorSwitchDelay = 7
        self.colorSwitchDuration = 3
        self.colorSwitchTime = time.time()
        self.colorSwitchAlpha = 1
        self.colorSwitchDelay = 5
        self.createPolygons()
        self.spawnEnemies()

    def loadSave(self):
        path = os.path.join("saves/", self.saveName)
        saveData = {}

        if not os.path.exists(path):
            print("The save file wasn't found!")
            return None
        
        with open(path, 'r') as f:
            data = json.load(f)

        # Charge grid tiles
        saveData['grid-tiles'] = {}
        for key, tile in data['tiles'].items():
            coords = key.split(',')
            coords[0], coords[1] = int(coords[0]), int(coords[1])

            saveData['grid-tiles'][tuple(coords)] = load(tile['sprite_surf'])

        # Charge off-grid tiles
        saveData['offgrid-tiles'] = []
        for element in data['off-grid']:
            position = element['position'].split(',')
            position[0], position[1] = float(position[0]), float(position[1])
            
            saveData['offgrid-tiles'].append({
                'surf': load(element['sprite_surf']).convert_alpha(),
                'position': position
            })

        # Charge physics shapes
        saveData['physics-shapes'] = []
        for pointCloud in data['physics']:
            tempPhysics = []
            for point in pointCloud:
                splittedPoint = point.split(',')
                tempPhysics.append((float(splittedPoint[0]), -float(splittedPoint[1])))
            saveData['physics-shapes'].append(tempPhysics)

        # Charge enemies
        saveData['enemies'] = []
        for enemy in data['enemies']:
            position = enemy['position'].split(',')
            position[0], position[1] = float(position[0]), -float(position[1])

            saveData['enemies'].append({
                'position': position,
                'type': enemy['type']
            })

        return saveData
    
    def createPolygons(self):
        for shape in self.data['physics-shapes']:
            self.BaseLevel.createPoly(shape)

    def spawnEnemies(self):
        self.app.EnemyHandler.Enemies.clear()
        for enemy in self.data['enemies']:
            config_0 = EnemyConfig()
            config_1= EnemyConfig(
                shooting=False,
                attackRange=0,
                sightDistance=700,
                moveSpeed=225
            )
            config_2 = EnemyConfig(
                attackRate=.6,
                bulletSpeed=700,
                bulletSize=35,
                attackRange=600,
                sightDistance=1300, moveSpeed=80, bounceSpeedGain=0.2
            )
            config_3 = EnemyConfig(
                attackRate=1.8,
                bulletSpeed=2000,
                bulletSize=10,
                attackRange=1000,
                sightDistance=1500,
                moveSpeed=300,
                bounceSpeedGain=0.9
            )
            configs = [config_0, config_1, config_2, config_3]
            self.app.EnemyHandler.Enemies.append(Enemy(self.app, self.app.convertCoordinates(enemy['position']), "res/img/"+self.enemy_types_images[enemy['type']], 64*3, configs[enemy['type']]))

    def render(self):
        if not self.BaseLevel: return

        for poly in self.BaseLevel.polygons:
            polyToDraw = []
            offscreenCount = 0
            for i in poly.get_vertices():
                pos = self.app.convertCoordinates(i)
                polyToDraw.append(pos)
                offscreenCount += not isOffScreen(self.app.screenSize, pos)
            if len(polyToDraw) != offscreenCount:
                draw.polygon(self.app.screen, self.color, polyToDraw)
            # else: print("offscreen")

    def update(self):
        if not self.BaseLevel: return
        self.BaseLevel.update()

        self.colorSwitchAlpha = clamp01(self.colorSwitchAlpha + self.app.deltaTime * (1/self.colorSwitchDuration))
        self.color = colorLerp(self.previousColor, self.targetColor, self.colorSwitchAlpha, LinearInOut)
        if time.time() - self.colorSwitchTime >= self.colorSwitchDuration + self.colorSwitchDelay:
            self.colorSwitchTime = time.time()
            self.colorSwitchAlpha = 0
            self.previousColor = self.targetColor
            self.targetColor = self.generate_random_color()

    def generate_random_color(self):
        return Color(randint(100,255),randint(100,255),randint(100,255), 255)