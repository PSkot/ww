import pygame
import math
import random

class entity:
    def __init__(self, rect, x_vel, y_vel, health, maxHealth,
    tiles = None, img = None):
        self.rect = rect
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.health = health
        self.maxHealth = maxHealth
        self.tiles = tiles
        self.img = [pygame.transform.scale(i, (self.rect.width, self.rect.height)) for i in img]

        #Variable initialization
        self.movement = 0
        self.collisions = {'up': False, 'right': False, 'down': False, 'left': False}

    def update(self, win):
        self.move()
        self.drawEntity(win)
        self.drawHealth(win)

    def drawHealth(self, win):
        pygame.draw.rect(win, (200, 0, 0), (self.rect.x, self.rect.y - 10, self.rect.width, 5))
        if self.health > 0:
            health_size = int(self.rect.width*self.health/self.maxHealth)
            if not health_size:
                pygame.draw.rect(
                        win, (0, 200, 0),
                        (self.rect.x, self.rect.y - 10, 1, 5))
            else:
                pygame.draw.rect(
                        win, (0, 200, 0),
                        (self.rect.x, self.rect.y - 10, health_size, 5))

    def drawEntity(self, win):
        win.blit(self.img, (self.rect.x, self.rect.y))

    def checkCollision(self, tiles, pos = 'x'):
        for t in tiles:
            if self.rect.colliderect(t['rect']):
                if pos == 'x':
                    if self.movement > 0:
                        self.rect.right = t['rect'].left
                        self.collisions['right'] = True

                    elif self.movement < 0:
                        self.rect.left = t['rect'].right
                        self.collisions['left'] = True

                else:
                    if t['rect'].y > self.rect.y:
                        self.rect.bottom = t['rect'].top
                        self.collisions['down'] = True

                    else: #t['rect'].y < self.rect.y:
                        self.rect.top = t['rect'].bottom
                        self.collisions['up'] = True

    def move(self):
        self.rect.y += self.y_vel
        self.checkCollision(self.tiles, pos = 'y')

    def drawEntityRect(self, win):
        pygame.draw.rect(win, (255, 0, 0), self.rect, 2)


