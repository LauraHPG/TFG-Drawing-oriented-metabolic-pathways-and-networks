import networkx as nx
import sys

import grandalf
from grandalf.layouts import SugiyamaLayout

import matplotlib.pyplot as plt

import poly_point_isect as bent

import json

def read_graph(graph):
    nx.set_node_attributes(graph, {})
    for line in open(sys.argv[1]):
        reaction, substrates, products = line.rstrip().split(" : ")

        graph.add_node(reaction, node_type='reaction')

        for substrate in substrates.split(" "):

            graph.add_edge(substrate, reaction, relationship='substrate-reaction')
            graph.add_node(substrate, node_type='component')


        for product in products.split(" "):
            graph.add_edge(reaction, product, relationship='reaction-substrate')
            graph.add_node(product, node_type='component')

    return [node for node, data in graph.nodes(data=True) if data['node_type'] == 'reaction'], [node for node, data in graph.nodes(data=True) if data['node_type'] == 'component']

def splitHighDegreeComponents(graph, threshhold):

    ordered_nodes = nodes_ordered_by_degree(graph)
    print(f"Initial number of nodes: {graph.number_of_nodes()}")
    for node, degree in ordered_nodes:
        if degree >= threshhold and graph.nodes[node]['node_type'] != 'reaction':
                duplicateNode(graph, node)

    print(f"Final number of nodes: {graph.number_of_nodes()}")


def duplicateNode(graph, node):
    out_edges = graph.out_edges([node])
    in_edges = graph.in_edges([node])
    node_type = graph.nodes[node]['node_type']

    i = 0
    for out_edge in out_edges:
        new_node = "D" + str(i) + '_' + node
        i += 1
        graph.add_edge(new_node, out_edge[1], relationship='substrate-reaction')
        graph.add_node(new_node, node_type=node_type)

    for in_edge in in_edges:
        new_node = "D" + str(i) + '_'  + node
        i += 1
        graph.add_edge(in_edge[0], new_node, relationship='reaction-substrate')
        graph.add_node(new_node, node_type=node_type)
    
    linkSameNode(graph,node,i)
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

    cleanGraph = getCleanGraph(graph)
    cycles = nx.recursive_simple_cycles(cleanGraph)

    print(f"Number of cycles: {len(cycles)}")

    appearances = {}
    for cycle in cycles:
        for node in cycle:
            if node[0] == 'C':
                if node in appearances:
                    appearances[node] += 1
                else:
                    appearances[node] = 1


    sortedAppearances = sorted(appearances.items(), key=lambda x:x[1],reverse=True)

    print(f"{len(appearances)} nodes from {len(cleanGraph.nodes())} appear in a cycle")

    while True:
        print("(Node in most cycles, number of cycles it appears in): ", sortedAppearances[0])
        node = next(iter(sortedAppearances))[0]
        duplicateNode = input(f"Do you want to duplicate {node}? (Y/n)")
        if duplicateNode == "y" or duplicateNode == "Y":
            print(f"Initial number of nodes: {cleanGraph.number_of_nodes()}")

            out_edges = cleanGraph.out_edges([node])
            in_edges = cleanGraph.in_edges([node])

            i = 0
            for out_edge in out_edges:
                new_node = "D" + str(i) + '_' + node
                i += 1
                # cleanGraph.add_edge(new_node, out_edge[1], relationship='substrate-reaction')
                # cleanGraph.add_node(new_node, node_type='component')

                graph.add_edge(new_node, out_edge[1], relationship='substrate-reaction')
                graph.add_node(new_node, node_type='component')

            for in_edge in in_edges:
                new_node = "D" + str(i) + '_'  + node
                i += 1
                # cleanGraph.add_edge(in_edge[0], new_node, relationship='reaction-substrate')
                # cleanGraph.add_node(new_node, node_type='component')

                graph.add_edge(in_edge[0], new_node, relationship='reaction-substrate')
                graph.add_node(new_node, node_type='component')

            # linkSameNode(cleanGraph, node, i)
            linkSameNode(graph, node, i)

            # cleanGraph.remove_node(node)
            graph.remove_node(node)
            
            cleanGraph = getCleanGraph(graph)
            
        else:
            return

        print(f"Final number of nodes: {cleanGraph.number_of_nodes()}")
        cycles = nx.recursive_simple_cycles(cleanGraph)
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

        # Measure
        cleanGraph = getCleanGraph(graph)
        poses = sugiyama(cleanGraph)
        countCrossings(cleanGraph, poses)


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

