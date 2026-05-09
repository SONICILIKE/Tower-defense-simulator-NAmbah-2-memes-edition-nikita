import pygame
import math
import random

pygame.init()

# =====================================================
# WINDOW
# =====================================================

WIDTH = 1200
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Memes Edition")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)

# =====================================================
# COLORS
# =====================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GRAY = (70, 70, 70)

GREEN = (0, 255, 0)
RED = (255, 0, 0)

BLUE = (50, 100, 255)

YELLOW = (255, 255, 0)

ORANGE = (255, 120, 0)

PURPLE = (180, 0, 255)

BROWN = (140, 90, 40)

# =====================================================
# SETTINGS
# =====================================================

START_MONEY = 700

TOWER_COST = 150

PATH = [
    (0, 350),
    (250, 350),
    (250, 150),
    (600, 150),
    (600, 500),
    (1000, 500),
    (1200, 500)
]

LEVEL_COLORS = [
    (120, 120, 120),
    (0, 255, 0),
    (0, 200, 255),
    (255, 255, 0),
    (255, 150, 0),
    (255, 0, 0),
    (255, 0, 255),
    (120, 0, 255),
    (255, 255, 255),
    (0, 0, 0)
]

# =====================================================
# ENEMY
# =====================================================

class Enemy:

    def __init__(self, level=1, boss=False, mega=False):

        self.x = PATH[0][0] - random.randint(0, 300)
        self.y = PATH[0][1]

        self.path_index = 1

        self.level = level

        self.boss = boss
        self.mega = mega

        self.speed = 2

        # HP
        self.max_hp = 100 + level * 60

        if boss:
            self.max_hp *= 5
            self.speed = 2.5

        if mega:
            self.max_hp *= 6
            self.speed = 1.7

        self.hp = self.max_hp

        # SIZE
        self.radius = 15

        if boss:
            self.radius = 28

        if mega:
            self.radius = 45

        self.dead = False

    # =================================================

    def move(self):

        if self.path_index >= len(PATH):
            self.dead = True
            return

        target_x, target_y = PATH[self.path_index]

        dx = target_x - self.x
        dy = target_y - self.y

        dist = math.hypot(dx, dy)

        if dist <= self.speed:

            self.x = target_x
            self.y = target_y

            self.path_index += 1
            return

        if dist != 0:

            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    # =================================================

    def draw(self):

        color = LEVEL_COLORS[min(self.level - 1, 9)]

        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            self.radius
        )

        # HP BAR
        bar_width = self.radius * 2

        pygame.draw.rect(
            screen,
            RED,
            (
                self.x - self.radius,
                self.y - self.radius - 15,
                bar_width,
                6
            )
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x - self.radius,
                self.y - self.radius - 15,
                bar_width * (self.hp / self.max_hp),
                6
            )
        )

# =====================================================
# BULLET
# =====================================================

class Bullet:

    def __init__(self, x, y, enemy, damage):

        self.x = x
        self.y = y

        self.enemy = enemy

        self.speed = 9

        self.damage = damage

        self.dead = False

    # =================================================

    def move(self):

        if self.enemy.dead:
            self.dead = True
            return

        dx = self.enemy.x - self.x
        dy = self.enemy.y - self.y

        dist = math.hypot(dx, dy)

        if dist < 10:

            self.enemy.hp -= self.damage

            if self.enemy.hp <= 0:
                self.enemy.dead = True

            self.dead = True
            return

        if dist != 0:

            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    # =================================================

    def draw(self):

        pygame.draw.circle(
            screen,
            YELLOW,
            (int(self.x), int(self.y)),
            6
        )

        # BULLET RADIUS
        pygame.draw.circle(
            screen,
            ORANGE,
            (int(self.x), int(self.y)),
            12,
            1
        )

# =====================================================
# TOWER
# =====================================================

class Tower:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.level = 1

        self.max_hp = 100
        self.hp = self.max_hp

        self.range = 200

        self.damage = 60

        self.fire_rate = 35

        self.cooldown = 0

    # =================================================

    def upgrade(self):

        if self.level < 10:

            self.level += 1

            self.max_hp += 20
            self.hp = self.max_hp

            self.damage += 15

            self.range += 15

            if self.fire_rate > 10:
                self.fire_rate -= 2

    # =================================================

    def update(self, enemies, bullets):

        self.cooldown += 1

        target = None

        for enemy in enemies:

            if enemy.dead:
                continue

            dist = math.hypot(
                enemy.x - self.x,
                enemy.y - self.y
            )

            if dist <= self.range:
                target = enemy
                break

        if target and self.cooldown >= self.fire_rate:

            bullets.append(
                Bullet(
                    self.x,
                    self.y,
                    target,
                    self.damage
                )
            )

            self.cooldown = 0

    # =================================================

    def draw(self):

        color = LEVEL_COLORS[min(self.level - 1, 9)]

        pygame.draw.circle(
            screen,
            color,
            (self.x, self.y),
            20
        )

        # HP BAR
        pygame.draw.rect(
            screen,
            RED,
            (self.x - 20, self.y - 35, 40, 5)
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x - 20,
                self.y - 35,
                40 * (self.hp / self.max_hp),
                5
            )
        )

# =====================================================
# GAME
# =====================================================

