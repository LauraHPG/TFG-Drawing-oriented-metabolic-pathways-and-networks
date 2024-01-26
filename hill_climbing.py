import auxiliar_methods as fnc
import networkx as nx

def hill_climbing_2_lines(pos0, graph, reactions, edges_crossings_edge):
    pos = pos0  # initial solution
    iteration = 0
    while True:
        print(f"Iteration {iteration}")
        iteration += 1
        neighbor1, neighbor2 = generate_neighbors_2_lines(pos, edges_crossings_edge, reactions)  # generate neighbors of x

        neighbor1_crossings, _ = fnc.count_edge_crossings(graph, neighbor1, reactions)
        neighbor2_crossings, _ = fnc.count_edge_crossings(graph, neighbor2, reactions)

        print(neighbor1_crossings)
        print(neighbor2_crossings)
        
        best_neighbor_crossings, best_neighbor = (neighbor1_crossings, neighbor1) if neighbor1_crossings < neighbor2_crossings else (neighbor2_crossings, neighbor2)

        pos_crossings, _ = fnc.count_edge_crossings(graph, pos, reactions)

        print(pos_crossings)

        if pos_crossings <= best_neighbor_crossings:  # if the best neighbor is not better than x, stop
            return pos
        pos = best_neighbor  # otherwise, continue with the best neighbor

def hill_climbing_3_lines(pos0, graph, reactions, components):
    pos = pos0  # initial solution
    iteration = 0
    while True:
        print(f"3lines Iteration {iteration}")
        iteration += 1

        new_pos = generate_neighbors_3_lines(graph, pos, components)
        new_pos_crossings, _ = fnc.count_edge_crossings(graph, new_pos, reactions)

        print(new_pos_crossings)

        pos_crossings, _ = fnc.count_edge_crossings(graph, pos, reactions)

        print(pos_crossings)

        if pos_crossings <= new_pos_crossings:  # if the best neighbor is not better than x, stop
            return new_pos
        pos = new_pos  # otherwise, continue with the best neighbor

def swap_edges(pos, e1, e2, reactions):

    node1= e1[0]
    node2= e1[1]
    node3= e2[0]
    node4= e2[1]

    pos1 = pos.copy()
    pos2 = pos.copy()

    if node1 in reactions:
        if node3 in reactions: #node1 and node3 are reactions
            pos1[node1], pos1[node3] = pos1[node3], pos1[node1] #reactions swap
            pos2[node2], pos2[node4] = pos2[node4], pos2[node2] #components swap
        else: #node1 and node4 are reactions
            pos1[node1], pos1[node4] = pos1[node4], pos1[node1] #reactions swap 
            pos2[node2], pos2[node3] = pos2[node3], pos2[node2] #components swap
    else:
        if node3 in reactions:  #node2 and node3 are reactions
            pos1[node2], pos1[node3] = pos1[node3], pos1[node2] #reactions swap
            pos2[node1], pos2[node4] = pos2[node4], pos2[node1] #components swap
        else: #node2 and node4 are reactions
            pos1[node2], pos1[node4] = pos1[node4], pos1[node2] #reactions swap
            pos2[node1], pos2[node3] = pos2[node3], pos2[node1] #components swap

    return pos1, pos2

def reverse_dict_order(original_dict):
    reversed_dict = {}
    for key in reversed(list(original_dict.keys())):
        reversed_dict[key] = original_dict[key]
    return reversed_dict

def generate_neighbors_2_lines(pos, edges_crossing_edge, reactions):
    heaviest_edge, adjacent_edges = next(iter(edges_crossing_edge.items()))

    rev = reverse_dict_order(edges_crossing_edge)
    for edge in rev:
        if edge in adjacent_edges:
            return swap_edges(pos,heaviest_edge, edge, reactions)

