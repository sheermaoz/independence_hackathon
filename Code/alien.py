import pygame


class Alien(pygame.sprite.Sprite):
    def __init__(self,color,x,y):
        super().__init__()
        file_path = 'Resources/' + color + '.png'
        self.image0 = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image0, (30, 22.5))
        self.rect = self.image.get_rect(topleft = (x,y))

        if color == 'red': self.value = 100
        elif color == 'green': self.value = 200
        elif color == 'yellow': self.value = 300

        self.now = 0

    def update(self,direction):
        if pygame.time.get_ticks() > self.now + 20:
            self.rect.x += direction
            self.now = pygame.time.get_ticks()



class Extra(pygame.sprite.Sprite):
    def __init__(self,side,window_width, height):
        super().__init__()
        self.image0 = pygame.image.load('Resources/extra.png').convert_alpha()
        self.image = pygame.transform.scale(self.image0, (30 / 1, 18 / 1))

        if side == 'right':
            x = window_width - 50
            self.speed = -3
        else:
            x = 0
            self.speed = 3
        y = height

        self.rect = self.image.get_rect(topleft=(x,y))
        self.vw = 0

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < self.vw:
            self.kill()