class Game:

    def __init__(self):

        self.running = True

        self.enemies = []
        self.bullets = []
        self.towers = []

        self.money = START_MONEY

        self.wave = 0

        self.spawn_timer = 0

        self.message = ""

        self.shop_open = False

        # GLOBAL UPGRADES
        self.damage_upgrade = 0
        self.hp_upgrade = 0
        self.range_upgrade = 0
        self.speed_upgrade = 0

        self.boss_kills = 0

    # =================================================

    def draw_path(self):

        pygame.draw.lines(
            screen,
            BROWN,
            False,
            PATH,
            40
        )

    # =================================================

    def is_on_path(self, x, y):

        for px, py in PATH:

            if math.hypot(px - x, py - y) < 60:
                return True

        return False

    # =================================================

    def place_tower(self, x, y):

        # нельзя строить на дороге
        if self.is_on_path(x, y):
            self.message = "CANT BUILD ON PATH"
            return

        # нельзя рядом с башнями
        for tower in self.towers:

            if math.hypot(
                tower.x - x,
                tower.y - y
            ) < 50:

                self.message = "TOO CLOSE"
                return

        # нет денег
        if self.money < TOWER_COST:
            self.message = "NO MONEY"
            return

        tower = Tower(x, y)

        # upgrades
        tower.damage += self.damage_upgrade * 20

        tower.max_hp += self.hp_upgrade * 30
        tower.hp = tower.max_hp

        tower.range += self.range_upgrade * 25

        if self.speed_upgrade > 0:
            tower.fire_rate -= self.speed_upgrade * 3

        self.towers.append(tower)

        self.money -= TOWER_COST

    # =================================================

    def spawn_wave(self):

        level = min(self.wave, 10)

        # NORMAL ENEMIES
        normal_count = 4 + self.wave

        for i in range(normal_count):

            self.enemies.append(
                Enemy(level)
            )

        # BOSS
        self.enemies.append(
            Enemy(level, boss=True)
        )

        # MEGA BOSS
        if self.wave % 5 == 0:

            self.enemies.append(
                Enemy(level, mega=True)
            )

    # =================================================

    def update(self):

        # новая волна только когда врагов нет
        if len(self.enemies) == 0:

            self.spawn_timer += 1

            if self.spawn_timer >= 180:

                self.wave += 1

                self.spawn_wave()

                self.spawn_timer = 0

        # enemies
        for enemy in self.enemies:
            enemy.move()

        # towers
        for tower in self.towers:

            tower.update(
                self.enemies,
                self.bullets
            )

        # bullets
        for bullet in self.bullets:
            bullet.move()

        # rewards
        for enemy in self.enemies:

            if enemy.dead:

                reward = 5

                if enemy.boss or enemy.mega:

                    self.boss_kills += 1

                    reward = min(
                        self.boss_kills * 5,
                        25
                    )

                self.money += reward

        # remove dead
        self.enemies = [
            e for e in self.enemies
            if not e.dead
        ]

        self.bullets = [
            b for b in self.bullets
            if not b.dead
        ]

    # =================================================

    def draw_shop(self):

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (900, 0, 300, 300)
        )

        texts = [
            f"1 DAMAGE {self.damage_upgrade}/5",
            f"2 HP {self.hp_upgrade}/5",
            f"3 RANGE {self.range_upgrade}/5",
            f"4 SPEED {self.speed_upgrade}/5",
            "",
            "PRESS 1-4"
        ]

        y = 40

        for t in texts:

            txt = font.render(
                t,
                True,
                WHITE
            )

            screen.blit(txt, (920, y))

            y += 40

    # =================================================

    def draw_ui(self):

        money = font.render(
            f"MONEY: {self.money}",
            True,
            WHITE
        )

        wave = font.render(
            f"WAVE: {self.wave}",
            True,
            WHITE
        )

        towers = font.render(
            f"TOWERS: {len(self.towers)}",
            True,
            WHITE
        )

        screen.blit(money, (10, 10))
        screen.blit(wave, (10, 40))
        screen.blit(towers, (10, 70))

        # SHOP BUTTON
        pygame.draw.rect(
            screen,
            BLUE,
            (1040, 10, 120, 40)
        )

        txt = font.render(
            "SHOP",
            True,
            WHITE
        )

        screen.blit(txt, (1070, 18))

        # MESSAGE
        msg = font.render(
            self.message,
            True,
            YELLOW
        )

        screen.blit(msg, (10, 110))

        if self.shop_open:
            self.draw_shop()

    # =================================================

    def run(self):

        while self.running:

            clock.tick(FPS)

            # EVENTS
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                # MOUSE
                if event.type == pygame.MOUSEBUTTONDOWN:

                    mx, my = pygame.mouse.get_pos()

                    # SHOP BUTTON
                    if 1040 <= mx <= 1160 and 10 <= my <= 50:

                        self.shop_open = not self.shop_open

                    else:

                        self.place_tower(mx, my)

                # KEYBOARD
                if event.type == pygame.KEYDOWN:

                    # tower upgrade
                    if event.key == pygame.K_u:

                        mx, my = pygame.mouse.get_pos()

                        for tower in self.towers:

                            dist = math.hypot(
                                tower.x - mx,
                                tower.y - my
                            )

                            if dist < 30:

                                if self.money >= 100:

                                    tower.upgrade()

                                    self.money -= 100

                    # SHOP UPGRADES
                    if self.shop_open:

                        if event.key == pygame.K_1:

                            if self.damage_upgrade < 5:
                                self.damage_upgrade += 1

                        if event.key == pygame.K_2:

                            if self.hp_upgrade < 5:
                                self.hp_upgrade += 1

                        if event.key == pygame.K_3:

                            if self.range_upgrade < 5:
                                self.range_upgrade += 1

                        if event.key == pygame.K_4:

                            if self.speed_upgrade < 5:
                                self.speed_upgrade += 1

            # UPDATE
            self.update()

            # DRAW
            screen.fill(GRAY)

            self.draw_path()

            for enemy in self.enemies:
                enemy.draw()

            for tower in self.towers:
                tower.draw()

            for bullet in self.bullets:
                bullet.draw()

            self.draw_ui()

            pygame.display.flip()

# =====================================================
# START
# =====================================================

game = Game()
game.run()

pygame.quit()