from PhysicsObject import PhysicsObject

from pymunk import Vec2d, Circle, Body, Arbiter, ShapeFilter

import pygame
from pygame.image import load
import pygame.draw as draw
import pygame.transform as transform
import pygame.display as display

import time, math, random

from constants import *
from Helpers import lerp, clamp01, reflect
from easing_functions import *

class Bullet(PhysicsObject):
    def __init__(self, app, position:tuple, size:int, dir:Vec2d, speed:float, accelerationSpeed:float, maxBounces:int=1, maxLifeTime=MAX_BULLET_LIFETIME):
        super().__init__(app)
        # self.body.body_type=Body.STATIC
        self.displaySurf = display.get_surface()
        self.sprite = transform.scale(load('res/img/bullet.png'), (size,size))
        self.body.position = position
        self.direction = dir
        self.speed = speed
        self.lifetime = 0
        self.maxLifeTime = maxLifeTime
        self.acceleration = 0
        self.maxBounces = maxBounces
        self.bounces = 0
        self.accelerationSpeed = accelerationSpeed
        self.accelerationEase = BackEaseIn

        self.boundingBox = Circle(self.body, size)
        self.boundingBox.collision_type = COLLTYPE_BULLET
        app.space.add(self.body, self.boundingBox)

        self.playerCollisionHandler = app.space.add_collision_handler(COLLTYPE_PLAYER, COLLTYPE_BULLET)
        self.playerCollisionHandler.begin = self.playerCollisionBegin

        self.envCollisionHandler = app.space.add_collision_handler(COLLTYPE_ENV, COLLTYPE_BULLET)
        self.envCollisionHandler.pre_solve = self.envCollisionBegin

    def update(self):
        self.acceleration = clamp01(self.acceleration + self.app.deltaTime * self.accelerationSpeed)
        self.body.velocity = self.direction * lerp(self.speed * 0.4, self.speed, self.acceleration, self.accelerationEase)
        self.body.angular_velocity = 0
        self.lifetime += self.app.deltaTime

        super().update()

    def render(self):
        super().render()
        bound = self.sprite.get_rect(center=self.app.convertCoordinates(self.body.position))
        self.displaySurf.blit(self.sprite, bound)

    def isOver(self):
        return self.lifetime >= self.maxLifeTime

    def playerCollisionBegin(self, arbiter, space, data) -> bool:
        self.app.Player.stun(.25)
        self.lifetime = self.maxLifeTime
        return True

    def envCollisionBegin(self, arbiter:Arbiter, space, data) ->bool:
        if self.bounces >= self.maxBounces:
            self.lifetime = self.maxLifeTime
        else:
            self.bounces += 1
            reflectedOut = reflect(self.direction, arbiter.normal)
            self.direction = reflectedOut
        return False

class EnemyConfig:
    def __init__(self, shooting:bool=True, attackRate:float=0.4, bulletSpeed:float=800, bulletSize:float=25, attackRange:float=700, sightDistance:float=900, moveSpeed:float=100):
        self.shooting = shooting
        self.attackRate = attackRate
        self.bulletSpeed = bulletSpeed
        self.bulletSize = bulletSize
        self.attackRange = attackRange
        self.sightDistance = sightDistance
        self.moveSpeed = moveSpeed

