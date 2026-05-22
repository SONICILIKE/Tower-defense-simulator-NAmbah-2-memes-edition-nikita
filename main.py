import pygame
import math
import random

pygame.init()
pygame.mixer.init()

# =====================================================
# WINDOW & SETTINGS
# =====================================================
WIDTH, HEIGHT, FPS = 1200, 700, 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22)

START_MONEY = 700
TOWER_COST = 150

PATH = [(0, 350), (250, 350), (250, 150), (600, 150), (600, 500), (1000, 500), (1200, 500)]

LEVEL_COLORS = [
    (120, 120, 120), (0, 255, 0), (0, 200, 255), (255, 255, 0), (255, 150, 0),
    (255, 0, 0), (255, 0, 255), (120, 0, 255), (255, 255, 255), (0, 0, 0)
]

WHITE, BLACK, GRAY, GREEN, RED, BLUE, YELLOW, ORANGE, BROWN = \
    (255, 255, 255), (0, 0, 0), (70, 70, 70), (0, 255, 0), (255, 0, 0), \
        (50, 100, 255), (255, 255, 0), (255, 120, 0), (140, 90, 40)

# =====================================================
# IMAGES BLOCK
# =====================================================
IMG_TOWER = pygame.transform.scale(pygame.image.load("imagus/67.jfif").convert_alpha(), (48, 48))
IMG_BULLET = pygame.transform.scale(pygame.image.load("imagus/67.jfif").convert_alpha(), (24, 24))

IMG_ENEMIES = {
    "normal": pygame.transform.scale(pygame.image.load("imagus/67.jfif").convert_alpha(), (30, 30)),
    "boss": pygame.transform.scale(pygame.image.load("imagus/67.jfif").convert_alpha(), (56, 56)),
    "mega": pygame.transform.scale(pygame.image.load("imagus/67.jfif").convert_alpha(), (90, 90))
}

# =====================================================
# AUDIO BLOCK
# =====================================================
MUSIC_MENU = "sounds/thaxted-holst.mp3"
MUSIC_BATTLE = "sounds/HEROICCC.mp3"
current_music_state = None  # Стежить за треком: "menu", "battle" або None


# =====================================================
# CLASSES
# =====================================================

class Enemy:
    def __init__(self, level=1, boss=False, mega=False):
        self.x = PATH[0][0] - random.randint(0, 300)
        self.y = PATH[0][1]
        self.path_index = 1
        self.level = level
        self.boss, self.mega = boss, mega
        self.dead = False

        self.speed = 2.5 if boss else (1.7 if mega else 2)
        self.radius = 28 if boss else (45 if mega else 15)

        self.type = "mega" if mega else ("boss" if boss else "normal")
        self.image = IMG_ENEMIES[self.type]

        self.max_hp = 100 + level * 60
        if boss: self.max_hp *= 5
        if mega: self.max_hp *= 6
        self.hp = self.max_hp

    def move(self):
        if self.path_index >= len(PATH):
            self.dead = True
            return

        target_x, target_y = PATH[self.path_index]
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.speed:
            self.x, self.y = target_x, target_y
            self.path_index += 1
        elif dist != 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect.topleft)

        color = LEVEL_COLORS[min(self.level - 1, 9)]
        pygame.draw.circle(screen, color, (int(self.x), int(self.y - self.radius)), 5)

        # HP BAR
        bar_w = self.radius * 2
        bx, by = self.x - self.radius, self.y - self.radius - 15
        pygame.draw.rect(screen, RED, (bx, by, bar_w, 6))
        pygame.draw.rect(screen, GREEN, (bx, by, bar_w * (self.hp / self.max_hp), 6))


class Bullet:
    def __init__(self, x, y, enemy, damage):
        self.x, self.y = x, y
        self.enemy = enemy
        self.speed = 9
        self.damage = damage
        self.dead = False
        self.image = IMG_BULLET

    def move(self):
        if self.enemy.dead:
            self.dead = True
            return

        dx, dy = self.enemy.x - self.x, self.enemy.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 10:
            self.enemy.hp -= self.damage
            if self.enemy.hp <= 0:
                self.enemy.dead = True
            self.dead = True
        elif dist != 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect.topleft)


