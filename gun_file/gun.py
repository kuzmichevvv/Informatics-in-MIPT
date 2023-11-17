import math
from random import choice

import pygame


FPS = 30

RED = 0xFF0000
GREY = 0x7D7D7D
BLACK = (0, 0, 0)
NEON = (57, 255, 20)
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
ENEMY = (207, 16, 32)
WHITE = 0xFFFFFF
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class EnemyGun:
    def __init__(self, screen):
        self.screen = screen
        self.power = 3
        self.x = 0
        self.y = 0
        self.an = 1
        self.color = RED
        self.term = 1

    def fire2_end(self):
        global enemy_ball
        new_ball = EnemyBall(self.screen, self.x, self.y)
        new_ball.r += 5
        new_ball.vx = self.power * math.cos(self.an)
        new_ball.vy = - self.power * math.sin(self.an)

        enemy_ball.append(new_ball)
        self.power = choice(range(4, 10))

    def draw(self):
        angle = self.an
        dx = 30
        self.x = 20 + dx * math.cos(angle)
        self.y = 300 + dx * math.sin(angle)
        pygame.draw.line(self.screen, self.color, (20, 300), (self.x, self.y), width=5)

    def enemy_targetting(self):
        if self.an >= math.pi / 2:
            self.term = -1
        if self.an <= -math.pi / 2:
            self.term = 1
        self.an += 0.1 * self.term
        n = choice(range(20))
        if n in [0, 19]:
            self.fire2_end()


