import pygame
import math
import random

class obstacle:
    def __init__(self, x, y, w, h, damage):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.damage = damage

class entity:
    def __init__(self, rect, x_vel, y_vel, health, maxHealth,
    tiles = None, numJumps = 12, jumpSize = 25,
    pos = (0,0), img = None, weaponImg = None, weaponImgFire = None,
    shotImg = None):
        self.rect = rect
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.pos = pos
        self.health = health
        self.maxHealth = maxHealth
        self.numJumps = numJumps
        self.jumpSize = jumpSize
        self.tiles = tiles
        self.img = img
        self.dir = 1
        self.weaponImg = weaponImg
        self.weaponImgFire = weaponImgFire
        self.shotImg = shotImg


        #Variable initialization
        self.movement = 0
        self.jump = False
        self.drop = True
        self.damage = False
        self.jumpLoop = 0
        self.shootLoop = 0
        self.shootSpeed = 20
        self.shots = []
        self.shockWaves = []
        self.shockParticles = []
        self.lag = 10
        self.hangTime = self.jumpSize*2
        self.jumpLoop = 0
        self.jumpDelay = 0
        self.collisions = {'up': False, 'right': False, 'down': False, 'left': False}
        self.img = pygame.transform.scale(self.img, (self.rect.width, self.rect.height))

        if self.img is not None:
            self.img.set_colorkey((0, 0, 0))
            self.img_flipped = pygame.transform.flip(self.img, True, False)
            self.img_flipped.set_colorkey((0, 0, 0))

        if self.weaponImgFire is not None:
            self.weaponImgFire.set_colorkey((0, 0, 0))

        if self.weaponImg is not None:
            self.weaponImg.set_colorkey((0, 0, 0))

    def update(self, pos, win, mouseClicked, blockSize, screenSize, explosion, e_masks, e_coords, final_level):

        self.pos = pos
        mask1 = pygame.mask.from_surface(self.img)

        self.move(screenSize, final_level)
        self.drawEntity(win)
        self.drawHealth(win)
        self.drawWeapon(win, mouseClicked, True)
        self.drawCrossHair(win)


        for i, e_mask in enumerate(e_masks):
            ec = e_coords[i]
            offset = (ec[0] - self.rect.x, ec[1] - self.rect.y)
            if mask1.overlap_area(e_mask, offset):
                if self.lag == 0:
                    self.health -= 1
                    self.lag = 10

        if self.lag > 0:
            self.lag -= 1


    def drawHitBoxes(self, win):
        pygame.draw.rect(win, (255, 0, 0), self.rect, 2)

    def drawWeaponBox(self, win):
        pygame.draw.circle(
                            win, (0, 0, 255), (self.rect.x + self.rect.width//2,
                            self.rect.y + self.rect.height//2), self.rect.width//2, 1
                            )

    def drawWeapon(self, win, mouseClicked, show = False):
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

                win.blit(self.weaponImgFire, (self.shotLoc[0]-8, self.shotLoc[1]-24))

            else:
                self.weaponImg.set_colorkey((0, 0, 0))
                win.blit(self.weaponImg, (self.shotLoc[0]-8, self.shotLoc[1]-24))

        if show:
            pygame.draw.circle(
                                win, (255, 183, 183),
                                (int(self.shotLoc[0]), int(self.shotLoc[1])),
                                4
                                )

    def drawHealth(self, win):
        pygame.draw.rect(win, (200, 0, 0), (self.rect.x, self.rect.y - 10, self.rect.width, 5))
        if self.health > 0:
            pygame.draw.rect(
                    win, (0, 200, 0),
                    (self.rect.x, self.rect.y - 10, self.rect.width*self.health/self.maxHealth, 5))


    def drawEntity(self, win):
        if self.img is not None:
            if self.pos[0] > self.rect.x + self.rect.width//2:
                win.blit(self.img, (self.rect.x, self.rect.y))

            else:
                win.blit(self.img_flipped, (self.rect.x, self.rect.y))

    def checkCollision(self, tiles):
        for t in tiles:
            if self.rect.colliderect(t['rect']):
                if self.movement > 0:
                    self.rect.right = t['rect'].left
                    self.collisions['right'] = True

                elif self.movement < 0:
                    self.rect.left = t['rect'].right
                    self.collisions['left'] = True

                elif t['rect'].y > self.rect.y:
                    self.rect.bottom = t['rect'].top
                    self.collisions['down'] = True

                else:
                    self.rect.bottom = t['rect'].top
                    self.collisions['top'] = True

    def enemyCollision(self, enemies):
        for id, enemy in enemies.items():
            return self.rect.colliderect(enemy.rect)

    def projectileCollision(self, projectiles):
        pass

    def updateShots(self, screen, mouseClicked, BLOCK_SIZE, SCREEN_SIZE, explosion):
        if mouseClicked and self.shootLoop == 0:
            self.shots.append(projectile(self.shotLoc[0], self.shotLoc[1], self.shotDir[0], self.shotDir[1], img = self.shotImg))
            self.shootLoop = self.shootSpeed

        for shot in self.shots:
            for i in range(shot.shootVel):
                shot.x += shot.dir_x
                shot.y += shot.dir_y
                for obj in self.tiles:
                    rect = pygame.Rect(obj[0][0], obj[0][1], BLOCK_SIZE, BLOCK_SIZE)
                    if (shot.x + shot.radius <= 0) \
                    or (shot.x + shot.radius >= SCREEN_SIZE) \
                    or (shot.y + shot.radius <= 0) \
                    or (shot.y + shot.radius >= SCREEN_SIZE):
                        shot.draw(screen)
                        self.shots.remove(shot)
                        break

                    elif (collision(shot, rect, "circle", "rect")):
                        if explosion:
                            self.shockWaves.append(particle(shot.x, shot.y, radius = shot.radius))
                            for _ in range(random.randint(20, 40)):
                                colInt = int(random.randint(20, 30)/10*60)
                                self.shockParticles.append(
                                                particle(
                                                        shot.x, shot.y,
                                                        x_vel = random.randint(-40, 50)/10 - 1,
                                                        y_vel = random.randint(-2, 2),
                                                        radius = random.randint(5, 30),
                                                        col = (colInt,colInt,colInt), thickness = 0))
                        shot.draw(screen)
                        self.shots.remove(shot)
                        break

                else:
                    continue
                break

        for shot in self.shots:
            shot.draw(screen)

        index = 0
        indices = []
        for wave in self.shockWaves:
            wave.thickness -= 0.05
            wave.radius += 2
            wave.draw(screen)

            if wave.radius > 50:
                indices.append(index)

            index += 1

        indices.sort(reverse = True)
        for i in indices:
            del self.shockWaves[i]

        index = 0
        indices = []
        for part in self.shockParticles:
            part.draw(screen)
            part.radius -= 1
            part.x += part.x_vel
            part.y += part.y_vel
            if part.radius <= 0:
                indices.append(index)

            index += 1

        indices.sort(reverse = True)
        for i in indices:
            del self.shockParticles[i]

        if self.shootLoop > 0:
            self.shootLoop -= 1

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

        if self.drop:
            self.rect.y += self.y_vel

        #Y-collision check
        self.checkCollision(self.tiles)

        #Handle jump and drop

        if key[pygame.K_SPACE] and self.collisions['down']:
            self.jump = True
            self.drop = False

        if self.jump:
            self.rect.y -= self.jumpSize

        if self.numJumps == 0:
            self.drop = True
            self.jump = False
            self.numJumps = 12

        self.numJumps -= 1


    def drawCrossHair(self, screen):
        pygame.draw.line(screen, (150, 150, 150), [self.pos[0] - 10, self.pos[1]], [self.pos[0] + 10, self.pos[1]],  1)
        pygame.draw.line(screen, (150, 150, 150), [self.pos[0], self.pos[1] - 10], [self.pos[0], self.pos[1] + 10],  1)
        pygame.mouse.set_visible(False)

class player(entity):
    pass


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

        if self.img is not None:
            self.img.set_colorkey((0,0,0))

    def draw(self, win):

        if self.img is None:
            pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

        else:
            win.blit(self.img, (self.x-self.radius, self.y-self.radius))


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

def collision(obj_x, obj_y, type_x, type_y):
    if type_x == "circle":
        if type_y == "rect":
            radius_x = obj_x.radius
            pos_x = [obj_x.x, obj_x.y]

            pos_y = [obj_y.x, obj_y.y]
            wy = obj_y.w
            hy = obj_y.h

            testX = pos_x[0]
            testY = pos_x[1]

            if pos_x[0] < pos_y[0]:
                testX = pos_y[0]
            elif pos_x[0] > pos_y[0] + wy:
                testX = pos_y[0] + wy

            if pos_x[1] < pos_y[1]:
                testY = pos_y[1]
            elif pos_x[1] > pos_y[1] + hy:
                testY = pos_y[1] + hy

            distX = pos_x[0] - testX
            distY = pos_x[1] - testY
            distance = math.sqrt((distX**2.0) + (distY**2.0))

            if distance <= obj_x.radius:
                return True

    return False

class greenBlob(entity):

    def update(self, win, blockSize, screenSize):

        self.move(blockSize, screenSize)
        self.drawEntity(win)
        self.drawHealth(win)

    def move(self, BLOCK_SIZE, SCREEN_SIZE):

        if self.collisions['down']:
            if self.jumpDelay == 0:
                self.dir = random.choice([-1, 1])
                self.jump = True
                self.jumpDelay = 75
                self.sideWays = True
                self.hangTime = 0

        if self.jumpDelay > 0:
            self.jumpDelay -= 1

        if (self.jump or self.drop) and self.hangTime < self.jumpSize*2:
            if not self.collisions['right'] and self.rect.x + self.rect.width < SCREEN_SIZE and self.dir > 0:
                self.rect.x += self.x_vel

            if not self.collisions['left'] and self.rect.x > 0 and self.dir < 0:
                self.rect.x -= self.x_vel

        #Manage jump
        if self.jump:
            if not self.collisions['up']:
                self.rect.y -= 1
            else:
                self.jumpLoop = 0
                self.jump = False
                self.drop = True

            if self.jumpLoop > 0:
                self.jumpLoop -= 1

            if self.jumpLoop <= 0:
                self.jump = False
                self.drop = True
                self.jumpLoop = self.numJumps

        # If not jumping and no downwards collision, then drop
        else:
            self.drop = True
            if not self.collisions['down']:
                self.rect.y += 1
            else:
                self.jump = False
                self.drop = False

        #Increment hangtime
        self.hangTime += 1

        self.checkCollision(self.tiles)

    def drawEntity(self, win):
        if self.img is not None:
            win.blit(self.img, (self.rect.x, self.rect.y))


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

if __name__ == '__main__':
    pass