class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.level = 1
        self.max_hp = 100
        self.hp = self.max_hp
        self.range = 200
        self.damage = 60
        self.fire_rate = 35
        self.cooldown = 0
        self.image = IMG_TOWER

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.max_hp += 20
            self.hp = self.max_hp
            self.damage += 15
            self.range += 15
            if self.fire_rate > 10:
                self.fire_rate -= 2

    def update(self, enemies, bullets):
        self.cooldown += 1
        target = None

        for enemy in enemies:
            if not enemy.dead and math.hypot(enemy.x - self.x, enemy.y - self.y) <= self.range:
                target = enemy
                break

        if target and self.cooldown >= self.fire_rate:
            bullets.append(Bullet(self.x, self.y, target, self.damage))
            self.cooldown = 0

    def draw(self):
        pygame.draw.circle(screen, (80, 80, 80), (self.x, self.y), self.range, 1)

        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect.topleft)

        color = LEVEL_COLORS[min(self.level - 1, 9)]
        pygame.draw.circle(screen, color, (self.x, self.y - 1), 12, 2)

        lvl = font.render(str(self.level), True, WHITE)
        screen.blit(lvl, (self.x - 5, self.y - 13))

        # HP BAR
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 35, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 35, 40 * (self.hp / self.max_hp), 5))


