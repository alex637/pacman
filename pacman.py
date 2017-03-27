import sys
import pygame
from pygame.locals import *
from math import floor
import random


def init_window():
    pygame.init()
    pygame.display.set_mode((512, 512))
    pygame.display.set_caption('Pacman')


def draw_background(scr, img=None):
    if img:
        scr.blit(img, (0, 0))
    else:
        bg = pygame.Surface(scr.get_size())
        bg.fill((128, 128, 128))
        scr.blit(bg, (0, 0))


class GameObject(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tile_size, map_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img)
        self.screen_rect = None
        self.x = 0
        self.y = 0
        self.tick = 0
        self.tile_size = tile_size
        self.map_size = map_size
        self.set_coord(x, y)

    def set_coord(self, x, y):
        self.x = x
        self.y = y
        self.screen_rect = Rect(floor(x) * self.tile_size, floor(y) * self.tile_size, self.tile_size, self.tile_size)

    def game_tick(self):
        self.tick += 1

    def draw(self, scr):
        scr.blit(self.image, (self.screen_rect.x, self.screen_rect.y))


class Ghost(GameObject):
    def __init__(self, x, y, tile_size, map_size):
        GameObject.__init__(self, './resources/ghost.png', x, y, tile_size, map_size)
        self.direction = 0
        self.velocity = 4.0 / 10.0

    def update(self):
        super(Ghost, self).game_tick()
        if self.tick % 20 == 0 or self.direction == 0:
            self.direction = random.randint(1, 4)

        x, y = self.x, self.y
        if self.direction == 1:
            x += self.velocity
        elif self.direction == 2:
            y += self.velocity
        elif self.direction == 3:
            x -= self.velocity
        elif self.direction == 4:
            y -= self.velocity

        if x >= self.map_size:
            x = self.map_size - 1
            self.direction = random.randint(1, 4)
        elif y >= self.map_size:
            y = self.map_size - 1
            self.direction = random.randint(1, 4)
        elif x <= 0:
            x = 0
            self.direction = random.randint(1, 4)
        elif y <= 0:
            y = 0
            self.direction = random.randint(1, 4)

        if map.get(x,y) == 1 or map.get(x,y) == 2:       # a wall
            self.direction = random.randint(1, 4)
        else:
            self.x, self.y = x, y

        self.set_coord(self.x, self.y)
        self.draw(screen)


class Pacman(GameObject):
    def __init__(self, x, y, tile_size, map_size):
        GameObject.__init__(self, './resources/pacman.png', x, y, tile_size, map_size)
        self.direction = 0
        self.velocity = 4.0 / 10.0
        self.special_abilities = [0 for i in range(3)]
        self.points = 0
        self.food_left = 0
        for i in range(map.h):
            for j in range(map.w):
                if map.map[i][j] == 3:
                    self.food_left += 1
        self.check()
        self.path = self.find_path()    # there is some food left


    def update(self):
        super(Pacman, self).game_tick()
        x, y = self.x, self.y
        if self.direction == 1:
            x += self.velocity
        elif self.direction == 2:
            y += self.velocity
        elif self.direction == 3:
            x -= self.velocity
        elif self.direction == 4:
            y -= self.velocity
        if x >= self.map_size:
            x = self.map_size - 1
        elif y >= self.map_size:
            y = self.map_size - 1
        elif x <= 0:
            x = 0
        elif y <= 0:
            y = 0

        data = map.get(x, y)
        if data == 1:      # unbreakable wall
            self.direction = 0
        elif data == 2:    # breakable wall
            self.x, self.y = x, y
            map.used(self.x, self.y)
        elif data == 3:    # food
            self.x, self.y = x, y
            self.points += 1
            self.food_left -= 1
            self.check()
            self.path = self.find_path()  # there is still some food
            map.used(self.x, self.y)
        elif data == 4:     # artifact_1 - extra 5 points
            self.x, self.y = x, y
            self.points += 5
            map.used(self.x, self.y)
        elif data == 5:     # artifact_2 - surviving meeting with a ghost
            self.x, self.y = x, y
            self.special_abilities[0] = 1
            map.used(self.x, self.y)
        else:
            self.x, self.y = x, y

        if (floor(self.x), floor(self.y)) == self.path[1]:
            self.path.pop(1)
        self.set_coord(self.x, self.y)


    def check(self):
        for ghost in sprites:
            if floor(ghost.x) == floor(self.x) and floor(ghost.y) == floor(self.y):
                if self.special_abilities[0]:
                    self.special_abilities[0] = 0
                else:           # end of the game
                    print('You met a ghost. Game over.')
                    sys.exit(0)
        if self.food_left == 0:
            print("Congratulations!!! Level passed! You get {0} points.".format(self.points))
            sys.exit(0)

    def find_path(self):
        n = map.h
        m = map.w
        special_map = [[None] * m for i in range(n)]
        for i in range(n):
            for j in range(m):
                if map.get(i, j) == 3:      # food
                    special_map[i][j] = 2
                elif map.get(i, j) == 1:    # unbreakable wall
                    special_map[i][j] = 0
                else:
                    special_map[i][j] = 1   # possible to visit

        paths = [[[]] * m for i in range(n)]
        paths[floor(self.x)][floor(self.y)].append((floor(self.x), floor(self.y)))
        q = [(floor(self.x), floor(self.y))]
        while q:
            current_x, current_y = q.pop(0)
            for x, y in [(current_x - 1, current_y), (current_x, current_y - 1),
                         (current_x, current_y + 1), (current_x + 1, current_y)]:
                if 0 <= x < n and 0 <= y < m:
                    if special_map[x][y] == 2:
                        return paths[current_x][current_y] + [(x, y)]
                    elif special_map[x][y]:
                        q.append((x, y))
                        paths[x][y] = paths[current_x][current_y] +[(x, y)]
                        special_map[x][y] = 0
        # food cannot be reached, so:
        print("You cannot get any more food. Your score is {0} points.".format(self.points))
        sys.exit(0)


