import pygame, sys
from player import Player, GameState
import cv2
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser


class Game:
    def __init__(self):
        self.player_sprite = \
            Player(((video_width + (screen_width / 2)), screen_height*0.9), screen_width, 5, video_width, screen, window_height)
        self.player = pygame.sprite.GroupSingle(self.player_sprite)
        self.setup_game()
    
    
    def setup_game(self):
        # health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load('Resources/player.png').convert_alpha()
        self.score = 0
        self.font = pygame.font.Font('Resources/Pixeled.ttf', 14)
        self.small_font = pygame.font.Font('Resources/Pixeled.ttf', 7)

        # obstacle setup
        self.shape = None
        self.block_size = 3
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 6
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=video_width + (screen_width/15), y_start=screen_height/2-30)

        # alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows=9, cols=10)
        self.alien_direction = 1

        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(100,200)

        # Audio
        self.laser_sound = pygame.mixer.Sound('Resources/laser.wav')
        self.laser_sound.set_volume(0.01)
        self.explosion_sound = pygame.mixer.Sound('Resources/explosion.wav')
        self.explosion_sound.set_volume(0.01)

    def reset_game(self):
        self.setup_game()
        self.player_sprite.game_state = GameState.RUNNING
        self.player_sprite.game_started = True

    def create_obstacle(self, x_start, y_start, offset_x):
        self.shape = obstacle.shape

        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance=50, y_distance=20, x_offset=70, y_offset=50):
        x_offset = x_offset + video_width
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset
                if row_index  < 3:
                    alien_sprite = Alien('yellow', x, y)
                elif 3 <= row_index <= 5:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)


                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= window_width:
                self.alien_direction = -1
                self.alien_move_down(6)
                break
            elif alien.rect.left <= video_width:
                self.alien_direction = 1
                self.alien_move_down(6)
                break

    def alien_move_down(self,distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center,6,screen_height, 'red')
            self.alien_lasers.add(laser_sprite)

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right','left']),window_width, video_width))
            self.extra_spawn_time = randint(400,800)

    def collision_checks(self):
        # player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                # extra collisions
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += 500
                    laser.kill()
                    self.explosion_sound.play()

        # alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.player_sprite.game_state = GameState.LOSE
                        self.player_sprite.game_started = False
                    self.explosion_sound.play()

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        life_surf = self.font.render('Lives:', False, 'white')
        life_rect = life_surf.get_rect(topleft = (10,100))
        screen.blit(life_surf, life_rect)
        for live in range(self.lives - 1):
            x = 100 + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf,(x,100))

    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft = (10,130))
        screen.blit(score_surf, score_rect)

    def display_in_scope(self):
        scope_surf = self.font.render('Hands out of camera scope!', False, 'red')
        scope_rect = scope_surf.get_rect(topleft = (10,160))

        if not self.player_sprite.in_scope:
            screen.blit(scope_surf, scope_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You won', False, 'white')
            victory_rect = victory_surf.get_rect(center=((window_width/2) + (video_width/2), (screen_height / 2)-150))
            screen.blit(victory_surf, victory_rect)

            start_surf = self.font.render('Click to restart', False, 'white')
            start_rect = start_surf.get_rect(center=((window_width / 2) + (video_width / 2), (screen_height / 2) + 150))
            screen.blit(start_surf, start_rect)

            self.player_sprite.game_state = GameState.WIN
            self.player_sprite.game_started = False
            for laser in self.alien_lasers:
                laser.kill()
            for laser in self.player_sprite.lasers:
                laser.kill()
            for extra in self.extra:
                extra.kill()

    def start_message(self):
        start_surf = self.font.render('Click to start the game', False, 'white')
        start_rect = start_surf.get_rect(center=((window_width/2) + (video_width/2), (screen_height / 2)-50))
        screen.blit(start_surf, start_rect)

    def death_message(self):
        dead_surf = self.font.render('You died!', False, 'white')
        dead_rect = dead_surf.get_rect(center=((window_width/2) + (video_width/2), (screen_height / 2)-50))
        screen.blit(dead_surf, dead_rect)

        start_surf = self.font.render('Click to restart', False, 'white')
        start_rect = start_surf.get_rect(center=((window_width/2) + (video_width/2), (screen_height / 2)+50))
        screen.blit(start_surf, start_rect)

    def run(self):

        self.player.update()
        if self.player_sprite.game_state == GameState.IDLE:
            self.start_message()
            return
        if self.player_sprite.game_state == GameState.LOSE:
            self.death_message()
            return
        if self.player_sprite.game_state == GameState.RESTART:
            self.reset_game()
            return

        self.aliens.update(self.alien_direction)
        self.alien_position_checker()
        self.alien_lasers.update()
        self.extra_alien_timer()
        self.extra.update()
        self.collision_checks()
        self.display_lives()

        self.player.sprite.lasers.draw(screen)
        # self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.display_in_scope()

        self.victory_message()


def start_game():
    game = Game()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    video_capture = cv2.VideoCapture(0)  # 0 represents the default camera
    video_capture.set(3, 1920)
    video_capture.set(4, 1080)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER and game.player_sprite.game_state == GameState.RUNNING:
                game.alien_shoot()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.player_sprite.game_state == GameState.IDLE:
                    game.player_sprite.game_state = GameState.RUNNING
                    game.player_sprite.game_started = True
                elif game.player_sprite.game_state in [GameState.LOSE, GameState.WIN] :
                    game.player_sprite.game_state = GameState.RESTART

        # Convert the frame from BGR to RGB for PyGame
        img = game.player_sprite.img
        img = cv2.flip(img, 1)

        try:
            frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.rotate(frame_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotate the frame
            frame_rgb = pygame.surfarray.make_surface(frame_rgb)

            # Scale the video frame to fit the specified dimensions
            frame_scaled = pygame.transform.scale(frame_rgb, (video_width, video_height))

            # Clear the PyGame window and blit the video frame
            screen.fill((0, 0, 0))
            screen.fill((50, 50, 50), (0, 0, video_width, screen.get_height()))
            screen.blit(frame_scaled, (video_pos_x, video_pos_y))
        except:
            print("First game loop (image not initialized)")

        game.run()
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    screen_width = 600
    screen_height = 700

    video_width = 213 * 1.7
    video_height = 120 * 1.7

    window_width = screen_width + video_width
    window_height = screen_height

    video_pos_x = 0
    video_pos_y = screen_height - video_height

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Gesture-Controlled Space Invaders+")

    clock = pygame.time.Clock()

    start_game()
