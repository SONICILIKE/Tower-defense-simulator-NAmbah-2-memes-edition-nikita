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
pygame.display.set_caption("Tower Defense")

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

        self.max_hp = 100 + level * 60

        if boss:
            self.max_hp *= 5
            self.speed = 2.5

        if mega:
            self.max_hp *= 6
            self.speed = 1.7

        self.hp = self.max_hp

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

        # атакует первого врага
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
            (80, 80, 80),
            (self.x, self.y),
            self.range,
            1
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (self.x, self.y),
            24
        )

        pygame.draw.circle(
            screen,
            color,
            (self.x, self.y),
            20
        )

        lvl = font.render(
            str(self.level),
            True,
            WHITE
        )

        screen.blit(lvl, (self.x - 6, self.y - 10))

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

        self.message = ""

        self.shop_open = False

        self.wave_started = False

        self.damage_upgrade = 0
        self.hp_upgrade = 0
        self.range_upgrade = 0
        self.speed_upgrade = 0

    # =================================================

    def get_upgrade_cost(self, level):

        return (level + 1) * 100

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

        if self.is_on_path(x, y):
            self.message = "CANT BUILD ON PATH"
            return

        for tower in self.towers:

            if math.hypot(
                tower.x - x,
                tower.y - y
            ) < 50:

                self.message = "TOO CLOSE"
                return

        if self.money < TOWER_COST:
            self.message = "NO MONEY"
            return

        tower = Tower(x, y)

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

        normal_count = 4 + self.wave

        for i in range(normal_count):

            self.enemies.append(
                Enemy(level)
            )

        self.enemies.append(
            Enemy(level, boss=True)
        )

        if self.wave % 5 == 0:

            self.enemies.append(
                Enemy(level, mega=True)
            )

    # =================================================

    def start_wave(self):

        if len(self.enemies) == 0:

            self.wave += 1

            self.spawn_wave()

    # =================================================

    def skip_wave(self):

        self.enemies.clear()

    # =================================================

    def update(self):

        # auto next wave
        if len(self.enemies) == 0 and self.wave_started:

            self.start_wave()

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

                reward = 10

                if enemy.boss:
                    reward = 50

                if enemy.mega:
                    reward = 100

                self.money += reward

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
            (900, 120, 280, 300)
        )

        dmg_cost = self.get_upgrade_cost(self.damage_upgrade)
        hp_cost = self.get_upgrade_cost(self.hp_upgrade)
        range_cost = self.get_upgrade_cost(self.range_upgrade)
        speed_cost = self.get_upgrade_cost(self.speed_upgrade)

        texts = [

            f"1 DAMAGE LVL {self.damage_upgrade}",
            f"COST {dmg_cost}",

            "",

            f"2 HP LVL {self.hp_upgrade}",
            f"COST {hp_cost}",

            "",

            f"3 RANGE LVL {self.range_upgrade}",
            f"COST {range_cost}",

            "",

            f"4 SPEED LVL {self.speed_upgrade}",
            f"COST {speed_cost}",
        ]

        y = 140

        for t in texts:

            txt = font.render(
                t,
                True,
                WHITE
            )

            screen.blit(txt, (920, y))

            y += 25

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

        # START BUTTON
        pygame.draw.rect(
            screen,
            GREEN,
            (900, 10, 120, 40)
        )

        txt = font.render(
            "START",
            True,
            BLACK
        )

        screen.blit(txt, (930, 18))

        # SKIP BUTTON
        pygame.draw.rect(
            screen,
            ORANGE,
            (900, 60, 120, 40)
        )

        txt2 = font.render(
            "SKIP",
            True,
            BLACK
        )

        screen.blit(txt2, (940, 68))

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

        # TOWER INFO
        mx, my = pygame.mouse.get_pos()

        for tower in self.towers:

            dist = math.hypot(
                tower.x - mx,
                tower.y - my
            )

            if dist < 30:

                upgrade_cost = tower.level * 100

                info = [
                    f"LEVEL: {tower.level}",
                    f"DAMAGE: {tower.damage}",
                    f"RANGE: {tower.range}",
                    f"UPGRADE: {upgrade_cost}$",
                    "PRESS U"
                ]

                y = 150

                for i in info:

                    txt = font.render(
                        i,
                        True,
                        WHITE
                    )

                    screen.blit(txt, (10, y))

                    y += 25

        if self.shop_open:
            self.draw_shop()

    # =================================================

    def run(self):

        while self.running:

            clock.tick(FPS)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                # MOUSE
                if event.type == pygame.MOUSEBUTTONDOWN:

                    mx, my = pygame.mouse.get_pos()

                    # START
                    if 900 <= mx <= 1020 and 10 <= my <= 50:

                        self.wave_started = True
                        self.start_wave()

                    # SKIP
                    elif 900 <= mx <= 1020 and 60 <= my <= 100:

                        self.skip_wave()

                    # SHOP
                    elif 1040 <= mx <= 1160 and 10 <= my <= 50:

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

                                cost = tower.level * 100

                                if self.money >= cost:

                                    tower.upgrade()

                                    self.money -= cost

                    # shop upgrades
                    if self.shop_open:

                        upgrades = [
                            ("damage_upgrade", pygame.K_1),
                            ("hp_upgrade", pygame.K_2),
                            ("range_upgrade", pygame.K_3),
                            ("speed_upgrade", pygame.K_4)
                        ]

                        for attr, key in upgrades:

                            if event.key == key:

                                lvl = getattr(self, attr)

                                cost = self.get_upgrade_cost(lvl)

                                if self.money >= cost:

                                    setattr(
                                        self,
                                        attr,
                                        lvl + 1
                                    )

                                    self.money -= cost

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