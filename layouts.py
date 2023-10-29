import networkx as nx
import auxiliar_methods as fnc
import random

def initialLayout(graph):
    positions = {}
    x_r = 0
    x_c = 0

    num_nodes = graph.number_of_nodes()
    num_reactions = sum(1 for _, data in graph.nodes(data=True) if data['node_type'] == 'reaction')
    num_components = num_nodes - num_reactions
    step = num_components /  num_reactions

    for node in graph.nodes():
        if graph.nodes[node]['node_type'] == 'reaction':
            x_r += step
            positions[node] = (x_r, 2)
        else:
            x_c += 1
            positions[node] = (x_c,1)

    return positions

def trivialGreedyLayout(graph):
    ordered_nodes = fnc.nodes_ordered_by_degree(graph)
    positions = {}
    x_r = 0
    x_c = 0

    num_nodes = graph.number_of_nodes()
    num_reactions = sum(1 for _, data in graph.nodes(data=True) if data['node_type'] == 'reaction')
    num_components = num_nodes - num_reactions
    step = num_components /  num_reactions
    
    for node in ordered_nodes:
        if not node in positions:
            
            if graph.nodes[node]['node_type'] == 'reaction':
                x_r += step
                positions[node] = (x_r, 2)
            else:
                x_c += 1
                positions[node] = (x_c,1)

            neighbours = graph.neighbors(node)
            ordered_neighbours = fnc.nodes_ordered_by_degree(graph,neighbours)
            for neighbour in ordered_neighbours:
                if neighbour in ordered_nodes:
                    if not neighbour in positions:
                        if graph.nodes[neighbour]['node_type'] == 'reaction':
                            x_r += step
                            positions[neighbour] = (x_r, 2)
                        else:
                            x_c += 1
                            positions[neighbour] = (x_c,1)

    return positions

def randomLayout(graph):
    reactions = [node for node, data in graph.nodes(data=True) if data['node_type'] == 'reaction']
    components = [node for node, data in graph.nodes(data=True) if data['node_type'] == 'component']

    random.shuffle(reactions)
    random.shuffle(components)

    positions = {}
    x_r = 0
    x_c = 0

    num_reactions = len(reactions)
    num_components = len(components)
    step = num_components /  num_reactions

    for node in reactions:
        x_r += step
        positions[node] = (x_r, 2)

    for node in components:    
        x_c += 1
        positions[node] = (x_c,1)

    return positions

def selectInitialLayout(graph):
    layout = input("Select layout:\n     0: Initial\n     1: Trivial Greedy\n     2: Random\n")
    match layout:
        case '0':
            return initialLayout(graph)
        case '1': 
            return trivialGreedyLayout(graph)
        case '2': 
            return randomLayout(graph)
        case _:
            return None
