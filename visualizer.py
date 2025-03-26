import pygame
import requests
import io

pygame.init()

WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT = pygame.font.SysFont("consolas", 20)
BASE_URL = "https://img.pokemondb.net/sprites/scarlet-violet/normal/1x/"  # not pixelated ones, idk which style is better
ALT_URL = "https://img.pokemondb.net/sprites/x-y/normal/"

class Game:
    START_SCREEN = 0
    INPUT_SCREEN = 1
    RESULT_SCREEN = 2

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pokémon Battle Matchup Optimizer")
        self.background = pygame.image.load("images/background2.png")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.state = Game.START_SCREEN
        self.enemy_team = [""] * 6
        self.user_team = [""] * 6
        self.running = True

        self.start_button = pygame.Rect(0, 0, 0, 0)
        self.enter_button = pygame.Rect(0, 0, 0, 0)
        self.pokemon_sprites = {}

    def load_sprite_from_url(self, pokemon_name):
        url = f"{BASE_URL}{pokemon_name}.png"
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            return pygame.transform.scale(pygame.image.load(io.BytesIO(response.content)), (80, 80))
        else:
            url = f"{ALT_URL}{pokemon_name}-f.png"
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                return pygame.transform.scale(pygame.image.load(io.BytesIO(response.content)), (80, 80))

        print(f"Could not load sprite for {pokemon_name}")
        return None

    def get_team_positions(self, team, vertical_offset) -> list[int]:
        return [(WIDTH // 2 - 250 + i * 100, vertical_offset) for i in range(6)]

    def display_pokemon(self, pokemon_name, position) -> None:
        x, y = position
        if self.pokemon_sprites.get(pokemon_name):
            self.screen.blit(self.pokemon_sprites[pokemon_name], (x - 40, y - 40))

        pokemon_name_text = FONT.render(pokemon_name.capitalize(), True, BLACK)
        self.screen.blit(pokemon_name_text, (x - pokemon_name_text.get_width() // 2, y - 60))

    def draw_button(self, text, x_pos, y_pos, width, height, colour, action=None) -> None:
        pygame.draw.rect(self.screen, colour, (x_pos, y_pos, width, height))
        text_surface = FONT.render(text, True, BLACK)
        self.screen.blit(text_surface, (x_pos + (width - text_surface.get_width()) // 2, y_pos + (height - text_surface.get_height()) // 2))
        return pygame.Rect(x_pos, y_pos, width, height)

    def check_game_state(self) -> None:
        if self.state == Game.START_SCREEN:
            self.start_button = self.draw_button("Start", WIDTH // 2 - 50, HEIGHT // 2, 100, 50, WHITE)
            title_text = FONT.render("Pokemon Battle Matchup Optimizer", True, BLACK)
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))

        elif self.state == Game.INPUT_SCREEN:
            input_text = FONT.render("Enter the Pokémon on the enemy team:", True, BLACK)
            self.screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 200))
            
            for i, name in enumerate(self.enemy_team):
                text_surface = FONT.render(f"{i + 1}. {name}", True, BLACK)
                self.screen.blit(text_surface, (WIDTH // 2 - 100, 250 + i * 30))
            
            self.enter_button = self.draw_button("Enter Team", WIDTH // 2 - 50, HEIGHT - 100, 100, 50, WHITE)
            
        elif self.state == Game.RESULT_SCREEN:
            enemy_team_positions = self.get_team_positions(self.enemy_team, (HEIGHT // 4) * 2)
            user_team_positions = self.get_team_positions(self.user_team, (HEIGHT // 4) * 3)
            
            for i, name in enumerate(self.enemy_team):
                self.display_pokemon(name, enemy_team_positions[i])
            
            for i, name in enumerate(self.user_team):
                self.display_pokemon(name, user_team_positions[i])

    def handle_event(self, event, mouse_position) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == Game.START_SCREEN and self.start_button and self.start_button.collidepoint(mouse_position):
                self.state = Game.INPUT_SCREEN
            elif self.state == Game.INPUT_SCREEN and self.enter_button and self.enter_button.collidepoint(mouse_position):
                self.user_team = get_enemy_team()
                pokemon_names = set(self.enemy_team + self.user_team)
                print(pokemon_names)
                self.pokemon_sprites = {name: self.load_sprite_from_url(name) for name in pokemon_names}
                self.state = Game.RESULT_SCREEN
        elif event.type == pygame.KEYDOWN and self.state == Game.INPUT_SCREEN:
            self.enter_enemy_team(event)

    def enter_enemy_team(self, event, input_index=[0]) -> None:
        if event.key == pygame.K_RETURN:
            input_index[0] += 1
            if input_index[0] >= 6:
                input_index[0] = 0
        elif event.key == pygame.K_BACKSPACE:
            self.enemy_team[input_index[0]] = self.enemy_team[input_index[0]][:-1]
        else:
            self.enemy_team[input_index[0]] += event.unicode.lower()

    def run(self):
        enemy_team_positions = self.get_team_positions(self.enemy_team, HEIGHT // 4 + 100)
        user_team_positions = self.get_team_positions(self.user_team, HEIGHT // 4 * 3)
            
        self.running = True
        while self.running:
            self.screen.blit(self.background, (0, 0))
            mouse_pos = pygame.mouse.get_pos()

            self.check_game_state()

            for event in pygame.event.get():
                self.handle_event(event, mouse_pos)

            pygame.display.flip()

        pygame.quit()

def get_enemy_team() -> list[str]:
    return ["quilava", "quilava", "quilava", "quilava", "quilava", "quilava"] # i love quilava

if __name__ == "__main__":
    game = Game()
    game.run()