import pygame
import math

pygame.init()

WIDTH = 800
HEIGHT = 600


class Enemy:
    def init(self):
        self.x = 0
        self.y = 300
        self.speed = 2

    def move(self):
        self.x += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 15)

    def run(self):
        while self.running:
            self.screen.fill((30, 30, 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.enemy.move()
                self.tower.update(self.enemy, self.bullets)

                for bullet in self.bullets:
                    bullet.move()

                self.enemy.draw(self.screen)
                self.tower.draw(self.screen)

                for bullet in self.bullets:
                    bullet.draw(self.screen)

                pygame.display.flip()

                self.clock.tick(60)
class Bullet:
    def init(self, x, y, tx, ty):
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty
        self.speed = 5

    def move(self):
        dx = self.tx - self.x
        dy = self.ty - self.y
        dist = math.hypot(dx, dy)

        if dist != 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)


class Tower:
    def init(self):
        self.x = 400
        self.y = 300
        self.cooldown = 0

    def update(self, enemy, bullets):
        self.cooldown += 1

class Game:
    def __init__(self):
        print("gamu HAs started")

game = Game()