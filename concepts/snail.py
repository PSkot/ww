import os
import pygame

subfolder = 'images/enemies/snail'
path = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir, subfolder))

snails = [pygame.image.load(os.path.join(path, i)) for i in os.listdir(path)]


width = 320 #512
height = 180 #288
FPS = 50
clock = pygame.time.Clock()

screenWidth = 640
screenHeight = 360

screen = pygame.display.set_mode((screenWidth, screenHeight))
display = pygame.Surface((width, height))

run = True
animationLoop = 0
snailDest = 250
snailSpeed = 1.5

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    clock.tick(FPS)

    display.fill((0, 0, 0))

    display.blit(snails[animationLoop//3-1], (snailDest, 90))

    if animationLoop//3 == 3:
        snailDest -= snailSpeed


    animationLoop += 1
    if animationLoop > 20:
        animationLoop = 0

    screen.blit(pygame.transform.scale(display, (screenWidth, screenHeight)), (0, 0))
    pygame.display.update()
