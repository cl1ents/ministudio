from PhysicsObject import PhysicsObject

from pymunk import Vec2d, Circle, Body

import pygame
from pygame.image import load
import pygame.draw as draw
import pygame.transform as transform
import pygame.display as display

import time, math

from constants import *
from Helpers import lerp, clamp01
from easing_functions import *

class Bullet(PhysicsObject):
    def __init__(self, app, position:tuple, size:int, dir:Vec2d, speed:float, accelerationSpeed:float, maxLifeTime=MAX_BULLET_LIFETIME):
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
        self.accelerationSpeed = accelerationSpeed
        self.accelerationEase = BackEaseIn

        self.boudingBox = Circle(self.body, size/2)
        self.boudingBox.collision_type = COLLTYPE_BULLET
        self.app.space.add(self.body, self.boudingBox)

        self.bulletCollisionHandler = app.space.add_collision_handler(COLLTYPE_PLAYER, COLLTYPE_BULLET)
        self.bulletCollisionHandler.begin = self.playerCollisionBegin

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

class Enemy(PhysicsObject):
    def __init__(self, app, position:tuple, size:int):
        super().__init__(app)
        self.displaySurf = display.get_surface()
        self.sprite = transform.scale(load('res/img/mouche.png'), (size,size))

        self.boundingBox = Circle(self.body, size/2)
        self.boundingBox.collision_type = COLLTYPE_ENEMY
        self.app.space.add(self.body, self.boundingBox)

        self.enemyCollisionHandler = app.space.add_collision_handler(COLLTYPE_PLAYER, COLLTYPE_ENEMY)

        self.body.position = position

        # Shooting
        self.bullets = []
        self.attackRate = 0.2
        self.lastAttackTime = time.time() - self.getAttackCooldown()
        self.bulletSpeed = 800
        self.bulletSize = 25

    def getAttackCooldown(self)->None:
        return 1 / self.attackRate

    def update(self)->None:
        self.body.velocity = Vec2d(0,0)
        self.body.angular_velocity = 0

        if (time.time() - self.lastAttackTime) >= self.getAttackCooldown():
            self.lastAttackTime = time.time()
            self.shoot()

        for bullet in self.bullets:
            bullet.update()
            if bullet.isOver():
                self.bullets.remove(bullet)
                self.app.space.remove(bullet.body, bullet.boudingBox)

        super().update()

    def render(self)->None:
        super().render()
        bound = self.sprite.get_rect(center=self.app.convertCoordinates(self.body.position))
        self.displaySurf.blit(self.sprite, bound)

        for bullet in self.bullets:
            bullet.render()

    def shoot(self):
        offset = Vec2d(0, 175/2)
        dir = (self.app.Player.body.local_to_world((0, 175/2)) - self.body.position).normalized()
        bullet = Bullet(self.app, self.body.position, self.bulletSize, dir, self.bulletSpeed, 1.6)
        self.bullets.append(bullet)
        print("New bullet")