def flipEdges(edges):
    flippedEdges = []
    for edge in edges:
        flippedEdges.append((edge[1],edge[0]))
    return flippedEdges

def changeSourceAndSinkNodeType(graph):
    for node in graph.nodes():
        in_edges = graph.in_edges(node)
        out_edges = graph.out_edges(node)
        
        flipped_in_edges = flipEdges(in_edges)
        flipped_out_edges = flipEdges(out_edges)
        
        real_in_edges = list(set(in_edges) - set(flipped_out_edges))
        real_out_edges = list(set(out_edges) - set(flipped_in_edges))

        if len(real_in_edges) == 0:
            graph.nodes[node]['node_type'] = 'source'
        elif len(real_out_edges) == 0:
            graph.nodes[node]['node_type'] = 'sink'

def rearangeSources(graph, pos):
    new_positions = {}
    for node in pos:
        if graph.in_degree(node) == 0:
            # print("source node:", node, "out degree:", graph.out_degree(node))
            [neighbor] = graph.neighbors(node)
            posNeigh = pos[neighbor]
            # print("Neighbor:", neighbor, "NPosition:", posNeigh)
            newPosX = 0
            if pos[node][0] < posNeigh[0]:
                newPosX = posNeigh[0]-40
            else:
                newPosX = posNeigh[0]+40

            # if the only neighbor lower of neighbor is node, put node at same x as neighbor
            belowNeighbors = 0
            for neigh in graph.predecessors(neighbor):
                # print(neigh, pos[neigh])
                if pos[neigh][1] < posNeigh[1]:
                    belowNeighbors += 1

            for neigh in graph.successors(neighbor):
                # print(neigh, pos[neigh])
                if pos[neigh][1] < posNeigh[1]:
                    belowNeighbors += 1


            # print(belowNeighbors)

            # it is the only under neigh, we put it under the upper one
            if belowNeighbors == 1:
                newPosX = posNeigh[0]

            new_positions[node] = (newPosX, posNeigh[1] - 40)
        else:
            new_positions[node] = pos[node]

    return new_positions 

def countCrossings(graph,pos):
    # numCrossings = 0

    segments = []
    for edge in graph.edges():
        # bentley ottman does not cover vertial lines -> change x by y, no two adjacent nodes will be at the same height 
        try:
            segments.append((pos[edge[0]][1],pos[edge[0]][0]), (pos[edge[1]][1],pos[edge[1]][0]))      
                              
        except:
            # print("Could not compute number of crossings inverted")

            try:
            
                segments = []
                segments.append(((pos[edge[0]][0],pos[edge[0]][1]), (pos[edge[1]][0],pos[edge[1]][1])))

            except:
                print("Could not compute number of crossings")
                return
            
    numCrossings = bent.isect_segments(segments, validate=True)
    print("Number of crossings:", len(numCrossings))    
    return numCrossings

def isConnected(graph):
    H = graph.to_undirected()
    numCC = nx.number_connected_components(H)
    print(f"Number of connected components: {numCC}")

    if numCC > 1:
        return False

    return True

def printGraphInfo(graph,poses):
    print("Num Nodes:", len(graph.nodes()))
    print("Num Edges:", len(graph.edges()))
    countCrossings(graph,poses)
    isConnected(graph)

