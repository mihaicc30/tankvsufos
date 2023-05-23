import pygame
import sys
import random
import time
from random import randint, choice

# pygame init
pygame.init()
WIDTH, HEIGHT = 800, 1000  # resolution
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tank vs UFOs')
clock = pygame.time.Clock()

# vehicle imgs
# tank 1 animation
tank1 = pygame.image.load('img/tank1.png').convert_alpha()
tank2 = pygame.image.load('img/tank2.png').convert_alpha()
tank3 = pygame.image.load('img/tank3.png').convert_alpha()
tank4 = pygame.image.load('img/tank4.png').convert_alpha()
tank = pygame.transform.scale(tank1, (120, 120)).convert_alpha()

ufo = pygame.image.load('img/ufo.png').convert_alpha()
ufo = pygame.transform.scale(ufo, (60, 30)).convert_alpha()
# bullet imgs
x_bullet = pygame.image.load('img/bullet.png').convert_alpha()
x_laser = pygame.image.load('img/pixel_laser_red.png').convert_alpha()

# background img & others
mainmenu = pygame.image.load('img/mainmenu.jpg').convert_alpha()
background = pygame.image.load('img/background.jpg').convert_alpha()
background = pygame.transform.scale(background, (WIDTH, 1000))
# ground = pygame.image.load('img/ground.jpg').convert_alpha()
# ground = pygame.transform.scale(ground, (WIDTH, 500))
# font
font = pygame.font.Font("font/shadowcard_gothic.TTF", 30)  # can specify file instead of None (eg: file.ttf )
font2 = pygame.font.Font("font/shadowcard_gothic.TTF", 50)

# timer
score_timer = pygame.USEREVENT + 1
pygame.time.set_timer(score_timer, 2000)
CURRENT_SCORE = 0


class Bullet:
    def __init__(self, x, y, bullet_img):
        self.x = x
        self.y = y
        self.bullet_img = bullet_img
        self.mask = pygame.mask.from_surface(self.bullet_img)

    def draw(self, screen):
        screen.blit(self.bullet_img, (self.x, self.y))

    def move(self, bullet_speed):
        self.y += bullet_speed

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Vehicle:
    COOLDOWN = 20

    def __init__(self, x, y, health=10):
        self.x = x
        self.y = y
        self.health = health
        self.vehicle_img = None
        self.bullet_img = x_bullet
        self.bullets = []
        self.cooldown_counter = 0

    def draw(self, screen):
        screen.blit(self.vehicle_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(screen)

    def move_bullets(self, bullet_speed, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(bullet_speed)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 1
                self.bullets.remove(bullet)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            bullet = Bullet(self.x + 10, self.y, self.bullet_img)  # to center the bullet creation
            self.bullets.append(bullet)
            self.cooldown_counter = 1

    def get_width(self):
        return self.vehicle_img.get_width()

    def get_height(self):
        return self.vehicle_img.get_height()


class Player(Vehicle):
    def __init__(self, x, y, health=10):
        super().__init__(x, y, health)
        self.vehicle_img = tank
        self.bullet_img = x_bullet
        self.mask = pygame.mask.from_surface(self.vehicle_img)
        self.health = health
        self.max_hp = health

    def draw(self, screen):
        super().draw(screen)
        self.healthbar(screen)

    def move_bullets(self, bullet_speed, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(bullet_speed)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        global CURRENT_SCORE
                        objs.remove(obj)
                        self.bullets.remove(bullet)
                        CURRENT_SCORE += 1

    def healthbar(self, screen):
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y + self.vehicle_img.get_height() + 10, self.vehicle_img.get_width(), 10))
        pygame.draw.rect(screen, (0, 255, 0),
                         (self.x, self.y + self.vehicle_img.get_height() + 10,
                          self.vehicle_img.get_width() * (self.health / self.max_hp), 10))


class Enemy(Vehicle):
    def __init__(self, x, y, health=10):
        super().__init__(x, y, health)
        self.vehicle_img = ufo
        self.bullet_img = x_laser
        self.mask = pygame.mask.from_surface(self.vehicle_img)
        self.max_hp = health

    def move(self, speed):
        self.y += speed

    def shoot(self):
        if self.cooldown_counter == 0:
            bullet = Bullet(self.x - 18, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cooldown_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def tank_ani():
    tankz = [tank1, tank2, tank3, tank4]
    index = random.randint(0, 3)
    return tankz[index]


def main():
    global CURRENT_SCORE
    CURRENT_SCORE = 0  # reset
    run = True
    FPS = 60
    level = 0
    lives = 5

    enemies = []
    wave_length = 5
    enemy_speed = 2
    player_speed = 6
    bullet_speed = 7

    player = Player(400, 760)

    game_over = False
    game_over_count = 0

    def redraw_window():
        screen.blit(background, (0, 0))
        lives_label = font.render(f"Lives: {lives}", False, (255, 255, 255))
        level_label = font.render(f"Level: {level}", False, (255, 255, 255))
        score = font.render(f"Score: {CURRENT_SCORE}", False, (255, 255, 255))
        screen.blit(score, (300, 10))
        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if game_over:
            x = False
            game_over_label = font.render("You Lost!!", False, (255, 255, 255))
            screen.blit(game_over_label, (WIDTH / 2 - game_over_label.get_width() / 2, 350))

        if not game_over:
            pygame.display.update()

    while run:
        clock.tick(FPS)
        pygame.display.update()
        redraw_window()
        #  loosing terms
        if lives <= 0 or player.health <= 0:
            lives = 0
            player.health = 0
            game_over = True
            game_over_count += 1
            main_menu()
        #  create enemies
        if len(enemies) == 0:
            level += 1
            wave_length += 1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 50), random.randrange(HEIGHT - 2000, HEIGHT - 1500))
                enemies.append(enemy)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()

            if event.type == score_timer:
                CURRENT_SCORE += 1

        # controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > -20:  # left
            player.x -= player_speed
            player.vehicle_img = pygame.transform.scale(tank_ani(), (120, 120)).convert_alpha()

        if keys[pygame.K_RIGHT] and player.x + player.get_width() < 810:  # right
            player.x += player_speed
            player.vehicle_img = pygame.transform.scale(tank_ani(), (120, 120)).convert_alpha()
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_speed)
            enemy.move_bullets(bullet_speed, player)

            if random.randrange(0, 1 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 1
                if CURRENT_SCORE > 0:
                    CURRENT_SCORE -= 1
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                if CURRENT_SCORE > 0:
                    CURRENT_SCORE -= 1
                enemies.remove(enemy)

        player.move_bullets(-bullet_speed, enemies)


def main_menu():
    run = True
    global CURRENT_SCORE

    while run:
        screen.blit(mainmenu, (0, 0))
        main_page_label = font2.render('Press SPACE to START!', False, (0, 0, 0))
        screen.blit(main_page_label, (WIDTH / 2 - main_page_label.get_width() / 2, 750))
        if CURRENT_SCORE != 0:
            sc = font.render(f"YOU LOST! Score: {CURRENT_SCORE}", False, (255, 0, 0))
            screen.blit(sc, (WIDTH / 2 - sc.get_width() / 2, 150))
        pygame.display.update()
        for event in pygame.event.get():
            key = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()

    pygame.quit()


main_menu()
