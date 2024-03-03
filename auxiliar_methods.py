import networkx as nx
import sys

def read_graph(graph):
    nx.set_node_attributes(graph, {})
    for line in open(sys.argv[1]):
        reaction, substrates, products = line.rstrip().split(" : ")
        
        graph.add_node(reaction, node_type='reaction')

        for substrate in substrates.split(" "):

            graph.add_edge(substrate, reaction)
            graph.add_node(substrate, node_type='component')

            
        for product in products.split(" "):
            graph.add_edge(reaction, product)
            graph.add_node(product, node_type='component')
    
    
    splitHighDegreeComponents(graph)
    
    H = graph.to_undirected()
    print(f"Number of connected components: {nx.number_connected_components(H)}")

    return [node for node, data in graph.nodes(data=True) if data['node_type'] == 'reaction'], [node for node, data in graph.nodes(data=True) if data['node_type'] == 'component']

def splitHighDegreeComponents(graph):

    doSplit = input("Do you want to split the high degree components? (Y/n)")

    if doSplit == "Y" or doSplit == "y":

        ordered_nodes = nodes_ordered_by_degree(graph)
        print(f"Initial number of nodes: {graph.number_of_nodes()}")
        for node, degree in ordered_nodes:
            if degree >= 10 and graph.nodes[node]['node_type'] == 'component':
                 duplicateNode(graph, node)
        
        print(f"Final number of nodes: {graph.number_of_nodes()}")  
    else:
        return

def duplicateNode(graph, node):
    out_edges = graph.out_edges([node])
    in_edges = graph.in_edges([node])

    i = 0
    for out_edge in out_edges:
        new_node = "D" + str(i) + '_' + node
        i += 1
        graph.add_edge(new_node, out_edge[1])
        graph.add_node(new_node, node_type='component')
    
    for in_edge in in_edges:
        new_node = "D" + str(i) + '_'  + node
        i += 1
        graph.add_edge(in_edge[0], new_node)
        graph.add_node(new_node, node_type='component')

    graph.remove_node(node) 

def nodes_ordered_by_degree(graph, nodes=None):
    """
    Returns a list of nodes ordered by degree in descending order.

    Args:
    graph (networkx.Graph): The input graph.
    nodes (list or None): List of nodes to order by degree. If None, all nodes in the graph are used.

    Returns:
    list: A list of nodes ordered by degree in descending order.
    """
    if nodes is None:
        nodes = graph.nodes()

    # Calculate the degree for each node and create a list of (node, degree) tuples
    degree_list = [(node, degree) for node, degree in graph.degree(nodes)]

    # Sort the list by degree in descending order
    degree_list.sort(key=lambda x: x[1], reverse=True)

    # Extract the nodes from the sorted list
    #nodes_sorted_by_degree = [node for node, _ in degree_list]

    #return nodes_sorted_by_degree
    return degree_list

def removeCyclesByNodeInMostCycles(graph):

    cycles = nx.recursive_simple_cycles(graph)

    appearances = {}
    for cycle in cycles:
        for node in cycle:
            if node[0] == 'C':
                if node in appearances:
                    appearances[node] += 1
                else:
                    appearances[node] = 1


    sortedAppearances = sorted(appearances.items(), key=lambda x:x[1],reverse=True)

    print(f"Number of nodes in a cycle: {len(appearances)}")

    while True:
        print("(Node in most cycles, number of cycles it appears in): ", sortedAppearances[0])
        node = next(iter(sortedAppearances))[0]
        duplicateNode = input(f"Do you want to duplicate {node}? (Y/n)")
        if duplicateNode == "y" or duplicateNode == "Y":
            print(f"Initial number of nodes: {graph.number_of_nodes()}")
            
            out_edges = graph.out_edges([node])
            in_edges = graph.in_edges([node])

            i = 0
            for out_edge in out_edges:
                new_node = "D" + str(i) + '_' + node
                i += 1
                graph.add_edge(new_node, out_edge[1])
                graph.add_node(new_node, node_type='component')
            
            for in_edge in in_edges:
                new_node = "D" + str(i) + '_'  + node
                i += 1
                graph.add_edge(in_edge[0], new_node)
                graph.add_node(new_node, node_type='component')

            graph.remove_node(node) 
        else:
            return

        print(f"Final number of nodes: {graph.number_of_nodes()}")  
        cycles = nx.recursive_simple_cycles(graph)
        print(f"Number of cycles: {len(cycles)}")
        if len(cycles) == 0 : return

        appearances = {}
        for cycle in cycles:
            for node in cycle:
                if node[0] == 'C':
                    if node in appearances:
                        appearances[node] += 1
                    else:
                        appearances[node] = 1

        sortedAppearances = sorted(appearances.items(), key=lambda x:x[1],reverse=True)
        
        H = graph.to_undirected()
        print(f"Number of connected components: {nx.number_connected_components(H)}")

def get_color(node_type):
    if node_type == 'reaction':
        return 'blue'   
    if node_type == 'source':
        return 'orange'
    if node_type == 'sink':
        return 'green'
    return 'red'
 
def setColorNodeType(graph):

    node_colors = {node: get_color(data['node_type']) for node, data in graph.nodes(data=True)}
    nx.set_node_attributes(graph, node_colors, 'color')

    colors = [data['color'] for _, data in graph.nodes(data=True)]

    return colors

def changeSourceAndSinkNodeType(graph):
    for node in graph.nodes():
        if graph.in_degree(node) == 0:
            graph.nodes[node]['node_type'] = 'source'
        elif graph.out_degree(node) == 0:
            graph.nodes[node]['node_type'] = 'sink'

def rearangeSources(graph, pos):
    for node in pos:
        if graph.in_degree(node) == 0:
            print("source node:", node, "out degree:", graph.out_degree(node))
            [neighbor] = graph.neighbors(node)
            posNeigh = pos[neighbor]
            print("Neighbor:", neighbor, "NPosition:", posNeigh)
            newPosX = 0
            if pos[node][0] < posNeigh[0]:
                newPosX = posNeigh[0]-40
            else:
                newPosX = posNeigh[0]+40
            
            # if the only neighbor lower of neighbor is node, put node at same x as neighbor
            belowNeighbors = 0
            for neigh in graph.predecessors(neighbor):
                print(neigh, pos[neigh])
                if pos[neigh][1] < posNeigh[1]:
                    belowNeighbors += 1

            for neigh in graph.successors(neighbor):
                print(neigh, pos[neigh])
                if pos[neigh][1] < posNeigh[1]:
                    belowNeighbors += 1


            print(belowNeighbors)
            if belowNeighbors == 1:
                newPosX = posNeigh[0]

            pos[node] = (newPosX, posNeigh[1] - 40)

def countCrossings(graph,pos):
   pass