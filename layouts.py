import networkx as nx

def trivialLayout(graph):
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

def greedyLayout1(graph):
    ordered_nodes = nx.nodes_ordered_by_degree(graph)
    print(ordered_nodes)
    positions = {}
    x_r = 0
    x_c = 0

    num_nodes = graph.number_of_nodes()
    num_reactions = sum(1 for _, data in graph.nodes(data=True) if data['node_type'] == 'reaction')
    num_components = num_nodes - num_reactions
    step = num_components /  num_reactions
    
    for node in ordered_nodes:
        if not node in positions:
            print(f"Node {node} has degree: {graph.degree[node]}")   
            
            if graph.nodes[node]['node_type'] == 'reaction':
                x_r += step
                positions[node] = (x_r, 2)
            else:
                x_c += 1
                positions[node] = (x_c,1)

            neighbours = graph.neighbors(node)
            ordered_neighbours = nx.nodes_ordered_by_degree(graph,neighbours)
            for neighbour in ordered_neighbours:
                if neighbour in ordered_nodes:
                    if not neighbour in positions:
                        if graph.nodes[neighbour]['node_type'] == 'reaction':
                            x_r += step
                            positions[neighbour] = (x_r, 2)
                        else:
                            x_c += 1
                            positions[neighbour] = (x_c,1)

    print(positions.__len__())
    return positions

def selectInitialLayout(graph):
    layout = input("Select layout:\n     0: Trivial\n     1: Greedy pocho\n")
    match layout:
        case '0':
            return trivialLayout(graph)
        case '1': 
            return greedyLayout1(graph)
        case _:
            return None
