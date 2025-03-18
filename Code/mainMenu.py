import pygame
import sys

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font('Resources/Pixeled.ttf', 20)
        self.options = ["Play", "Settings", "History", "Credits", "Quit"]
        self.selected_option = 0

    def display_menu(self):
        self.screen.fill((0, 0, 0))
        
        # Display headline
        headline_surf = self.font.render("SPACE INVADERS", True, (255, 255, 255))
        headline_rect = headline_surf.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 6))
        self.screen.blit(headline_surf, headline_rect)
        
        for index, option in enumerate(self.options):
            color = (255, 255, 255) if index == self.selected_option else (100, 100, 100)
            text_surf = self.font.render(option, True, color)
            text_rect = text_surf.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + index * 30))
            self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

    def display_selected_option(self):
        self.screen.fill((0, 0, 0))
        selected_option_surf = self.font.render(self.options[self.selected_option], True, (255, 255, 255))
        selected_option_rect = selected_option_surf.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 4))
        self.screen.blit(selected_option_surf, selected_option_rect)
        
        if self.selected_option == 3:  # Credits
            credits = ["Yaniv Golan", "Arie Vainstein", "Zvi Komarov", "Avraham", "Sherr Maoz", "Ido Reved", "Ishai Picus"]
            for index, name in enumerate(credits):
                name_surf = self.font.render(name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + index * 30))
                self.screen.blit(name_surf, name_rect)
        
        # Display back button
        back_surf = self.font.render("Back", True, (255, 255, 255))
        back_rect = back_surf.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() - 50))
        self.screen.blit(back_surf, back_rect)
        
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return  # Go back to the main menu

    def run(self):
        while True:
            self.display_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Play
                            return self.selected_option
                        else:
                            self.display_selected_option()
