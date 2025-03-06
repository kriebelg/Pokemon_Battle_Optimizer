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