class player(entity):

    def __init__(self, rect, x_vel, y_vel, health, maxHealth,
    tiles = None, img = None, weaponImg = None, weaponImgFire = None,
    shotImg = None, numJumps = 6, jumpCount = 10, jumpSize = 20, dmg = 10,
    ):
        super(player, self).__init__(rect, x_vel, y_vel, health, maxHealth,
        tiles, img)

        #Variable initialization
        self.jump = False
        self.numJumps = numJumps
        self.jumpCount = 0
        self.shots = []
        self.shootSpeed = 20
        self.shootLoop = 10
        self.lag = 0
        self.jumpSize = jumpSize
        self.dmg = dmg

        #Set up images
        self.weaponImg = weaponImg
        self.weaponImgFire = weaponImgFire
        self.shotImg = shotImg

        self.img_front = img
        self.img_back = [pygame.transform.flip(i, True, False) for i in img]

    def update(self, pos, win, mouseClicked, screenSize, enemies, final_level):

        self.pos = pos

        self.move(screenSize, final_level)
        self.drawEntity(win)
        self.drawHealth(win)
        self.drawWeapon(win, True)
        self.drawCrossHair(win)
        self.updateShots(win, mouseClicked, enemies)
        self.enemyCollision(win, enemies)
        self.enemyDamage(win, enemies)

    def move(self, SCREEN_SIZE, final_level):
        key = pygame.key.get_pressed()

        self.collisions = {'up': False, 'right': False, 'down': False, 'left': False}

        if key[pygame.K_d]:
            self.movement = 1
            if final_level and self.rect.x + self.rect.width >= SCREEN_SIZE:
                pass
            else:
                self.rect.x += self.x_vel

        elif key[pygame.K_a] and self.rect.x > 0:
            self.movement = -1
            self.rect.x -= self.x_vel

        #X-collision check
        self.checkCollision(self.tiles)

        self.movement = 0

        #Y-collision check
        if not self.jump:
            self.rect.y += self.y_vel
        else:
            self.rect.y -= self.jumpSize

        self.checkCollision(self.tiles, pos = 'y')

        if self.collisions['up']:
            self.jump = False
            #self.rect.y += self.momentum

        #Handle jump and drop
        if self.collisions['down']:
            self.jumpCount = self.numJumps
            self.jump = False
            if key[pygame.K_SPACE]:
                self.jump = True

        self.jumpCount -= 1

        if self.jumpCount == 0:
            self.jump = False
            self.jumpCount = self.numJumps

    def updateShots(self, screen, mouseClicked, enemies):
        if mouseClicked and self.shootLoop == 0:
            self.shots.append(projectile(self.shotLoc[0], self.shotLoc[1], self.shotDir[0], self.shotDir[1], img = self.shotImg))
            self.shootLoop = self.shootSpeed

        for shot in reversed(self.shots):
            for _ in range(shot.shootVel):
                shot.x += shot.dir_x
                shot.y += shot.dir_y
                shotMask = pygame.mask.from_surface(shot.img)

                #Bullet-tile collision
                for tile, e in zip(self.tiles, enemies):
                    tileImg = tile['img']
                    tileImg.set_colorkey((0, 0, 0))
                    tileMask = pygame.mask.from_surface(tileImg)
                    eMask = pygame.mask.from_surface(e.img)
                    tileOffset = (int(shot.x) - tile['rect'].x, int(shot.y) - tile['rect'].y)
                    eOffset = (int(shot.x) - e.rect.x, int(shot.y) - e.rect.y)
                    tileOverlap = tileMask.overlap(shotMask, tileOffset)
                    eOverlap = eMask.overlap(shotMask, eOffset)

                    if eOverlap is not None:
                        e.health -= self.dmg
                        shot.draw(screen)
                        self.shots.remove(shot)
                        break

                    if tileOverlap is not None:
                        shot.draw(screen)
                        self.shots.remove(shot)
                        break

                else:
                    continue
                break


            shot.draw(screen)

        if self.shootLoop > 0:
            self.shootLoop -= 1

    ### Basic drawings
    def drawEntity(self, win):
        if self.pos[0] > self.rect.x + self.rect.width//2:
            self.img = self.img_front[0]
        else:
            self.img = self.img_back[0]
        win.blit(self.img, (self.rect.x, self.rect.y))


    def drawWeapon(self, win, show = False):
        weaponTimer = 0
        dist = [self.pos[0] - self.rect.x - self.rect.width // 2,
        self.pos[1] - self.rect.y - self.rect.height//2]
        norm = math.sqrt(dist[0] ** 2.0 + dist[1] ** 2.0)
        if norm != 0:
            self.shotDir = [dist[0] / norm, dist[1] / norm]
        self.shotLoc = [
                int(self.shotDir[0]*self.rect.width//2 + self.rect.x + self.rect.width//2),
                int(self.shotDir[1]*self.rect.width//2 + self.rect.y + self.rect.height//2)
                ]

        if self.weaponImg is not None:
            if self.shootLoop > 0 and self.weaponImgFire is not None:
                win.blit(self.weaponImgFire, (self.shotLoc[0]-4, self.shotLoc[1]-12))

            else:
                win.blit(self.weaponImg, (self.shotLoc[0]-4, self.shotLoc[1]-12))

        if show:
            pygame.draw.circle(
                                win, (255, 183, 183),
                                (int(self.shotLoc[0]), int(self.shotLoc[1])),
                                2
                                )

    def drawCrossHair(self, screen):
        pygame.draw.line(screen, (150, 150, 150), [self.pos[0] - 10, self.pos[1]], [self.pos[0] + 10, self.pos[1]],  1)
        pygame.draw.line(screen, (150, 150, 150), [self.pos[0], self.pos[1] - 10], [self.pos[0], self.pos[1] + 10],  1)
        pygame.mouse.set_visible(False)

    #Collisions
    def enemyCollision(self, win, enemies):

        player_mask = pygame.mask.from_surface(self.img)

        for e in enemies:

            if abs(e.rect.x - self.rect.x) < 100 \
            and abs(e.rect.y - self.rect.y) < 50 and (self.rect.x - e.rect.x)*e.movement > 0:
                e.agg = True
            else:
                e.agg = False

            if e.collision:
                ex, ey = (e.rect.x, e.rect.y)
                eMask = pygame.mask.from_surface(e.img)
                offset = (ex - self.rect.x, ey - self.rect.y)
                if player_mask.overlap_area(eMask, offset):
                    if self.lag == 0:
                        self.health -= e.dmg
                        self.lag = 30

            if self.lag >= 15 and self.lag < 30:
                oline = player_mask.outline()
                s = pygame.Surface((self.rect.width, self.rect.height))
                s.set_colorkey((0, 0, 0))
                s.set_alpha(128)
                pygame.draw.polygon(s, (200, 0, 0), oline, 0)
                win.blit(s, (self.rect.x, self.rect.y))

        if self.lag > 0:
            self.lag -= 1

    def enemyDamage(self, win, enemies):
        player_mask = pygame.mask.from_surface(self.img)

        for e in enemies:
            if e.weaponDamage:
                wMask = pygame.mask.from_surface(e.wImg)
                offset = (e.pos[0] - self.rect.x - e.offset, e.pos[1] - 4 - self.rect.y)

                if player_mask.overlap_area(wMask, offset):
                    if self.lag == 0:
                        self.health -= e.dmg
                        self.lag = 30

            if self.lag >= 15 and self.lag < 30:
                oline = player_mask.outline()
                s = pygame.Surface((self.rect.width, self.rect.height))
                s.set_colorkey((0, 0, 0))
                s.set_alpha(128)
                pygame.draw.polygon(s, (200, 0, 0), oline, 0)
                win.blit(s, (self.rect.x, self.rect.y))

        if self.lag > 0:
            self.lag -= 1

    ### Box functions
    def drawWeaponBox(self, win):
        pygame.draw.circle(
                            win, (0, 0, 255), (self.rect.x + self.rect.width//2,
                            self.rect.y + self.rect.height//2), self.rect.width//2, 1
                            )


class greenBlob(entity):

    def __init__(self, rect, x_vel, y_vel, health, maxHealth,
    tiles = None, img = None, aggImg = None, dmg = 5, collision = True, weaponDamage = False):
        super(greenBlob, self).__init__(rect, x_vel, y_vel, health, maxHealth,
        tiles, img)
        self.dmg = dmg
        self.collision = collision
        self.weaponDamage = weaponDamage
        self.jumpLag = 40
        self.jump = False
        self.movement = 1
        self.images = img
        self.activeImage = img
        self.aggImg = aggImg
        self.agg = True
        self.img = pygame.transform.scale(img[0], (self.rect.width, self.rect.height))

        #Used for movement function
        self.moveIdx = 0
        ind = [-i**2 for i in range(-5, 6)]
        self.movements = [ind[i+1] - ind[i] for i, j in enumerate(ind) if i < 10]

    def update(self, win):
        self.move()
        self.drawEntity(win)
        self.drawHealth(win)

    def move(self):
        if self.collisions['down']:
            if self.jumpLag == 0:
                self.jump = True
            else:
                self.jumpLag -= 1

        if self.agg:
            self.jumpLag = 0

        if self.jump and self.jumpLag == 0:
            self.rect.x += 2*self.movement
            self.checkCollision(self.tiles)
            self.rect.y -= self.movements[self.moveIdx]
            self.checkCollision(self.tiles, pos = 'y')

            self.moveIdx += 1
            if self.moveIdx >= 10:
                self.moveIdx = 0
                self.jump = False
                if self.agg:
                    self.jumpLag = 0
                else:
                    self.jumpLag = 40
                    self.movement *= -1

        else:
            self.rect.y += self.y_vel
            self.checkCollision(self.tiles, pos = 'y')


class skeleton(entity):
    def __init__(self, rect, x_vel, y_vel, health, maxHealth,
    tiles = None, img = None, aggImg = None, dmg = 15, collision = False, weaponDamage = True, weaponImg = None):
        super(skeleton, self).__init__(rect, x_vel, y_vel, health, maxHealth,
        tiles, img)
        self.dmg = dmg
        self.collision = collision
        self.degrees = 360
        self.weaponImg = pygame.transform.rotate(weaponImg, -90)
        self.weaponImgFlipped = pygame.transform.flip(self.weaponImg, True, False)
        self.weaponDamage = weaponDamage
        self.wepDir = -1
        self.movement = 1
        self.img = img[0]
        self.images = img
        self.aggImages = aggImg
        self.activeImages = img
        self.walk = 0
        self.speed = 0
        self.agg = False
        self.aggSpeed = 1.5

    def update(self, win):
        if self.agg:
            self.activeImages = self.aggImages
        else:
            self.activeImages = self.images
        self.imagesFlipped = [pygame.transform.flip(i, True, False) for i in self.activeImages]
        self.move()
        self.drawWeapon(win)
        self.drawEntity(win)
        self.drawHealth(win)

    def drawWeapon(self, win):
        if self.degrees%360 == 300 or self.degrees%360 == 60:
            self.wepDir *= -1
        self.degrees += 10*self.wepDir
        self.loc = (self.rect.x + self.rect.width//2, self.rect.y + self.rect.height//2)
        self.pos = (self.loc[0]+int(math.sin(self.degrees*math.pi/180)*self.rect.width//2),
                    self.loc[1]+int(math.cos(self.degrees*math.pi/180)*self.rect.width//2))

        if self.movement == 1:
            self.wImg = self.weaponImg
            self.offset = 0
        else:
            self.wImg = self.weaponImgFlipped
            self.offset = 15

        win.blit(self.wImg, (self.pos[0] - self.offset, self.pos[1]-self.rect.width//4))
        pygame.draw.circle(
                            win, (255, 255, 255),
                            (self.pos[0], self.pos[1]),
                            2
                            )

    def drawEntity(self, win):
        if self.movement > 0:
            if self.degrees%360 == 60 or self.degrees%360 == 300:
                self.img = self.activeImages[0]
            elif self.degrees%360 == 0:
                self.img = self.activeImages[1]
        else:
            if self.degrees%360 == 60 or self.degrees%360 == 300:
                self.img = self.imagesFlipped[0]
            elif self.degrees%360 == 0:
                self.img = self.imagesFlipped[1]

        win.blit(self.img, (self.rect.x, self.rect.y))

    def move(self):

        self.collisions = {'up': False, 'right': False, 'down': False, 'left': False}

        self.rect.x += self.movement+self.movement*self.agg

        self.checkCollision(self.tiles)

        self.walk += 1
        if self.agg:
            self.walk = 0
        if self.walk == 40 or self.collisions['right'] or self.collisions['left']:
            self.walk = 0
            self.movement *= -1

        self.rect.y += self.y_vel
        self.checkCollision(self.tiles, pos = 'y')

class projectile:
    def __init__(self, x, y, dir_x, dir_y, shootVel = 12, type = "ball", radius = 7, length = 10, img = None):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.type = type
        self.radius = radius
        self.length = length
        self.shootVel = shootVel
        self.img = img

    def draw(self, win):

        if self.img is None:
            pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

        else:
            win.blit(self.img, (self.x, self.y))


class portal:
    def __init__(self, rect, images):
        self.rect = rect
        self.images = images
        self.imageIndex = 0
        self.spawned = False
        self.currentImage = images[self.imageIndex]

    def spawn(self, win):
        win.blit(self.currentImage, (self.rect.x, self.rect.y))

        if self.imageIndex < len(self.images)-1:
            self.imageIndex += 1
        else:
            self.spawned = True

        self.currentImage = self.images[self.imageIndex]


class particle:
    def __init__(self, x, y, x_vel = 0, y_vel = 0, radius = 4, col = (255,255,255), type = "wave", thickness = 4):
        self.x = x
        self.y = y
        self.radius = radius
        self.col = col
        self.type = type
        self.thickness = thickness
        self.x_vel = x_vel
        self.y_vel = y_vel

    def draw(self, win):
        pygame.draw.circle(win, self.col, (int(self.x), int(self.y)), int(self.radius), int(self.thickness))

def read_maps(path, levels):
    maps = {}
    for i in range(levels):
        map = []
        with open(file) as f:
            lines = f.readlines()
        for line in lines:
            map.append([int(i) for i in line.strip().split("  ")])

        maps[levels+1] = map

    return maps

def read_enemies(file):
    enemies = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter = ',')
        for row in reader:
            enemies.append(row)
    return enemies

if __name__ == '__main__':
    pass
