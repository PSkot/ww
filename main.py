import pygame
import time
import random
import csv
from engine import *

FPS = 50
SCREEN_SIZE = 500
PLAYER_HEIGHT = 20
PLAYER_WIDTH = 10

BLOCK_TYPES = {
1: (0,150,0),
2: (139,69,19),
3: (255, 255, 255),
4: (),
}

ABILITIES = {
1: (255, 0, 0),
2: (0, 255, 0),
3: (255, 0, 255),
}


NAME = "Waldo's World"

MAP_SIZE = 20
clock = pygame.time.Clock()

BLOCK_SIZE = SCREEN_SIZE//MAP_SIZE

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

ENEMIES = {
1: entity(100, SCREEN_SIZE - BLOCK_SIZE*3 - 35,
    25, 35, 5, 8, 10, 10)
}

level = 1

def spawnEnemies():
    pass

def readMap():
    pass

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption(NAME)
def game(map, level, final = False):

    objectCoords = []

    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if map[i][j] != 0:
                objectCoords.append([[j*BLOCK_SIZE, i*BLOCK_SIZE], map[i][j]])

    run = True
    numJumps = 6
    jumpSize = BLOCK_SIZE-5
    jumpLoop = numJumps
    shootLoop = 0
    jump = False
    drop = False
    damage = False
    playerHeight = 35
    playerWidth = 25
    collisionLag = 0
    main_char = entity(
                    0, SCREEN_SIZE - BLOCK_SIZE*3 - playerHeight,
                    playerWidth, playerHeight, 5, 8, 10, 10)
    explosion = True

    while run:
        mousePos = pygame.mouse.get_pos()
        mouseClicked = False

        main_char.update(mousePos)

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseClicked = True

        screen.fill((0, 0, 0))

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                if map[i][j] != 0:
                    rect = pygame.Rect(j*BLOCK_SIZE, i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(screen, BLOCK_TYPES[map[i][j]], rect)

        key = pygame.key.get_pressed()

        for j in objectCoords:
            main_char.checkCollision(j[0], BLOCK_SIZE)

        if key[pygame.K_SPACE] and main_char.downCollision:
            jump = True

        if key[pygame.K_d] and not main_char.rightCollision:
            if final and main_char.x + main_char.w >= SCREEN_SIZE:
                pass
            else:
                for i in range(main_char.x_vel):
                    for j in objectCoords:
                        main_char.checkCollision(j[0], BLOCK_SIZE)

                    if not main_char.rightCollision and (drop or jump or main_char.downCollision):
                        main_char.x += 1

        if key[pygame.K_a] and not main_char.leftCollision and main_char.x > 0:
            for i in range(main_char.x_vel):
                for j in objectCoords:
                    main_char.checkCollision(j[0], BLOCK_SIZE)
                if not main_char.leftCollision and (drop or jump or main_char.downCollision):
                    main_char.x -= 1



        #Draw crosshair
        pygame.draw.line(screen, (150, 150, 150), [main_char.pos[0] - 5, main_char.pos[1]], [main_char.pos[0] + 5, main_char.pos[1]],  1)
        pygame.draw.line(screen, (150, 150, 150), [main_char.pos[0], main_char.pos[1] - 5], [main_char.pos[0], main_char.pos[1] + 5],  1)
        pygame.mouse.set_visible(False)


        if main_char.shootLoop > 0:
            main_char.shootLoop -= 1

        #Draw character
        main_char.drawHitBoxes(screen)
        main_char.drawHealth(screen)
        main_char.drawWeaponBox(screen)
        main_char.drawWeaponLocation(screen)
        if main_char.enemyCollision(ENEMIES) and collisionLag == 0:
            main_char.health -= 1
            collisionLag = 11

        if collisionLag > 0:
            collisionLag -= 1


        #Draw enemies
        for id, enemy in ENEMIES.items():
            enemy.drawHitBoxes(screen)
            enemy.drawHealth(screen)

        main_char.updateShots(screen, objectCoords, mouseClicked)



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
