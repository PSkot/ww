import pygame
import time
import random
import csv
import os
from engine import *
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,30)

scale = 2


FPS = 50
SCREEN_SIZE = 500*scale
PLAYER_HEIGHT = 20*scale
PLAYER_WIDTH = 10*scale


grass1 = pygame.image.load('./images/grass1.png')
dirt1 = pygame.image.load('./images/dirt1.png')
spikes1 = pygame.image.load('./images/spikes1.png')
mage1 = pygame.image.load('./images/mage1.png')
staff1_nofire = pygame.image.load('./images/staff1_nofire.png')
staff1_fire = pygame.image.load('./images/staff1_fire.png')
enemy1 = pygame.image.load('./images/enemy1.png')

ABILITIES = {
1: (255, 0, 0),
2: (0, 255, 0),
3: (255, 0, 255),
}


NAME = "Waldo's World"

MAP_SIZE = 20
clock = pygame.time.Clock()

BLOCK_SIZE = SCREEN_SIZE//MAP_SIZE
grass1 = pygame.transform.scale(grass1, (BLOCK_SIZE, BLOCK_SIZE))
dirt1 = pygame.transform.scale(dirt1, (BLOCK_SIZE, BLOCK_SIZE))
spikes1 = pygame.transform.scale(spikes1, (BLOCK_SIZE, BLOCK_SIZE))
mage1 = pygame.transform.scale(mage1, (38, 70))
staff1_nofire = pygame.transform.scale(staff1_nofire, (16, 48))
staff1_fire = pygame.transform.scale(staff1_fire, (16, 48))
enemy1 = pygame.transform.scale(enemy1, (15*scale, 15*scale))

BLOCK_TYPES = {
1: grass1,
2: dirt1,
3: spikes1,
4: (),
}


def read_map(file):
    map = []
    with open(file) as f:
        lines = f.readlines()
    for line in lines:
        map.append([int(i) for i in line.strip().split("  ")])
    return map

def read_enemies(file):
    enemies = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter = ',')
        for row in reader:
            enemies.append(row)
    return enemies

MAPS = {
1: read_map('map1.txt'),
2: read_map('map2.txt'),
}



level = 1

def spawnEnemies():
    pass

def readMap():
    pass

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption(NAME)
def game(map, level, final_level = False):

    objectCoords = []

    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if map[i][j] != 0:
                objectCoords.append([[j*BLOCK_SIZE, i*BLOCK_SIZE], map[i][j]])

    run = True
    jumpSize = BLOCK_SIZE-5*scale
    shootLoop = 0
    playerHeight = 35*scale
    playerWidth = 19*scale
    collisionLag = 0
    ENEMIES = {
    1: entity(100, SCREEN_SIZE - BLOCK_SIZE*2 - 15*scale,
        15*scale, 15*scale, 5, 8, 10, 10, objectCoords, img = enemy1, type = 'enemy',
        jumpSize = 20)
    }
    main_char = entity(
                    0, SCREEN_SIZE - BLOCK_SIZE*3 - playerHeight,
                    playerWidth, playerHeight, 5*scale, 8*scale, 10, 10, objectCoords,
                    jumpSize = jumpSize, img = mage1, weaponImg = staff1_nofire,
                    weaponImgFire = staff1_fire)
    explosion = True

    while run:
        mousePos = pygame.mouse.get_pos()
        mouseClicked = False



        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseClicked = True

        screen.fill((0, 0, 0))

        #Draw map
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                if map[i][j] != 0:
                    x, y = (j*BLOCK_SIZE, i*BLOCK_SIZE)
                    screen.blit(BLOCK_TYPES[map[i][j]], (x,y))

        #Update main character

        if main_char.enemyCollision(ENEMIES) and collisionLag == 0:
            main_char.health -= 1
            collisionLag = 11

        if collisionLag > 0:
            collisionLag -= 1

        main_char.update(mousePos, screen, mouseClicked, BLOCK_SIZE, SCREEN_SIZE, explosion, final_level)

        #Draw enemies
        for id, enemy in ENEMIES.items():
            enemy.update(mousePos, screen, mouseClicked, BLOCK_SIZE, SCREEN_SIZE, explosion, final_level)


        pygame.display.update()

        #Level change if not on final level

        if main_char.health == 0:
            game(MAPS[level], level)
            quit()

        if main_char.x > SCREEN_SIZE and level == 1:
            level += 1
            game(MAPS[level], level, True)
            quit()



if __name__ == '__main__':
    game(MAPS[level], level)