class Enemy(PhysicsObject):
    def __init__(self, app, position:tuple, sprite_path:str, size:int, config:EnemyConfig)->None:
        super().__init__(app)
        self.displaySurf = display.get_surface()
        self.sprite = transform.scale(load(sprite_path), (size,size))
        self.body.position = position
        self.size = size
        self.mask = ShapeFilter(mask=ShapeFilter.ALL_MASKS()^ENEMY_CATEGORY)
        self.dead = False

        # Physics:
        self.boundingBox = Circle(self.body, size/2)
        self.boundingBox.collision_type = COLLTYPE_ENEMY
        self.app.space.add(self.body, self.boundingBox)

        self.enemyCollisionHandler = app.space.add_collision_handler(COLLTYPE_PLAYER, COLLTYPE_ENEMY)

        # Behaviour:
        self.config = config
        self.lastAttackTime = time.time() - (1 / self.config.attackRate)

    def update(self)->None:
        self.body.velocity = Vec2d(0,0)
        self.body.angular_velocity = 0

        distanceToPlayer = (self.app.Player.body.position - self.body.position).length
        if (distanceToPlayer <= self.config.attackRange):
            elapsed = time.time() - self.lastAttackTime
            if (elapsed >= self.getAttackCooldown()):
                plrRay = self.app.space.segment_query_first(self.body.position, self.app.Player.body.position, self.config.bulletSize, self.app.Player.mask)
                enemyRay = self.app.space.segment_query_first(self.body.position, self.app.Player.body.position, self.config.bulletSize, self.mask)
                if plrRay and not enemyRay:
                    self.perform()
        elif (distanceToPlayer <= self.config.sightDistance):
            plrRay = self.app.space.segment_query_first(self.body.position, self.app.Player.body.position, self.size, self.app.Player.mask)
            if plrRay:
                self.move()
        super().update()

    def render(self)->None:
        bound = self.sprite.get_rect(center=self.app.convertCoordinates(self.body.position))
        self.displaySurf.blit(self.sprite, bound)
        super().render()

    def move(self)->None:
        dir = (self.app.Player.body.position - self.body.position).normalized()
        self.body.velocity = dir * self.config.moveSpeed

    def perform(self)->None:
        offset = Vec2d(0, 175/2)
        dir = (self.app.Player.body.position + offset - self.body.position).normalized()
        bullet = Bullet(self.app, self.body.position, self.bulletSize, dir, self.bulletSpeed, 1.6, random.randint(1, 8))
        self.app.EnemyHandler.Bullets.append(bullet)

    def getAttackCooldown(self)->float:
        return 1 / self.config.attackRate

# class Enemy(PhysicsObject):
#     def __init__(self, app, position:tuple, size:int, config:EnemyConfig):
#         super().__init__(app)
#         self.displaySurf = display.get_surface()
#         self.sprite = transform.scale(load('res/img/mouche.png'), (size,size))
#         self.dead = False

#         self.boundingBox = Circle(self.body, size/2)
#         self.boundingBox.collision_type = COLLTYPE_ENEMY
#         self.app.space.add(self.body, self.boundingBox)
#         self.enemyCollisionHandler = app.space.add_collision_handler(COLLTYPE_PLAYER, COLLTYPE_ENEMY)

#         # Shooting
#         self.config = config

#     def getAttackCooldown(self)->None:
#         return 1 / self.attackRate

#     def update(self)->None:
#         self.body.velocity = Vec2d(0,0)
#         self.body.angular_velocity = 0

#         distanceToPlayer = (self.app.Player.body.position - self.body.position).length
#         if (time.time() - self.lastAttackTime) >= self.getAttackCooldown() and distanceToPlayer <= self.attackRange:
#             self.lastAttackTime = time.time()
#             self.shoot()

#         super().update()

#     def render(self)->None:
#         super().render()
#         bound = self.sprite.get_rect(center=self.app.convertCoordinates(self.body.position))
#         self.displaySurf.blit(self.sprite, bound)

#     def shoot(self):
#         offset = Vec2d(0, 175/2)
#         dir = (self.app.Player.body.position + offset - self.body.position).normalized()
#         bullet = Bullet(self.app, self.body.position, self.bulletSize, dir, self.bulletSpeed, 1.6, random.randint(1, 8))
#         self.app.EnemyHandler.Bullets.append(bullet)

class EnemyHandler:
    def __init__(self, app):
        self.app = app
        self.Enemies = []
        self.Bullets = []

    def update(self):
        for enemy in self.Enemies:
            enemy.update()
            if enemy.dead:
                self.Enemies.remove(enemy)

        for bullet in self.Bullets:
            bullet.update()
            if bullet.isOver():
                self.Bullets.remove(bullet)
                self.app.space.remove(bullet.body, bullet.boundingBox)

    def render(self):
        for enemy in self.Enemies:
            enemy.render()

        for bullet in self.Bullets:
            bullet.render()

    def instantiateEnemy(self, position:tuple, size:int):
        config = EnemyConfig()
        self.Enemies.append(Enemy(self.app, position, 'res/img/mouche.png', 64, config))