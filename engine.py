import pygame
import math
import random
BLOCK_SIZE = 25
SCREEN_SIZE = 500
explosion = True


class entity:
    def __init__(self, x, y, w, h, x_vel, y_vel, health, maxHealth, shots = [], shockWaves = [],
    shockParticles = [], pos = (0,0), type = 'player', enemy_id = None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.pos = pos
        self.health = health
        self.maxHealth = maxHealth
        self.shots = shots
        self.shockWaves = shockWaves
        self.shockParticles = shockParticles
        self.shootLoop = 10

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

        dist = [self.pos[0] - self.x, self.pos[1] - self.y]
        norm = math.sqrt(dist[0] ** 2.0 + dist[1] ** 2.0)
        self.dir = [dist[0] / norm, dist[1] / norm]
        self.shotLoc = [int(self.dir[0]*self.w//2 + self.x + self.w//2), int(self.dir[1]*self.w//2 + self.y + self.h//2)]

    def update(self, pos):
        self.pos = pos
        self.upCollision = False
        self.downCollision = False
        self.rightCollision = False
        self.leftCollision = False

    def drawHitBoxes(self, win):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(win, (255, 0, 0), self.rect, 2)

    def drawWeaponBox(self, win):
        pygame.draw.circle(win, (0, 0, 255), (self.x + self.w//2, self.y + self.h//2), self.w//2, 1)

    def drawWeaponLocation(self, win):
        dist = [self.pos[0] - self.x - self.w // 2, self.pos[1] - self.y - self.h//2]
        norm = math.sqrt(dist[0] ** 2.0 + dist[1] ** 2.0)
        if norm != 0:
            self.dir = [dist[0] / norm, dist[1] / norm]
        self.shotLoc = [int(self.dir[0]*self.w//2 + self.x + self.w//2), int(self.dir[1]*self.w//2 + self.y + self.h//2)]

        pygame.draw.circle(
                            win, (0, 255, 0),
                            (int(self.shotLoc[0]), int(self.shotLoc[1])),
                            3
                            )

    def drawHealth(self, win):
        pygame.draw.rect(win, (200, 0, 0), (self.x, self.y - 10, self.w, 5))
        if self.health > 0:
            pygame.draw.rect(win, (0, 200, 0), (self.x, self.y - 10, self.w*self.health/self.maxHealth, 5))


    def drawEntity(self, win, img):
        img = pygame.scale.transform(img, (self.w, self.h))
        win.blit(img, self.x, self.y)

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

    def updateShots(self, screen, objectCoords, mouseClicked):
        if mouseClicked and self.shootLoop == 0:
            self.shots.append(projectile(self.shotLoc[0], self.shotLoc[1], self.dir[0], self.dir[1]))
            self.shootLoop = 10

        for shot in self.shots:
            for i in range(shot.shootVel):
                shot.x += shot.dir_x
                shot.y += shot.dir_y
                for obj in objectCoords:
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

    def manageJump(self):
        # Check if character is jumping and handle jump
        if jump:
            for _ in range(jumpSize):
                for j in objectCoords:
                    l, r, u, d = main_char.checkCollision(j[0], BLOCK_SIZE)
                    if u and j[1] == 3: #Check collision by block type
                        damage = True

                if not main_char.upCollision:
                    main_char.y -= 1
                else:
                    if damage:
                        main_char.health -= 1
                        damage = not damage
                    jumpLoop = 0
                    jump = False
                    drop = True
                    break

            if jumpLoop > 0:
                jumpLoop -= 1

            if jumpLoop <= 0:
                jump = False
                drop = True
                jumpLoop = numJumps

        # If not jumping and no downwards collision, then drop
        else:
            drop = True
            for i in range(main_char.y_vel):
                for j in objectCoords:
                    main_char.checkCollision(j[0], BLOCK_SIZE)
                if not main_char.downCollision:
                    main_char.y += 1
                else:
                    jump = False
                    drop = False


class projectile:
    def __init__(self, x, y, dir_x, dir_y, shootVel = 6, type = "ball", radius = 4, length = 10):
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
