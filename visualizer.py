import pygame
import requests
import io

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Teams")

background = pygame.image.load("images/background2.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
RED = (255, 100, 100)

font = pygame.font.Font(None, 28)

pokemon_names = ["pikachu", "charizard", "blastoise", "venusaur", "gengar", "alakazam", 
                 "lucario", "tyranitar", "metagross", "salamence", "garchomp", "dragonite"]
enemy_team = pokemon_names[0:6] # gets first 6 pokemon names
user_team = pokemon_names[6:12] # gets last 6 pokemon names

BASE_URL = "https://img.pokemondb.net/sprites/black-white/normal/"

def load_sprite_from_url(pokemon_name):
    url = f"{BASE_URL}{pokemon_name}.png"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image = pygame.image.load(io.BytesIO(response.content))
        return pygame.transform.scale(image, (80, 80))  # Resize if needed
    else:
        print(f"Could not load sprite for {pokemon_name}")
        return None

pokemon_sprites = {name: load_sprite_from_url(name) for name in pokemon_names}

enemy_team_positions = [(WIDTH // 2 - 250 + i * 100, (HEIGHT // 4) + 100) for i in range(6)]
user_team_positions = [(WIDTH // 2 - 250 + i * 100, HEIGHT * 3 // 4) for i in range(6)]

running = True
while running:
    screen.blit(background, (0, 0))

    for i, name in enumerate(enemy_team): 
        x, y = enemy_team_positions[i]
        
        if pokemon_sprites[name]:
            screen.blit(pokemon_sprites[name], (x - 40, y - 40))
        
        pokemon_name = font.render(name.capitalize(), True, BLACK)
        screen.blit(pokemon_name, (x - pokemon_name.get_width() // 2, y - 60))

    for i, name in enumerate(user_team):
        x, y = user_team_positions[i]
        
        if pokemon_sprites[name]:
            screen.blit(pokemon_sprites[name], (x - 40, y - 40))

        pokemon_name = font.render(name.capitalize(), True, BLACK)
        screen.blit(pokemon_name, (x - pokemon_name.get_width() // 2, y - 60))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
