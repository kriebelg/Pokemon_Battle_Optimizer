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