def linkSameNode(graph, nodeName, iMax):
    for i in range(0,iMax):
        nodeI = "D" + str(i) + '_' + nodeName
        for j in range(0,iMax):
            nodeJ = "D" + str(j) + '_' + nodeName
            if i != j:
                graph.add_edge(nodeI, nodeJ, relationship='sameNode')
                graph.add_edge(nodeJ, nodeI, relationship='sameNode')
    
def remove_edges_with_attribute(graph, attribute_key, attribute_value):
    edges_to_remove = []
    edges = graph.edges()
    for edge in edges:
        if graph.edges[edge][attribute_key] == attribute_value:
            edges_to_remove.append(edge)
    graph.remove_edges_from(edges_to_remove)

    return graph

def getCleanGraph(graph):

    cleanGraph = nx.DiGraph(graph)

    cleanGraph = remove_edges_with_attribute(cleanGraph,'relationship','sameNode')
    return cleanGraph

def sugiyama(graph):

    cleanGraph = getCleanGraph(graph)

    g = grandalf.utils.convert_nextworkx_graph_to_grandalf(cleanGraph)


    class defaultview(object):
        w, h = 20, 20


    for v in g.C[0].sV:
        v.view = defaultview()

    sug = SugiyamaLayout(g.C[0])
    sug.init_all()  # roots = [V[0]])
    sug.draw()  # Calculate positions

    poses = {v.data: (v.view.xy[0], v.view.xy[1]) for v in g.C[0].sV}  # Extract positions
    poses = rearangeSources(cleanGraph, poses)
    
    return poses

def getLargestCC(graph):
    cleanGraph = getCleanGraph(graph)
    connected = isConnected(cleanGraph)
    edges = cleanGraph.edges()

    if not connected:
        H = cleanGraph.to_undirected()
        largest_cc = max(nx.connected_components(H), key=len)
        subGraph = cleanGraph.subgraph(largest_cc).copy()
        subGraph.to_directed()

        return subGraph
    return -1

def getConnectedComponents(graph):
    cleanGraph = getCleanGraph(graph)
    H = cleanGraph.to_undirected()
    # S = [H.subgraph(c).copy() for c in nx.connected_components(H)]
    S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    nth = input("Select nth CC:\n")
    n = int(nth)
    subGraph = cleanGraph.subgraph(S[n]).copy()
    subGraph.to_directed()

    return subGraph

def parseGraph(graph, node_positions):
    graphInfo = {}

    node_colors = nx.get_node_attributes(graph, "color")
    node_types = nx.get_node_attributes(graph, "node_type")

    graphInfo['nodes'] = []
    for node in graph.nodes():
        nodeInfo = {}
        nodeInfo['id'] = node
        nodeInfo['label'] = node
        nodeInfo['x'] = node_positions[node][0]
        nodeInfo['y'] = node_positions[node][1]
        nodeInfo['color'] = node_colors[node]
        nodeInfo['type'] = node_types[node]
        nodeInfo['shape'] = 'box'

        graphInfo['nodes'].append(nodeInfo)

    graphInfo['edges'] = []
    edge_relationships = nx.get_edge_attributes(graph, "relationship")
    for edge in graph.edges():
        # {"arrows": "to", "from": "C00668", "to": "R02739", "width": 1}
        edgeInfo = {}
        edgeInfo['arrows'] = "to"
        edgeInfo['from'] = edge[0]
        edgeInfo['to'] = edge[1]
        edgeInfo['width'] = 1
        edgeInfo['relationship'] = edge_relationships[edge]

        graphInfo['edges'].append(edgeInfo)

    print(graphInfo)
    # return graphInfo
    # with open("graphInfo.json", "w") as outfile:
    #     json.dump(graphInfo, outfile)


def printNodeInfo(graph, node):
    print("Predecessors:")
    for pred in graph.predecessors(node):
        print("- ", pred)
    print("Successors")
    for suc in graph.successors(node):
        print("- ", suc)
