from PhysicsObject import PhysicsObject

from pymunk import Vec2d, Circle, Body

import pygame
from pygame.image import load
import pygame.draw as draw
import pygame.transform as transform
import pygame.display as display

import time

class Bullet(PhysicsObject):
    def __init__(self, app, position:tuple, size:int, dir:Vec2d, speed:float):
        super().__init__(app)
        # self.body.body_type=Body.STATIC
        self.displaySurf = display.get_surface()
        self.sprite = transform.scale(load('res/img/bullet.png'), (size,size))
        self.body.position = position
        self.direction = dir
        self.speed = speed

        self.boudingBox = Circle(self.body, size/2)
        self.app.space.add(self.body, self.boudingBox)

    def update(self, dT):
        self.body.velocity = Vec2d(0,0)
        self.body.angular_velocity = 0

        self.body.position += self.direction * self.speed * dT
        super().update()

    def render(self):
        super().render()
        self.displaySurf.blit(self.sprite, self.app.convertCoordinates(self.body.position))

class Enemy(PhysicsObject):
    def __init__(self, app, player, position:tuple, size:int):
        super().__init__(app)
        self.displaySurf = display.get_surface()
        self.player = player
        self.sprite = transform.scale(load('res/img/mouche.png'), (size,size))

        self.boundingBox = Circle(self.body, size/2)
        self.app.space.add(self.body, self.boundingBox)

        self.body.position = position

        # Shooting
        self.bullets = []
        self.attackRate = 0.4
        self.lastAttackTime = time.time() - self.getAttackCooldown()
        self.bulletSpeed = 600
        self.bulletSize = 25

    def getAttackCooldown(self)->None:
        return 1 / self.attackRate

    def update(self, dt:float)->None:
        self.body.velocity = Vec2d(0,0)
        self.body.angular_velocity = 0

        if (time.time() - self.lastAttackTime) >= self.getAttackCooldown():
            self.lastAttackTime = time.time()
            self.shoot()

        for bullet in self.bullets:
            bullet.update(dt)

        super().update()

    def render(self)->None:
        super().render()
        self.displaySurf.blit(self.sprite, self.app.convertCoordinates(self.body.position))

        for bullet in self.bullets:
            bullet.render()

    def shoot(self):
        dir = (self.player.body.position - self.body.position).normalized()
        bullet = Bullet(self.app, self.body.position, self.bulletSize, dir, self.bulletSpeed)
        self.bullets.append(bullet)
        print("New bullet")
