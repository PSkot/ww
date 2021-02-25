import pygame

def main():
    screen = pygame.display.set_mode((200, 200))
    fake_screen = pygame.display.set_mode((300, 300))
    pic = pygame.surface.Surface((50, 50))
    pic.fill((255, 100, 200))

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # elif event.type == VIDEORESIZE:
            #     screen = pygame.display.set_mode(event.size, HWSURFACE|DOUBLEBUF|RESIZABLE)

        fake_screen.fill((0, 0, 0))
        fake_screen.blit(pic, (100, 100))
        screen.blit(pygame.transform.scale(fake_screen, screen.get_rect().size), (0, 0))
        pygame.display.update()

main()
