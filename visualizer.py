import pygame
import requests
import io
import pandas as pd
import random
from pokemon_data_scraper import get_pokemon_data, convert_pokemon_to_id
from graph_algorithm import recommend_top_types
from pokemon_final_team import get_user_pokemon, get_pokemon
from pokemon_class import Pokemon

pygame.init()

WIDTH, HEIGHT = 800, 600
BLACK, WHITE, RED = (0, 0, 0), (255, 255, 255), (255, 0, 0)
ENEMY_TEAM_OFFSET, USER_TEAM_OFFSET = 250, 440
FONT = pygame.font.SysFont("consolas", 20)
BASE_URL = "https://img.pokemondb.net/sprites/"
ADD_ONS = ("scarlet-violet/normal/1x/", "x-y/normal/", "sun-moon/normal/1x/", "sword-shield/normal/")

START_SCREEN, INPUT_SCREEN, RESULT_SCREEN = range(3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pokémon Battle Matchup Optimizer")

        self.background = pygame.transform.scale(pygame.image.load("images/background2.png"), (WIDTH, HEIGHT))

        # game state
        self.state = START_SCREEN
        self.enemy_team = [""] * 6
        self.user_team = [""] * 6
        self.running = True
        self.input_index = 0
        self.error_message = None
        self.pokemon_sprites = {}

        # ui elements
        self.start_button = None
        self.enter_button = None
        self.random_button = None
        self.back_button = None

    def load_sprite(self, pokemon_name: str) -> pygame.Surface:
        """Tries to load a Pokémon sprite from the web, handling variations in naming."""
        if pokemon_name in self.pokemon_sprites:
            return self.pokemon_sprites[pokemon_name]

        formatted_name = pokemon_name.lower().replace(" ", "-").replace(".", "").replace("'", "").replace("♀", "-f").replace("♂", "-m")

        for url in ADD_ONS:
            try:
                sprite = self.fetch_sprite(BASE_URL + url + formatted_name + ".png")
                if sprite:
                    self.pokemon_sprites[pokemon_name] = sprite
                    return self.adjust_sprite(sprite, url)
            except Exception as e:
                print(f"Error loading {pokemon_name}: {e}")

        print(f"Sprite not found: {pokemon_name}")
        return None

    def fetch_sprite(self, url: str) -> pygame.Surface:
        """Helper function to fetch and scale a sprite from a given URL."""
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            sprite = pygame.image.load(io.BytesIO(response.content))
            return pygame.transform.scale(sprite, (80, 80))
        return None

    def adjust_sprite(self, sprite: pygame.Surface, url: str) -> pygame.Surface:
        """Adjusts the sprite if needed based on the source URL."""
        if url == ADD_ONS[0]: 
            return sprite

        adjusted_sprite = pygame.Surface((80, 90), pygame.SRCALPHA)
        if url == ADD_ONS[1]:
            y_offset = 20
        elif url == ADD_ONS[2]:
            y_offset = 0
        elif url == ADD_ONS[3]:
            y_offset = 0
        adjusted_sprite.blit(sprite, (0, y_offset))
        return adjusted_sprite

    def get_team_positions(self, vertical_offset: float) -> list[int]:
        """Returns a list of positions for the Pokémon sprites."""
        return [(WIDTH // 7 + i * 115, vertical_offset) for i in range(6)]

    def display_pokemon(self, pokemon_name: str, position: float) -> None:
        """Displays a Pokémon name and sprite at the given position."""
        x, y = position
        sprite = self.pokemon_sprites.get(pokemon_name)
        if sprite:
            self.screen.blit(sprite, (x - 40, y - 40))
        pokemon_name_text = FONT.render(pokemon_name.capitalize(), True, BLACK)
        self.screen.blit(pokemon_name_text, (x - pokemon_name_text.get_width() // 2, y - 40))

    def draw_button(self, text, x_pos, y_pos, width, height) -> None:
        """Draws a button on the screen."""
        rect = pygame.Rect(x_pos, y_pos, width, height)
        pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        text_surface = FONT.render(text, True, BLACK)
        self.screen.blit(text_surface, (x_pos + (width - text_surface.get_width()) // 2, y_pos + (height - text_surface.get_height()) // 2))
        return rect
    
    def draw_input_boxes(self):
        """Draws input boxes for entering the enemy team Pokémon names."""
        for i in range(6):
            x, y = WIDTH // 2 - 100, 250 + i * 30
            box_rect = pygame.Rect(x - 10, y - 5, 200, 25)

            pygame.draw.rect(self.screen, WHITE, box_rect)
            pygame.draw.rect(self.screen, BLACK, box_rect, 2)
            
            text_surface = FONT.render(f"{i + 1}. {self.enemy_team[i]}", True, BLACK)
            self.screen.blit(text_surface, (x, y))
            
            if i == self.input_index:
                pygame.draw.polygon(self.screen, BLACK, [
                    (x - 15, y + 5),
                    (x - 20, y),
                    (x - 20, y + 10)
                ])

    def check_game_state(self) -> None:
        """Updates screen based on current game state."""
        if self.state == START_SCREEN:
            self.start_button = self.draw_button("Start", WIDTH // 2 - 50, HEIGHT // 2 + 125, 100, 50)
            title_text = pygame.image.load("images/title_text.png")
            title_text_sized = pygame.transform.scale(title_text, (title_text.get_width() // 1.5, title_text.get_height() // 1.5))
            self.screen.blit(title_text_sized, (WIDTH // 7, HEIGHT // 3 + 50))

        elif self.state == INPUT_SCREEN:
            input_text = FONT.render("Enter the Pokémon on the enemy team:", True, BLACK)
            self.screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 200))
            self.draw_input_boxes()
            self.enter_button = self.draw_button("Enter Team", WIDTH // 2.3, HEIGHT - 100, 120, 50)
            self.draw_error_message()
            self.random_button = self.draw_button("Randomize Team", WIDTH // 10, HEIGHT // 2 + 20, 160, 50)

        elif self.state == RESULT_SCREEN:
            self.display_results()
            
    def display_results(self) -> None:
        """Displays results on screen."""
        enemy_team_positions = self.get_team_positions(ENEMY_TEAM_OFFSET)
        user_team_positions = self.get_team_positions(USER_TEAM_OFFSET)

        for i in range(6):
            start_pos = user_team_positions[i]
            end_pos = enemy_team_positions[i]
            updated_start_pos = (start_pos[0], start_pos[1] - 50)
            updated_end_pos = (end_pos[0], end_pos[1] + 50)

            pygame.draw.line(self.screen, BLACK, updated_start_pos, updated_end_pos, 3)
            self.draw_arrowhead(updated_start_pos, updated_end_pos)
            self.draw_arrowhead(updated_end_pos, updated_start_pos) 
        
        for i, name in enumerate(self.enemy_team):
            self.display_pokemon(name, enemy_team_positions[i])

        for i, name in enumerate(self.user_team):
            self.display_pokemon(name, user_team_positions[i])

        self.back_button = self.draw_button("Back", WIDTH // 2.3, HEIGHT - 100, 120, 50)

    def draw_arrowhead(self, start, end) -> None:
        """Draws an arrowhead at the end of a line."""
        import math
        
        arrow_size = 10
        angle = math.atan2(end[1] - start[1], end[0] - start[0])

        # calculate arrowhead points
        point1 = (end[0] - arrow_size * math.cos(angle - math.pi / 6), 
                end[1] - arrow_size * math.sin(angle - math.pi / 6))
        point2 = (end[0] - arrow_size * math.cos(angle + math.pi / 6), 
                end[1] - arrow_size * math.sin(angle + math.pi / 6))

        # triangle arrowhead
        pygame.draw.polygon(self.screen, BLACK, [end, point1, point2])

    def handle_event(self, event, mouse_position) -> None:
        """Handles events."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == START_SCREEN and self.start_button.collidepoint(mouse_position):
                self.state = INPUT_SCREEN
            elif self.state == INPUT_SCREEN and self.enter_button.collidepoint(mouse_position):
                self.check_team()
            elif self.state == INPUT_SCREEN and self.random_button.collidepoint(mouse_position):
                self.enemy_team = generate_random_team(pd.read_csv("pokemon_data.csv"))
                self.pokemon_sprites = {name: self.load_sprite(name) for name in self.enemy_team}
                self.error_message = None
                self.input_index = 0
                self.draw_input_boxes()
            elif self.state == RESULT_SCREEN and self.back_button.collidepoint(mouse_position):
                self.enemy_team = [""] * 6
                self.user_team = [""] * 6
                self.pokemon_sprites.clear()
                self.state = INPUT_SCREEN
        elif event.type == pygame.KEYDOWN and self.state == INPUT_SCREEN:
            self.enter_enemy_team(event)

    def check_team(self) -> None:
        """Checks if inputted enemy team is valid."""
        self.pokemon_sprites = {name: self.load_sprite(name) for name in set(self.enemy_team)}
        invalid_names = [name for name in self.enemy_team if not self.pokemon_sprites.get(name)]

        if invalid_names:
            self.error_message = "Invalid Pokémon names: " + ", ".join(invalid_names)
        else:
            # self.user_team = get_user_pokemon((get_pokemon(self.enemy_team, "pokemon_data.csv"), 'pokemon_data.csv'), 'pokemon_data.csv', 'chart.csv')
            self.user_team = get_user_pokemon(get_pokemon([convert_pokemon_to_id(pkmn, "pokemon_data.csv") for pkmn in self.enemy_team], "pokemon_data.csv"), "pokemon_data.csv", "chart.csv")
            self.pokemon_sprites.update({name.lower(): self.load_sprite(name) for name in set(self.user_team)})
            self.state = RESULT_SCREEN
            self.error_message = None

    def draw_error_message(self) -> None:
        """Displays error message on screen."""
        if self.error_message:
            error_surface = FONT.render(self.error_message, True, RED)
            self.screen.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, HEIGHT - 130))

    def enter_enemy_team(self, event) -> None:
        """Handles input for enemy team Pokémon names."""
        if event.key == pygame.K_RETURN or event.key == pygame.K_DOWN:
            self.enemy_team[self.input_index] = self.enemy_team[self.input_index].strip()
            self.input_index = (self.input_index + 1) % 6  # down
        elif event.key == pygame.K_UP:
            self.input_index = (self.input_index - 1) % 6  # up
        elif event.key == pygame.K_BACKSPACE:
            self.enemy_team[self.input_index] = self.enemy_team[self.input_index][:-1]
        else:
            self.enemy_team[self.input_index] += event.unicode.lower()


    def run(self):
        while self.running:
            self.screen.blit(self.background, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.check_game_state()
            for event in pygame.event.get():
                self.handle_event(event, mouse_pos)
            pygame.display.flip()
        pygame.quit()

def run_algorithm(team, data) -> list[str]:  # placeholder for algorithm function
    return ["charmander", "quilava", "quilava", "quilava", "quilava", "quilava"] # i love quilava

def convert_team_to_ints(team) -> list[int]:
    id_list = []
    for pkmn in team:
        id_list.append(convert_pokemon_to_id(pkmn, "pokemon_data.csv"))
    return id_list

def generate_random_team(data):
    """Generates a random Pokémon team."""
    return random.sample(data["Name"].tolist(), 6)

if __name__ == "__main__":
    Game().run()
