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

def layeredDigraph(graph):
    positions = {}
    jList = []
    lastLayer = []
    source, lastLayer = fnc.get_source_and_sink_nodes(graph) #final layer are the sink nodes
    assignedNodes = set()
    numNodes = graph.number_of_nodes()
    # Initialize all source nodes to layer 0
    jList.append(source) 

    for node in source:
        assignedNodes.add(node)

    for node in lastLayer:
        assignedNodes.add(node)

    allNodesInALayer = False
    i = 0
    while not allNodesInALayer:
        for node in jList[i]:
            neighbors = graph.neighbors(node)
            for neigh in neighbors:
                if not neigh in assignedNodes:
                    if len(jList) == i + 1:
                        jList.append([])
                    jList[i + 1].append(neigh)
                    assignedNodes.add(neigh)
                    if numNodes == len(assignedNodes):
                        allNodesInALayer = True

        i += 1

    jList.append(lastLayer)
    print("Jlist: ", jList)

    for j, layer in enumerate(jList):
        for i, node in enumerate(layer):
            positions[node] = (i, j)

    # x_r = 0
    # x_c = 0
    # for node in source:
    #     positions[node] = (x_c, 0)
    #     x_c += 1
    #     graph[node].neighbors()
        
    return positions

def selectInitialLayout(graph):
    layout = input("Select layout:\n     0: Initial\n     1: Trivial Greedy\n     2: Random\n     3: Layered Digraph\n")
    match layout:
        case '0':
            return initialLayout(graph)
        case '1': 
            return trivialGreedyLayout(graph)
        case '2': 
            return randomLayout(graph)
        case '3':
            return layeredDigraph(graph)
        case _:
            return None
