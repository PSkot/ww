import pygame
import math
import os

width = 800
height = 800
FPS = 20

clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))

run = True

path = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir))

rope = pygame.image.load(path + '/images/rope.png')
ball = pygame.image.load(path + '/images/ball.png')
bolt = pygame.image.load(path + '/images/bolt.png')

def rot_center(image, rect, angle):
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center = rect.center)
    return rot_image, rot_rect

class pendulum:
    def __init__(self, pivot, length, amp_zero, gravity, rope, ball, bolt):
        self.pivot = pivot
        self.length = length
        self.amp_zero = amp_zero
        self.gravity = gravity
        self.line_start = (self.pivot[0]-1, self.pivot[1])
        self.rope = rope
        self.ball = ball
        self.bolt = bolt
        self.t = 1
        self.vel = 0

        T0 = 2*math.pi*math.sqrt(length/gravity)
        self.T = -T0*(math.log(math.cos(amp_zero/2))/(1-math.cos(amp_zero/2)))

    def update(self, win):
        self.amp = self.amp_zero*math.cos(2*math.pi/self.T*self.t)
        self.line_end = (int(self.line_start[0]+math.sin(self.amp)*self.length), int(self.line_start[1]+math.cos(self.amp)*self.length))
        self.new_rope = pygame.transform.rotate(self.rope, math.degrees(self.amp))

        self.vel += (-1*self.gravity/self.length*math.sin(self.amp))

        if self.t >= self.T:
            self.t = 0
        self.t += 1

        if self.amp < 0:
            self.offset = self.new_rope.get_rect().topright[0] - self.rope.get_width()
        else:
            self.offset = 0

        self.draw(win)

    def draw(self, win):
        win.blit(self.new_rope, (self.line_start[0] - self.offset, self.line_start[1]))
        win.blit(self.ball, (self.line_end[0] - self.ball.get_width()//2, self.line_end[1] - self.ball.get_height()//2))
        win.blit(self.bolt, (self.line_start[0] - self.bolt.get_width()//2, self.line_start[1] - self.bolt.get_height()//2))

        # Later for collision
        # pygame.draw.circle(win, (0, 0, 200), self.line_end, self.ball.get_width()//2, 1)

obst = pendulum((250, 150), rope.get_height(), 1.5, 3, rope, ball, bolt)

while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill((150, 0, 0))
    obst.update(screen)

    pygame.display.update()
