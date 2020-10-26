import pygame
import math
import random


class entity:
    def __init__(self, x, y, w, h, x_vel, y_vel, health, maxHealth,
    objectCoords = None, numJumps = 6, jumpSize = 50, shots = [], shockWaves = [],
    shockParticles = [], pos = (0,0), type = 'player', img = None, weaponImg = None,
    weaponImgFire = None, enemy_id = None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.pos = pos
        self.type = type
        self.health = health
        self.maxHealth = maxHealth
        self.shots = shots
        self.shockWaves = shockWaves
        self.shockParticles = shockParticles
        self.shootLoop = 10
        self.jump = False
        self.drop = False
        self.damage = False
        self.numJumps = numJumps
        self.jumpSize = jumpSize
        self.jumpLoop = 0
        self.objectCoords = objectCoords
        self.img = img
        self.weaponImg = weaponImg
        self.weaponImgFire = weaponImgFire

        if self.img is not None:
            self.img.set_colorkey((0, 0, 0))
            self.img_flipped = pygame.transform.flip(self.img, True, False)
            self.img_flipped.set_colorkey((0, 0, 0))

        if self.weaponImgFire is not None:
            self.weaponImgFire.set_colorkey((0, 0, 0))

        if self.weaponImg is not None:
            self.weaponImg.set_colorkey((0, 0, 0))


        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

        dist = [self.pos[0] - self.x, self.pos[1] - self.y]
        norm = math.sqrt(dist[0] ** 2.0 + dist[1] ** 2.0)
        self.dir = [dist[0] / norm, dist[1] / norm]
        self.shotLoc = [int(self.dir[0]*self.w//2 + self.x + self.w//2), int(self.dir[1]*self.w//2 + self.y + self.h//2)]

    def update(self, pos, win, mouseClicked, blockSize, screenSize, explosion, final_level):
        self.pos = pos
        self.upCollision = False
        self.downCollision = False
        self.rightCollision = False
        self.leftCollision = False

        self.move(blockSize, screenSize, final_level)
        self.manageJump(blockSize)
        self.drawEntity(win)
        #self.drawHitBoxes(win)
        self.drawHealth(win)
        #self.drawWeaponBox(win)
        self.drawWeaponLocation(win, mouseClicked, True)
        self.drawCrossHair(win)
        self.updateShots(win, mouseClicked, blockSize, screenSize, explosion)


    def drawHitBoxes(self, win):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(win, (255, 0, 0), self.rect, 2)

    def drawWeaponBox(self, win):
        pygame.draw.circle(win, (0, 0, 255), (self.x + self.w//2, self.y + self.h//2), self.w//2, 1)

    def drawWeaponLocation(self, win, mouseClicked, show = False):
        weaponTimer = 0
        dist = [self.pos[0] - self.x - self.w // 2, self.pos[1] - self.y - self.h//2]
        norm = math.sqrt(dist[0] ** 2.0 + dist[1] ** 2.0)
        if norm != 0:
            self.dir = [dist[0] / norm, dist[1] / norm]
        self.shotLoc = [int(self.dir[0]*self.w//2 + self.x + self.w//2), int(self.dir[1]*self.w//2 + self.y + self.h//2)]


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
        pygame.draw.rect(win, (200, 0, 0), (self.x, self.y - 10, self.w, 5))
        if self.health > 0:
            pygame.draw.rect(win, (0, 200, 0), (self.x, self.y - 10, self.w*self.health/self.maxHealth, 5))


    def drawEntity(self, win):
        if self.img is not None:
            if self.type == 'player':
                if self.pos[0] > self.x + self.w//2:
                    win.blit(self.img, (self.x, self.y))

                else:
                    win.blit(self.img_flipped, (self.x, self.y))

            else:
                win.blit(self.img, (self.x, self.y))

    def checkCollision(self, objectCoords, blockSize):

        collLeft, collRight, collUp, collDown = [False]*4

        if self.x == objectCoords[0] + blockSize and self.y < objectCoords[1] + blockSize and self.y + self.h > objectCoords[1]:
            self.leftCollision = True
            collLeft = True

        if self.x + self.w == objectCoords[0] and self.y < objectCoords[1] + blockSize and self.y + self.h > objectCoords[1]:
            self.rightCollision = True
            collRight = True

        if self.y == objectCoords[1] + blockSize and self.x < objectCoords[0] + blockSize and self.x + self.w > objectCoords[0]:
            self.upCollision = True
            collUp = True

        if self.y + self.h == objectCoords[1] and self.x < objectCoords[0] + blockSize and self.x + self.w > objectCoords[0]:
            self.downCollision = True
            collDown = True

        return collLeft, collRight, collUp, collDown

    def enemyCollision(self, enemies):
        for id, enemy in enemies.items():
            return self.rect.colliderect(enemy.rect)

    def projetileCollision(self, projectiles):
        pass

    def updateShots(self, screen, mouseClicked, BLOCK_SIZE, SCREEN_SIZE, explosion):
        if mouseClicked and self.shootLoop == 0:
            self.shots.append(projectile(self.shotLoc[0], self.shotLoc[1], self.dir[0], self.dir[1]))
            self.shootLoop = 10

        for shot in self.shots:
            for i in range(shot.shootVel):
                shot.x += shot.dir_x
                shot.y += shot.dir_y
                for obj in self.objectCoords:
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

    def move(self, BLOCK_SIZE, SCREEN_SIZE, final_level):
        key = pygame.key.get_pressed()

        for j in self.objectCoords:
            self.checkCollision(j[0], BLOCK_SIZE)

        if key[pygame.K_SPACE] and self.downCollision:
            self.jump = True

        if key[pygame.K_d] and not self.rightCollision:
            if final_level and self.x + self.w >= SCREEN_SIZE:
                pass
            else:
                for i in range(self.x_vel):
                    for j in self.objectCoords:
                        self.checkCollision(j[0], BLOCK_SIZE)

                    if not self.rightCollision and (self.drop or self.jump or self.downCollision):
                        self.x += 1


        if key[pygame.K_a] and not self.leftCollision and self.x > 0:
            for i in range(self.x_vel):
                for j in self.objectCoords:
                    self.checkCollision(j[0], BLOCK_SIZE)
                if not self.leftCollision and (self.drop or self.jump or self.downCollision):
                    self.x -= 1


    def drawCrossHair(self, screen):
        pygame.draw.line(screen, (150, 150, 150), [self.pos[0] - 10, self.pos[1]], [self.pos[0] + 10, self.pos[1]],  1)
        pygame.draw.line(screen, (150, 150, 150), [self.pos[0], self.pos[1] - 10], [self.pos[0], self.pos[1] + 10],  1)
        pygame.mouse.set_visible(False)

    def manageJump(self, BLOCK_SIZE):
        # Check if character is jumping and handle jump
        if self.jump:
            for _ in range(self.jumpSize):
                for j in self.objectCoords:
                    l, r, u, d = self.checkCollision(j[0], BLOCK_SIZE)
                    if u and j[1] == 3: #Check collision by block type
                        self.damage = True

                if not self.upCollision:
                    self.y -= 1
                else:
                    if self.damage:
                        self.health -= 1
                        self.damage = not self.damage
                    self.jumpLoop = 0
                    self.jump = False
                    self.drop = True
                    break

            if self.jumpLoop > 0:
                self.jumpLoop -= 1

            if self.jumpLoop <= 0:
                self.jump = False
                self.drop = True
                self.jumpLoop = self.numJumps

        # If not jumping and no downwards collision, then drop
        else:
            self.drop = True
            for i in range(self.y_vel):
                for j in self.objectCoords:
                    self.checkCollision(j[0], BLOCK_SIZE)
                if not self.downCollision:
                    self.y += 1
                else:
                    self.jump = False
                    self.drop = False


class projectile:
    def __init__(self, x, y, dir_x, dir_y, shootVel = 12, type = "ball", radius = 4, length = 10):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.type = type
        self.radius = radius
        self.length = length
        self.shootVel = shootVel


    def draw(self, win):
        pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

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

if __name__ == '__main__':
    pass
