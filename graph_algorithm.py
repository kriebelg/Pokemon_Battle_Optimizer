import pokemon_class
from pokemon_type_data_scraper import read_effectiveness


def graph_builder(file_path):
    types, effectiveness = read_effectiveness(file_path)
    type_indices = {type_name: idx for idx, type_name in enumerate(types)}
    graph = pokemon_class.TypeGraph()
    for p_type in types:
        graph.add_vertex(p_type)
    for po_type in types:
        for pok_type in types:
            graph.add_attacking_edge(po_type, pok_type, effectiveness[type_indices[po_type]][type_indices[pok_type]])
    return graph


def strong_weak(chosen_pokemons):
    strong = {}
    weak = {}
    graph = graph_builder(file_path = 'chart.csv')
    for chosen_pokemon in chosen_pokemons:
        pokemon_vertex = graph.vertices[chosen_pokemon]
        for out in pokemon_vertex.outgoing_neighbors:
            if out == 2.0:
                for pokemon in pokemon_vertex.outgoing_neighbors[out]:
                    poke = pokemon.item
                    if poke in strong:
                        strong[poke] += 1
                    else:
                        strong[poke] = 1
            elif out == 0.5 or 0.0:
                for pokemon in pokemon_vertex.outgoing_neighbors[out]:
                    poke = pokemon.item
                    if poke in weak:
                        weak[poke] += 1
                    else:
                        weak[poke] = 1
        for inc in pokemon_vertex.incoming_neighbors:
            if inc == 2.0:
                for pokemon in pokemon_vertex.incoming_neighbors[inc]:
                    poke = pokemon.item
                    if poke in weak:
                        weak[poke] += 1
                    else:
                        weak[poke] = 1
            elif inc == 0.5 or 0.0:
                for pokemon in pokemon_vertex.incoming_neighbors[inc]:
                    poke = pokemon.item
                    if poke in strong:
                        strong[poke] += 1
                    else:
                        strong[poke] = 1
    return strong, weak


def dict_subtraction(strong, weak):
    final_dict = {}
    for poke_type in weak:
        if poke_type in strong:
            temp = weak[poke_type] - strong[poke_type]
            if temp > 0:
                final_dict[poke_type] = temp
        else:
            final_dict[poke_type] = weak[poke_type]

    return final_dict

def score_assigner(final_dict, enemy_types, graph):
    temp = {}
    for key in final_dict:
        defense_0 = 0
        defense_2 = 0
        defense_5 = 0
        attack_0 = 0
        attack_2 = 0
        attack_5 = 0
        one_point_zero = 0
        key = key.capitalize()
        for type in enemy_types:
            if type in graph.vertices[key].incoming_neighbors[0.0]:
                defense_0 += 1
            elif type in graph.vertices[key].incoming_neighbors[0.5]:
                defense_5 += 1
            elif type in graph.vertices[key].incoming_neighbors[2.0]:
                defense_2 += 1
            elif type in graph.vertices[key].incoming_neighbors[1.0]:
                one_point_zero += 1
            elif type in graph.vertices[key].outgoing_neighbors[0.0]:
                attack_0 += 1
            elif type in graph.vertices[key].outgoing_neighbors[0.5]:
                attack_5 += 1
            elif type in graph.vertices[key].outgoing_neighbors[2.0]:
                attack_2 += 1
            elif type in graph.vertices[key].incoming_neighbors[1.0]:
                one_point_zero += 1
        final_score = final_dict[key]*((30*defense_0)+(5*attack_2)+(3*defense_5)+(0.1*one_point_zero)-(4.9*defense_2)-(30*attack_0)-(2.9*attack_5))
        temp[key] = final_score
    return temp








