import pygame
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from laser import Laser

from enum import Enum

color_mode = True

class GameState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WIN = "win"
    LOSE = "lose"
    RESTART = "restart"


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, cwidth, speed, screen, height):
        super().__init__()
        self.image0 = pygame.image.load('Resources/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image0, (30 / 1, 15 / 1))
        self.rect = self.image.get_rect(midtop=pos)

        global color_mode
        self.color_mode = color_mode

        self.speed = speed
        self.max_x_constraint = cwidth
        self.ready_to_shoot = False
        self.laser_time = 0
        self.laser_cooldown = 600

        self.lasers = pygame.sprite.Group()

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)
        self.vwidth = 0

        self.fingers = None
        self.img = None
        self.in_scope = False
        self.game_started = False

        self.screen = screen
        self.ww = cwidth
        self.wh = height

        self.laser_sound = pygame.mixer.Sound('Resources/laser.wav')
        self.laser_sound.set_volume(0.01)

        self.game_state = GameState.IDLE

        self.previous_center_x = None
        self.previous_center_y = None
        self.stabilization_threshold = 200  # Threshold for stabilization



    def constraint(self):
        if self.rect.left <= self.vwidth:
            self.rect.left = self.vwidth
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, -25, 'lightblue'))

    def read_fingers(self):
        _, img = self.cap.read()
        img = cv2.flip(img, 1)
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotate the frame
        
        self.hands = self.detector.findHands(img, draw=False, flipType=True)
        self.img = img
        if self.hands:
            hand = self.hands[0]
            
            x, y, w, h = hand['bbox']
            x1 = x + w // 2
            x1 = np.clip(x1, 0, self.ww - 100)
            y1 = y + h
            y1 = np.clip(y1, self.wh/2, self.wh - 30)

            map = x1 - 100
            map = map * (self.max_x_constraint - self.vwidth)
            map = map // (self.ww / 1.9)
            self.rect.x = map + self.vwidth
            self.rect.y = y1


            cv2.rectangle(img, (x - 20, y - 20),
                            (x + w + 20, y + h + 20),
                            (200, 0, 0), 10)
            return True
        return False

    def read_color(self):
        _, img = self.cap.read()
        img = cv2.flip(img, 1)
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotate the frame
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Detect green color
        self.lower_color = np.array([39, 68, 80])
        self.upper_color = np.array([93, 161, 255])
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)  # Apply Gaussian blur to reduce noise
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        self.img = img
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 500:  # Filter out small contours
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])

                    # Stabilize the movement
                    if self.previous_center_x is not None and self.previous_center_y is not None:
                        if abs(center_x - self.previous_center_x) > self.stabilization_threshold or abs(center_y - self.previous_center_y) > self.stabilization_threshold:
                            center_x = self.previous_center_x
                            center_y = self.previous_center_y

                    self.previous_center_x = center_x
                    self.previous_center_y = center_y

                    center_x = np.clip(center_x, 0, self.ww - 100)
                    center_y = np.clip(center_y, 0, self.wh - 30)


                            # Ensure center_x and center_y are integers
                    center_x = int(center_x)
                    center_y = int(center_y)
                    map_x = center_x - 100
                    map_x = map_x * (self.max_x_constraint - self.vwidth)
                    map_x = map_x // 1150
                    self.rect.x = map_x + self.vwidth
                    y = center_y
                    self.rect.y = np.clip(y, self.wh/2, self.wh - 70)

                    cv2.circle(img, (center_x, center_y), 50, (0, 0, 255), 8)
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
        if (self.color_mode):
            if self.read_color():
                self.in_scope = True
            else:
                self.in_scope = False
        else:
            if self.read_fingers():
                self.in_scope = True
            else:
                self.in_scope = False

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