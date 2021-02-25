import pygame
import time
import random
import csv
import os
import json
import pandas as pd
from engine import *
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,30)

with open("./playerConfig.json") as f:
    PLAYER_DATA = json.load(f)

IMAGE_PATH = PLAYER_DATA['Base']['images']

FPS = 30
SCREEN_SIZE = 500

tile_data = pd.read_csv('tiles.txt')
tile_data['SURFACE'] = [pygame.image.load(IMAGE_PATH + "tiles/" + str(i)) for i in tile_data['IMAGE']]

playerImg = pygame.image.load(IMAGE_PATH + "player/" + "playerimage.png")
weapon_idle = pygame.image.load(IMAGE_PATH + "player/" + "weapon_idle.png")
weapon_fire = pygame.image.load(IMAGE_PATH + "player/" + "weapon_fire.png")
blob = pygame.image.load(IMAGE_PATH + "enemies/" + "blob.png")
skeleton1 = pygame.image.load(IMAGE_PATH + "enemies/" + "skeleton1.png")
skeleton2 = pygame.image.load(IMAGE_PATH + "enemies/" + "skeleton2.png")
skeletonagg1 = pygame.image.load(IMAGE_PATH + "enemies/" + "skeleton_agg1.png")
skeletonagg2 = pygame.image.load(IMAGE_PATH + "enemies/" + "skeleton_agg2.png")
skeletonWeapon = pygame.image.load(IMAGE_PATH + "enemies/" + "skeletonWeapon.png")
shotImg = pygame.image.load(IMAGE_PATH + "player/" + "shot.png")
portalImages = [pygame.image.load(IMAGE_PATH + "portal/portal" + str(i+1) + ".png") for i in range(12)]

NAME = "Waldo's World"
MAP_SIZE = 20
clock = pygame.time.Clock()

BLOCK_SIZE = SCREEN_SIZE//MAP_SIZE

BLOCK_TYPES = {
1: tile_data[tile_data['ID'] == 1]['SURFACE'].values[0],
2: tile_data[tile_data['ID'] == 2]['SURFACE'].values[0],
3: tile_data[tile_data['ID'] == 3]['SURFACE'].values[0],
}


MAPS = read_maps('C:\Users\pete_\Documents\GitHub\ww\levels\1\maps', 2)
level = 1

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), 0, 32)

pygame.display.set_caption(NAME)
def game(map, level, final_level = False):

    tiles = []

    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if map[i][j] != 0:
                tiles.append(
                    {"rect": pygame.Rect(j*BLOCK_SIZE, i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    "type": map[i][j],
                    "img": BLOCK_TYPES[map[i][j]]
                    })


    jumpSize = PLAYER_DATA['Base']['jumpSize']
    player_x, player_x = (PLAYER_DATA['Location']['x'], PLAYER_DATA['Location']['y'])
    playerHeight, playerWidth = (PLAYER_DATA['Base']['height'], PLAYER_DATA['Base']['width'])
    player_x_vel, player_y_vel = (PLAYER_DATA['Base']['x_vel'], PLAYER_DATA['Base']['y_vel'])
    playerMaxHP, playerCurrentHP = (PLAYER_DATA['Base']['maxHitPoints'], PLAYER_DATA['Base']['currentHitPoints'])


    ENEMIES = [
    {
    1: greenBlob(pygame.Rect(100, 250,
        15, 15), 4, 5, 10, 10, tiles, img = [blob], dmg = 5),
    2: greenBlob(pygame.Rect(250, 250,
        30, 30), 8, 10, 15, 20, tiles, img = [blob], dmg = 8),
    3: skeleton(pygame.Rect(30, 250, 19, 35), 8, 5, 15, 15, tiles, img = [skeleton1, skeleton2], dmg = 10,
                aggImg = [skeletonagg1, skeletonagg2], weaponImg = skeletonWeapon)
    },
    {
    1: greenBlob(pygame.Rect(275, 0, 15*15, 15*15), 1, 10, 25, 50, tiles, img = [blob], dmg = 25)
    }
    ]


    main_char = player(
                    pygame.Rect(player_x, player_x, playerWidth, playerHeight),
                    player_x_vel, player_y_vel, playerCurrentHP,
                    playerMaxHP, tiles, img = [playerImg], weaponImg = weapon_idle,
                    weaponImgFire = weapon_fire, shotImg = shotImg, jumpSize = jumpSize)

    port = portal(pygame.Rect(SCREEN_SIZE-11, SCREEN_SIZE-BLOCK_SIZE*2-32, 11, 32), portalImages)

    degrees = 0
    run = True
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

        #Update enemies
        for id, enemy in ENEMIES[level-1].items():
            if enemy.health <= 0:
                ENEMIES[level-1].pop(id)
                break

        for id, enemy in ENEMIES[level-1].items():
            enemy.update(screen)


        #Update player
        main_char.update(mousePos, screen, mouseClicked, SCREEN_SIZE, ENEMIES[level-1].values(), final_level)

        #Level change if not on final level
        if main_char.health <= 0:
            game(MAPS[level], level)
            quit()

        if not len(ENEMIES[level-1]) and level == 1:
            port.spawn(screen)

        if port.spawned and main_char.rect.x > SCREEN_SIZE and level == 1:
            level += 1
            game(MAPS[level], level, True)
            quit()

        pygame.display.update()

if __name__ == '__main__':
    game(MAPS[level], level)
