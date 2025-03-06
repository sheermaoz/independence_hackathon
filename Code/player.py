import pygame
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from laser import Laser

from enum import Enum

class GameState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WIN = "win"
    LOSE = "lose"
    RESTART = "restart"


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, cwidth, speed, vwidth, screen, height):
        super().__init__()
        self.image0 = pygame.image.load('Resources/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image0, (30 / 1, 15 / 1))
        self.rect = self.image.get_rect(midtop=pos)

        self.speed = speed
        self.max_x_constraint = cwidth + vwidth
        self.ready_to_shoot = False
        self.laser_time = 0
        self.laser_cooldown = 600

        self.lasers = pygame.sprite.Group()

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)
        self.vwidth = vwidth

        self.fingers = None
        self.img = None
        self.in_scope = False
        self.game_started = False

        self.screen = screen
        self.ww = cwidth + vwidth
        self.wh = height

        self.laser_sound = pygame.mixer.Sound('Resources/laser.wav')
        self.laser_sound.set_volume(0.01)

        self.game_state = GameState.IDLE

    def constraint(self):
        if self.rect.left <= self.vwidth:
            self.rect.left = self.vwidth
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, -25, 700, 'lightblue'))

    def read_fingers(self):
        _, img = self.cap.read()
        img = cv2.flip(img, 1)

        # Find hand and its landmarks
        # self.feet = self.detector.findFeet(img, draw=False)
        # self.img = img
        # if self.feet:
        #     foot = self.feet[0]
        #     x, y, w, h = foot['bbox']
        #     x1 = x + w // 2
        #     x1 = np.clip(x1, 100, 1150)

        #     map = x1 - 100
        #     map = map * (self.max_x_constraint - self.vwidth)
        #     map = map // 1150
        #     self.rect.x = map + self.vwidth
        #     self.rect.y = y + h


        #     cv2.rectangle(img, (x - 20, y - 20),
        #                     (x + w + 20, y + h + 20),
        #                     (200, 0, 0), 10)
        #     return True
        
        self.hands = self.detector.findHands(img, draw=False, flipType=True)
        self.img = img
        if self.hands:
            hand = self.hands[0]
            
            x, y, w, h = hand['bbox']
            x1 = x + w // 2
            x1 = np.clip(x1, 100, 1150)
            y1 = y + h
            y1 = np.clip(y1, 350, 650)

            map = x1 - 100
            map = map * (self.max_x_constraint - self.vwidth)
            map = map // 1150
            self.rect.x = map + self.vwidth
            self.rect.y = y1


            cv2.rectangle(img, (x - 20, y - 20),
                            (x + w + 20, y + h + 20),
                            (200, 0, 0), 10)
            return True
        return False

    def get_input(self):
        if self.ready_to_shoot:
            self.laser_sound.play()
            self.shoot_laser()
            self.ready_to_shoot = False
            self.laser_time = pygame.time.get_ticks()

    def recharge_shoot(self):
        if not self.ready_to_shoot and self.game_started:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready_to_shoot = True

    def recharge_flip(self):
        if not self.ready_to_flip:
            current_time = pygame.time.get_ticks()
            if current_time - self.flip_time >= self.flip_cooldown and self.fingers != [0,0,0,0,1]:
                self.ready_to_flip = True

    def update(self):
        if self.read_fingers():
            self.in_scope = True

        else: self.in_scope = False

        try:
            self.constraint()
            self.lasers.update()
            self.get_input()
        except:
            pass

        self.recharge_shoot()

      
        self.screen.blit(self.image, self.rect)


    def get_image(self):
        return self.img