class EnemyBall:
    def __init__(self, screen: pygame.Surface, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 5
        self.vx = 0
        self.vy = 0
        self.color = ENEMY

    def move(self):
        self.x += self.vx
        self.y -= self.vy
        self.vy -= 0.1

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        pygame.draw.circle(
            self.screen,
            BLACK,
            (self.x, self.y),
            self.r - 3
        )

    def enemy_hittest(self, obj):
        if self.x >= obj.x - 24 and self.x <= obj.x + 24 and self.y >= obj.y - 10 and self.y <= obj.y + 20:
            return True
        return False


class Tank:
    def __init__(self, screen):
        self.screen = screen
        self.x = 40
        self.y = 580
        self.xx = 0
        self.yy = 0
        self.an = 0
        self.tank_on = 0
        self.tank_power = 0
        self.color = GREY

    def draw(self):
        angle = self.an
        dx = 20 + self.tank_power
        self.xx = self.x + dx * math.cos(angle)
        self.yy = self.y + dx * math.sin(angle) - 10
        if self.y - 10 <= self.yy:
            self.yy = self.y - 10
        pygame.draw.line(self.screen, self.color, (self.x, self.y - 10), (self.xx, self.yy), width=5)
        pygame.draw.rect(self.screen, GREY, (self.x - 10, self.y - 10, 20, 8), 0)
        pygame.draw.rect(self.screen, GREY, (self.x - 20, self.y - 2, 40, 12), 0)
        pygame.draw.rect(self.screen, BLACK, (self.x - 13, self.y + 5, 26, 10), 0)
        pygame.draw.circle(self.screen, BLACK, (self.x - 13, self.y + 10), 5)
        pygame.draw.circle(self.screen, BLACK, (self.x + 13, self.y + 10), 5)

    def targetting(self, event):
        if event:
            self.an = math.atan2((event.pos[1] - self.y + 10), (event.pos[0] - self.x))
        if self.tank_on:
            self.color = RED
        else:
            self.color = GREY

    def tank_power_up(self):
        if self.tank_on:
            if self.tank_power < 50:
                self.tank_power += 1
            self.color = RED
        else:
            self.color = GREY

    def move_left(self):
        self.x -= 5

    def move_right(self):
        self.x += 5

    def tank_fire(self, event):
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        new_ball.tank_off = 0
        new_ball.x = self.xx
        new_ball.y = self.yy
        new_ball.r += 5
        self.an = math.atan2((event.pos[1] - new_ball.y), (event.pos[0] - new_ball.x))
        new_ball.vx = self.tank_power * math.cos(self.an)
        new_ball.vy = - self.tank_power * math.sin(self.an)

        balls.append(new_ball)
        self.tank_on = 0
        self.tank_power = 0

    def tank_start_fire(self):
        self.tank_on = 1


class Rocket:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 30
        self.vx = 0
        self.vy = 0
        self.color = NEON
        self.live = 30

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.x += 3

    def explosion(self, targets):
        pygame.draw.line(self.screen, NEON, (self.x, -10), (self.x, 700), width=5)
        for target in targets.targets:
            x = target[0].x
            r = target[0].r
            if (self.x - x)**2 <= r**2:
                targets.new_target(type=target[1], obj=target[0])
                targets.hit()


    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


    def hittest(self, obj):
        return False


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30
        self.tank_off = 1

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        # FIXME
        self.x += self.vx
        self.y -= self.vy
        if self.tank_off:
            self.vy -= 0.7

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if (obj.x - self.x)**2 + (obj.y - self.y)**2 <= (self.r + obj.r)**2:
            return True
        return False


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.type = 1

    def change_type(self):
        self.type += 1
        self.type %= 2

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        if self.type == 1:
            new_ball = Ball(self.screen)
            new_ball.r += 5
            self.an = math.atan2((event.pos[1] - new_ball.y), (event.pos[0] - new_ball.x))
            new_ball.vx = self.f2_power * math.cos(self.an)
            new_ball.vy = - self.f2_power * math.sin(self.an)
        else:
            new_ball = Rocket(self.screen)

        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if self.type == 1:
            if event:
                self.an = math.atan2((event.pos[1]-450), (event.pos[0]-20))
            if self.f2_on:
                self.color = RED
            else:
                self.color = GREY
        else:
            self.color = NEON

    def draw(self):
        if self.type == 1:
            angle = self.an
            power =self.f2_power
            dx = power * 2
            x = 20 + dx * math.cos(angle)
            y = 450 + dx * math.sin(angle)
            pygame.draw.line(self.screen, self.color, (20, 450), (x, y), width=5)
        else:
            pygame.draw.line(self.screen, NEON, (20, 450), (30, 450), width=5)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY


class Targets:
    def __init__(self, screen):
        self.targets = []
        self.points = 0
        self.screen = screen

    def hit(self):
        self.points += 1

    def new_target(self, type=0, obj=None):
        if obj:
            self.targets.remove((obj, type))

        if type == 0:
            obj = Target_one(self.screen)
            self.targets.append((obj, 0))

        if type == 1:
            obj = Target_two(self.screen)
            self.targets.append((obj, 1))


class Target_one:
    def __init__(self, screen, pos_x1=600, pos_x2=780):
        self.screen = screen
        self.vy = 0
        self.x = choice(range(pos_x1, pos_x2))
        self.y = choice(range(300, 550))
        self.r = choice(range(2, 50))
        self.color = RED

    def move(self):
        self.y += self.vy
        if self.vy >= 0:
            self.vy += 1
        else:
            self.vy += 1.1
        if self.y + self.r >= 600:
            self.vy *= -1

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


class Target_two:
    def __init__(self, screen, pos_x1=300, pos_x2=700):
        self.screen = screen
        self.vr = -1.5
        self.x = choice(range(pos_x1, pos_x2))
        self.y = choice(range(100, 500))
        self.r = choice(range(40, 100))
        self.color = BLACK

    def move(self):
        self.r += self.vr
        if self.r <= 0:
            self.x = choice(range(200, 700))
            self.y = choice(range(100, 500))
            self.r = choice(range(40, 100))


    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Lora', 20)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
tank = Tank(screen)
enemy_ball = []
enemy_gun = EnemyGun(screen)
targets = Targets(screen)
targets.new_target()
targets.new_target(1)
finished = False
type_of_gun = 1
flag_move_left = False
flag_move_right = False
flag = True
lives = 5

while not finished:
    if flag:
        screen.fill(WHITE)
        if type_of_gun == 1:
            gun.draw()
        else:
            tank.draw()
            enemy_gun.draw()
            enemy_gun.enemy_targetting()

        for i in enemy_ball:
            i.draw()

        for target in targets.targets:
            target[0].draw()

        for b in balls:
           b.draw()

        # draw text
        text_surface = my_font.render(f'Сбито Мишеней: {targets.points}', True, BLACK)
        screen.blit(text_surface, (10, 10))
        text_surface = my_font.render(f'Потрачено шаров: {bullet}', True, BLACK)
        screen.blit(text_surface, (10, 35))
        text_surface = my_font.render(f'Количество жизней: {lives}', True, BLACK)
        screen.blit(text_surface, (10, 60))

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if type_of_gun == 1:
                    gun.fire2_start(event)
                else:
                    tank.tank_start_fire()
            elif event.type == pygame.MOUSEBUTTONUP:
                if type_of_gun == 1:
                    gun.fire2_end(event)
                else:
                    tank.tank_fire(event)
            elif event.type == pygame.MOUSEMOTION:
                if type_of_gun == 1:
                    gun.targetting(event)
                else:
                    tank.targetting(event)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                if type_of_gun == 1:
                    gun.change_type()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                type_of_gun += 1
                type_of_gun = type_of_gun % 2
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for b in balls:
                    if isinstance(b, Rocket):
                        b.explosion(targets)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                flag_move_left = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                flag_move_left = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                flag_move_right = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                flag_move_right = False

        # move
        count = 0
        len_balls = len(balls)
        for i in range(len_balls):
            b = balls[i - count]
            for target in targets.targets:
                if b.hittest(target[0]):
                    balls.pop(i)
                    targets.new_target(type=target[1], obj=target[0])
                    targets.hit()
                    count += 1
                    break

        for i in enemy_ball:
            if i.enemy_hittest(tank):
                lives -= 1
                enemy_ball.remove(i)
            if lives <= 0:
                flag = False

        for i in enemy_ball:
            i.move()

        pygame.display.update()

        for i in balls:
            i.move()

        if flag_move_right:
            tank.move_right()
        elif flag_move_left:
            tank.move_left()

        for i in targets.targets:
            i[0].move()

        gun.power_up()
        tank.tank_power_up()
    else:
        my_font = pygame.font.SysFont('Lora', 70)
        screen.fill(WHITE)
        text_surface = my_font.render(f'Вы проиграли', True, BLACK)
        screen.blit(text_surface, (100, 100))
        pygame.display.update()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
pygame.quit()
