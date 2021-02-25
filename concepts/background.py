import os
import pygame

path = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir))

background = pygame.image.load(path + "/images/background.png")
background_width = background.get_width()

def blit_background(display, background, x = 0):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        x += 1
    if keys[pygame.K_d]:
        x -= 1

    if x > 0:
        x -= background_width
    elif x <= -background_width:
        x = 0

    x2 = background_width + x

    display.blit(background, (x, 0))
    display.blit(background, (x2, 0))

    return x

width = 320 #512
height = 180 #288
FPS = 100
clock = pygame.time.Clock()

screenWidth = 640
screenHeight = 360

screen = pygame.display.set_mode((screenWidth, screenHeight))
display = pygame.Surface((width, height))

run = True

x = 0

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    clock.tick(FPS)

    x = blit_background(display, background, x)

    screen.blit(pygame.transform.scale(display, (screenWidth, screenHeight)), (0, 0))

    pygame.display.update()