class Map:
    def __init__(self, w, h, tile_size, file=None):
        self.wall_image = pygame.image.load("./resources/wall.png")
        self.breakable_wall_image = pygame.image.load("./resources/breakable_wall.png")
        self.food_image = pygame.image.load("./resources/food.jpg")
        self.map = [[0] * w for i in range(h)]
        self.w = w
        self.h = h
        self.tile_size = tile_size
        if file:
            with open(file) as f:
                for i in range(h):
                    line = f.readline()
                    self.map[i] = list(int(x) for x in line.rstrip().split())

    def get(self, x, y):    # Функция возвращает обьект в данной точке карты
        return self.map[floor(y)][floor(x)]

    def draw(self):
        for i in range(self.h):
            for j in range(self.w):
                c = self.map[i][j]
                if c == 1:      # unbreakable wall
                    screen.blit(self.wall_image, (j * self.tile_size, i * self.tile_size,
                                                  self.tile_size, self.tile_size))
                elif c == 2:    # breakable wall
                    screen.blit(self.breakable_wall_image, (j * self.tile_size, i * self.tile_size,
                                                  self.tile_size, self.tile_size))
                elif c == 3:    # food (standard white spot) - hamburger
                    screen.blit(self.food_image, (j * self.tile_size, i * self.tile_size,
                                                  self.tile_size, self.tile_size))

    def used(self, x, y):
        # breaking the wall or eating the food or getting the artifact
        self.map[floor(y)][floor(x)] = 0


def process_events(events, pacman):
    pacman.direction = 0
    d = {K_LEFT: 3, K_RIGHT: 1, K_UP: 4, K_DOWN: 2}
    for event in events:
        if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
            sys.exit(0)
        elif event.type == KEYDOWN and event.key in d:
            pacman.direction = d[event.key]
    if pacman.direction == 0:
        x, y = pacman.find_path()[1]
        if x > pacman.x:
            pacman.direction = 1  # to the right
        elif x < floor(pacman.x):
            pacman.direction = 3  # to the left
        elif y > pacman.y:
            pacman.direction = 2  # downwards
        else:
            pacman.direction = 4  # upwards


if __name__ == '__main__':
    init_window()
    tile_size = 32
    map_size = 16
    map = Map(map_size, map_size, tile_size, "./resources/map_1.txt")
    ghost1 = Ghost(2, 2, tile_size, map_size)
    ghost2 = Ghost(10, 10, tile_size, map_size)
    sprites = pygame.sprite.Group()
    sprites.add(ghost1, ghost2)
    pacman = Pacman(5, 5, tile_size, map_size)
    background = pygame.image.load("./resources/background.png")
    screen = pygame.display.get_surface()

    while 1:
        process_events(pygame.event.get(), pacman)
        pygame.time.delay(100)
        draw_background(screen, background)
        sprites.update()
        pacman.update()
        map.draw()
        pacman.draw(screen)
        pygame.display.update()
        pacman.check()
