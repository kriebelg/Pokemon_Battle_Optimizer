import csv

def get_pokemon_data(pokemon_id: int, filename: str) -> list:
    """Return the data for a specific Pokemon
    
    Preconditions:
      - pokemon_id is a valid Pokemon id
    """
    with open(filename) as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            if int(row[0]) == pokemon_id:
              return process_row(row)

def process_row(row: list[str]) -> list:
    """Convert a row of pokemon data to a list with more appropriate data types."""
    return [int(row[0]), 
            row[1], 
            row[2], 
            row[3], 
            int(row[4]), 
            int(row[5]), 
            int(row[6]), 
            int(row[7]), 
            int(row[8]), 
            int(row[9])]

print(get_pokemon_data(1, "pokemon_data.csv"))