class Game:
    def __init__(self):
        self.running = True
        self.enemies, self.bullets, self.towers = [], [], []
        self.money = START_MONEY
        self.wave = 0
        self.message = ""
        self.shop_open = False
        self.wave_started = False
        self.damage_upgrade = self.hp_upgrade = self.range_upgrade = self.speed_upgrade = 0

        self.update_music()  # Запускаємо спокійну музику меню відразу при створенні гри


    def get_upgrade_cost(self, level):
        return (level + 1) * 100

    def draw_path(self):
        pygame.draw.lines(screen, BROWN, False, PATH, 40)

    def is_on_path(self, x, y):
        # Ширина вашої дороги 40 пікселів, тому безпечний радіус відступу від центру — близько 35-40
        road_radius = 35

        # Перебираємо всі пари точок (відрізки дороги)
        for i in range(len(PATH) - 1):
            p1 = PATH[i]
            p2 = PATH[i + 1]

            # Вектори відрізка дороги та кліку миші
            line_vec_x = p2[0] - p1[0]
            line_vec_y = p2[1] - p1[1]
            p1_to_mouse_x = x - p1[0]
            p1_to_mouse_y = y - p1[1]

            # Довжина відрізка у квадраті
            line_len_sq = line_vec_x ** 2 + line_vec_y ** 2
            if line_len_sq == 0:
                continue

            # Проєкція точки кліку на відрізок ліній (обмежуємо від 0 до 1)
            t = (p1_to_mouse_x * line_vec_x + p1_to_mouse_y * line_vec_y) / line_len_sq
            t = max(0, min(1, t))

            # Знаходимо найближчу точку на дорозі до нашого кліку
            closest_x = p1[0] + t * line_vec_x
            closest_y = p1[1] + t * line_vec_y

            # Рахуємо реальну відстань від мишки до дороги
            distance = math.hypot(x - closest_x, y - closest_y)

            if distance < road_radius:
                return True  # Клікнули на дорогу або занадто близько до неї

        return False

    def place_tower(self, x, y):
        # ПЕРЕВІРКА 1: Чи не ставимо ми вежу на дорогу
        if self.is_on_path(x, y):
            self.message = "CANT BUILD ON PATH"
            return

        # ПЕРЕВІРКА 2: Чи не занадто близько до інших веж
        if any(math.hypot(t.x - x, t.y - y) < 50 for t in self.towers):
            self.message = "TOO CLOSE"
            return

        # ПЕРЕВІРКА 3: Гроші
        if self.money < TOWER_COST:
            self.message = "NO MONEY"
            return

        # Якщо все добре — будуємо!
        tower = Tower(x, y)
        tower.damage += self.damage_upgrade * 20
        tower.max_hp += self.hp_upgrade * 30
        tower.hp = tower.max_hp
        tower.range += self.range_upgrade * 25
        if self.speed_upgrade > 0:
            tower.fire_rate -= self.speed_upgrade * 3

        self.towers.append(tower)
        self.money -= TOWER_COST
        self.message = ""  # Очищуємо помилки при успіху

    def spawn_wave(self):
        level = min(self.wave, 10)
        for _ in range(4 + self.wave):
            self.enemies.append(Enemy(level))
        self.enemies.append(Enemy(level, boss=True))
        if self.wave % 5 == 0:
            self.enemies.append(Enemy(level, mega=True))

    def start_wave(self):
        if not self.enemies:
            self.wave += 1
            self.spawn_wave()

    def skip_wave(self):
        self.enemies.clear()

    def update_music(self):
        # Якщо хвиля ще ВЗАГАЛІ жодного разу не запускалася — грає меню
        if not self.wave_started:
            pygame.mixer.music.load(MUSIC_MENU)
            pygame.mixer.music.play(-1)
        else:
            # Якщо гру запустили — вмикаємо бойовий трек назавжди
            pygame.mixer.music.fadeout(1000)
            pygame.mixer.music.load(MUSIC_BATTLE)
            pygame.mixer.music.play(-1)

    def update(self):
        if not self.enemies and self.wave_started:
            self.start_wave()

        for enemy in self.enemies: enemy.move()
        for tower in self.towers: tower.update(self.enemies, self.bullets)
        for bullet in self.bullets: bullet.move()

        for enemy in self.enemies:
            if enemy.dead:
                self.money += 100 if enemy.mega else (50 if enemy.boss else 10)

        self.enemies = [e for e in self.enemies if not e.dead]
        self.bullets = [b for b in self.bullets if not b.dead]

    def draw_shop(self):
        pygame.draw.rect(screen, (30, 30, 30), (900, 120, 280, 300))
        upgrades = [
            ("DAMAGE", self.damage_upgrade),
            ("HP", self.hp_upgrade),
            ("RANGE", self.range_upgrade),
            ("SPEED", self.speed_upgrade)
        ]

        y = 140
        for i, (name, lvl) in enumerate(upgrades, 1):
            t1 = font.render(f"{i} {name} LVL {lvl}", True, WHITE)
            t2 = font.render(f"COST {self.get_upgrade_cost(lvl)}", True, WHITE)
            screen.blit(t1, (920, y))
            screen.blit(t2, (920, y + 25))
            y += 75

    def draw_ui(self):
        stats = [f"MONEY: {self.money}", f"WAVE: {self.wave}", f"TOWERS: {len(self.towers)}"]
        for idx, text in enumerate(stats):
            screen.blit(font.render(text, True, WHITE), (10, 10 + idx * 30))

        buttons = [(GREEN, "START", 10, BLACK), (ORANGE, "SKIP", 60, BLACK), (BLUE, "SHOP", 10, WHITE)]
        for color, name, y_pos, text_color in buttons:
            x_pos = 1040 if name == "SHOP" else 900
            pygame.draw.rect(screen, color, (x_pos, y_pos, 120, 40))
            txt = font.render(name, True, text_color)
            screen.blit(txt, (x_pos + 30, y_pos + 8))

        screen.blit(font.render(self.message, True, YELLOW), (10, 110))

        mx, my = pygame.mouse.get_pos()
        for tower in self.towers:
            if math.hypot(tower.x - mx, tower.y - my) < 30:
                info = [
                    f"LEVEL: {tower.level}", f"DAMAGE: {tower.damage}",
                    f"RANGE: {tower.range}", f"UPGRADE: {tower.level * 100}$", "PRESS U"
                ]
                for idx, text in enumerate(info):
                    screen.blit(font.render(text, True, WHITE), (10, 150 + idx * 25))

        if self.shop_open:
            self.draw_shop()

    def run(self):
        while self.running:
            clock.tick(FPS)
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 900 <= mx <= 1020 and 10 <= my <= 50:
                        # Якщо це перший запуск хвилі — міняємо музику на бойову
                        if not self.wave_started:
                            self.wave_started = True
                            self.update_music()  # Перемкне на MUSIC_BATTLE один раз і назавжди
                        self.start_wave()
                    elif 900 <= mx <= 1020 and 60 <= my <= 100:
                        self.skip_wave()
                    elif 1040 <= mx <= 1160 and 10 <= my <= 50:
                        self.shop_open = not self.shop_open
                    else:
                        self.place_tower(mx, my)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        for tower in self.towers:
                            if math.hypot(tower.x - mx, tower.y - my) < 30:
                                cost = tower.level * 100
                                if self.money >= cost:
                                    tower.upgrade()
                                    self.money -= cost

                    if self.shop_open:
                        shop_keys = [
                            ("damage_upgrade", pygame.K_1), ("hp_upgrade", pygame.K_2),
                            ("range_upgrade", pygame.K_3), ("speed_upgrade", pygame.K_4)
                        ]
                        for attr, key in shop_keys:
                            if event.key == key:
                                lvl = getattr(self, attr)
                                cost = self.get_upgrade_cost(lvl)
                                if self.money >= cost:
                                    setattr(self, attr, lvl + 1)
                                    self.money -= cost

            self.update()
            screen.fill(GRAY)
            self.draw_path()

            for obj in self.enemies + self.towers + self.bullets:
                obj.draw()

            self.draw_ui()
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()