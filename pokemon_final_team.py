import csv
import pokemon_data_scraper
from pokemon_class import Pokemon, Type
from graph_algorithm import recommend_top_types

def get_team_bst(team: Pokemon | list[Pokemon]):
    """gets the teams bst category"""
    if isinstance(team, Pokemon):
        return team.bst
    else:
        total_bst = 0
        for pokemon in team:
            total_bst += get_team_bst(pokemon)
        return total_bst // len(team)

def ideal_bst_range(team: Pokemon | list[Pokemon]):
    enemy_bst = get_team_bst(team)
    if isinstance(team, Pokemon):
        return [enemy_bst - 10, enemy_bst + 10]
    else:
        max_bst = max([pokemon.bst for pokemon in team])
        min_bst = min([pokemon.bst for pokemon in team])
        return [min_bst, max_bst]

def get_pokemon(team: list[int], file_path='pokemon_data.csv'):
    poke_list = []
    # pokemon = Pokemon(0, '', Type('', {'':0.0}), Type('', {}), 0, 0, 0, 0, 0)
    for poke in team:
        data = pokemon_data_scraper.get_pokemon_data([poke], file_path)

        if not data or not data[0]:
            continue 

        pokemon = Pokemon(
            pokemon_id=data[0][0],
            name=data[0][1],
            type1=data[0][2],
            type2=data[0][3] if data[0][3] else None,
            attack=data[0][4],
            defense=data[0][5],
            spec_attack=data[0][6],
            spec_defense=data[0][7],
            speed=data[0][8]
        )
        poke_list.append(pokemon)
    return poke_list

def filter_bst_team(team: list[Pokemon], bst_range: list[int]):
    new_team = []

    for pokemon in team:
        if bst_range[0] <= pokemon.bst <= bst_range[1]:
            new_team.append(pokemon)
    return new_team

def get_types(team: list[Pokemon]):
    types = [] 
    for pokemon in team:
        if pokemon.type2 is None:
            types.append(pokemon.type1)
        else:
            types.append((pokemon.type1, pokemon.type2))
    return tuple(types)

def get_user_pokemon(team: list[Pokemon], file_pokemon='pokemon_data.csv', file_types='chart.csv'):
    '''get enemy pokemon based on bst and type'''
    types = get_types(team)
    type = recommend_top_types(types, file_types, len(team))
    typ = [item[0] for item in type]
    enemy_bst_range = ideal_bst_range(team)
    possible_poke = []

    with open(file_pokemon, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            poke_types = (row[2], row[3]) if row[3] else row[2]
        
            if poke_types in types or row[2] in typ:
                possible_poke.append(int(row[0]))
    
    poke_data = get_pokemon(possible_poke, file_pokemon)
    po_data = filter_bst_team(poke_data, enemy_bst_range)
    pok_sorted = sorted(po_data, key=lambda x: x.bst, reverse=True)

    final_team = []
    count = len(team)
    for pokemon in pok_sorted:
        if count > 0:
            final_team.append(pokemon.name)
            count -= 1
    return final_team

if __name__ == '__main__':
    g = get_user_pokemon(get_pokemon([1,2,3,4,5,6], 'pokemon_data.csv'), 'pokemon_data.csv', 'chart.csv')
    print(g)
