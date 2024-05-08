import networkx as nx
import sys

import grandalf
from grandalf.layouts import SugiyamaLayout, DigcoLayout

import matplotlib.pyplot as plt

try:
    from . import poly_point_isect as bent
except:
    import poly_point_isect as bent

import json

import requests


def read_graph(graph):
    nx.set_node_attributes(graph, {})
    path = sys.argv[1]
    info = read_graph_from_txt(graph, path)
    checkMaxCCSize(graph)

    return info

def read_graph_from_txt(graph, path):
    for line in open(path):
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
    degree_list = [(node, degree) for node, degree in graph.degree(nodes) if not node.startswith('R')]

    # Sort the list by degree in descending order
    degree_list.sort(key=lambda x: x[1], reverse=True)


    # Extract the nodes from the sorted list
    #nodes_sorted_by_degree = [node for node, _ in degree_list]

    #return nodes_sorted_by_degree
    return degree_list

def getNodeInMostCycles(graph):

    cycles = nx.recursive_simple_cycles(graph)

    print(f"Number of cycles: {len(cycles)}")

    if len(cycles) == 0:
        return None

    appearances = {}
    for cycle in cycles:
        for node in cycle:
            if node[0] == 'C':
                if node in appearances:
                    appearances[node] += 1
                else:
                    appearances[node] = 1


    sortedAppearances = sorted(appearances.items(), key=lambda x:x[1],reverse=True)

    print("(Node in most cycles, number of cycles it appears in): ", sortedAppearances[0])

    return sortedAppearances[0][0]


def removeCyclesByNodeInMostCycles(graph):

    cycles = nx.recursive_simple_cycles(graph)

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

    print(f"{len(appearances)} nodes from {len(graph.nodes())} appear in a cycle")

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

                graph.add_edge(new_node, out_edge[1], relationship='substrate-reaction')
                graph.add_node(new_node, node_type='component')

            for in_edge in in_edges:
                new_node = "D" + str(i) + '_'  + node
                i += 1
                graph.add_edge(in_edge[0], new_node, relationship='reaction-substrate')
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

        # Measure
        poses = sugiyama(graph)
        countCrossings(graph, poses)


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
        
        if len(in_edges) == 0:
            graph.nodes[node]['node_type'] = 'source'
        elif len(out_edges) == 0:
            graph.nodes[node]['node_type'] = 'sink'



def rearangeSources(graph, pos):
    new_positions = {}
    for node in pos:
        if graph.in_degree(node) == 0:
            # print("source node:", node, "out degree:", graph.out_degree(node))
            neighbors = [n for n in graph.neighbors(node)]
            neighbor = neighbors[0]

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
    numCrossings = 0

    segments_x = []
    segments_y = []
    for edge in graph.edges():
        # bentley ottman does not cover vertial lines -> change x by y, no two adjacent nodes will be at the same height 
            segments_x.append(((pos[edge[0]][1],pos[edge[0]][0]), (pos[edge[1]][1],pos[edge[1]][0])))      
            segments_y.append(((pos[edge[0]][0],pos[edge[0]][1]), (pos[edge[1]][0],pos[edge[1]][1])))

    try:
        numCrossings = bent.isect_segments(segments_x, validate=True)
    except:
        try:
            numCrossings = bent.isect_segments(segments_y, validate=True)
        except:
            numCrossings = []
            print("Could not compute number of crossings")    
            
    print("Number of crossings:", len(numCrossings))    
    return len(numCrossings)

def isConnected(graph):
    H = graph.to_undirected()
    numCC = nx.number_connected_components(H)
    print(f"Number of connected components: {numCC}")

    if numCC > 1:
        return False

    return True

def getGraphInfo(graph,poses):
    numNodes = len(graph.nodes())
    print("Num Nodes:", numNodes)
    numEdges = len(graph.edges())
    print("Num Edges:", numEdges)
    numCrossings = countCrossings(graph,poses)
    H = graph.to_undirected()
    numCCs = nx.number_connected_components(H)
    numNodesCC = [len(H.subgraph(c).nodes()) for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    isConnected(graph)

    highestDegreeNode, highestDegree = getHighestDegreeNode(graph) 

    return numNodes, numEdges, numCrossings, numCCs, highestDegree, numNodesCC

def getCyclesInfo(graph):
    numCycles = len(nx.recursive_simple_cycles(graph))
    nodeInMostCycles = getNodeInMostCycles(graph)

    return numCycles, nodeInMostCycles

def getHighestDegreeNode(graph):
    '''
    Returns -> (node, degree)
    '''
    ordered_nodes = nodes_ordered_by_degree(graph)
    return ordered_nodes[0][0], ordered_nodes[0][1]

def sugiyama(graph, N = 1.5):

    g = grandalf.utils.convert_nextworkx_graph_to_grandalf(graph)


    class defaultview(object):
        w, h = 20, 20


    for v in g.C[0].sV:
        v.view = defaultview()

    sug = SugiyamaLayout(g.C[0])
    sug.init_all()  # roots = [V[0]])
    sug.draw(N)  # Calculate positions

    poses = {v.data: (v.view.xy[0], v.view.xy[1]) for v in g.C[0].sV}  # Extract positions
    poses = rearangeSources(graph,poses)

    return poses

def sugiyama_debug(graph):

    g = grandalf.utils.convert_nextworkx_graph_to_grandalf(graph)


    class defaultview(object):
        w, h = 20, 20


    for v in g.C[0].sV:
        v.view = defaultview()

    sug = SugiyamaLayout(g.C[0])
    sug.init_all()  # roots = [V[0]])
    
    sug.draw_step()  # Calculate positions

    poses = {v.data: (v.view.xy[0], v.view.xy[1]) for v in g.C[0].sV}  # Extract positions
    poses = rearangeSources(graph, poses)
    
    return poses

def getLargestCC(graph):
    connected = isConnected(graph)
    edges = graph.edges()

    if not connected:
        H = graph.to_undirected()
        largest_cc = max(nx.connected_components(H), key=len)
        subGraph = graph.subgraph(largest_cc).copy()
        subGraph.to_directed()

        return subGraph
    return -1

def getConnectedComponents(graph):
    H = graph.to_undirected()
    S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    nth = input("Select nth CC:\n")
    n = int(nth)
    subGraph = graph.subgraph(S[n]).copy()
    subGraph.to_directed()

    return subGraph

def getNodeLabel(name):
    return name.split("_")[-1]   

def retrieveNodeNames():
    url = "https://rest.kegg.jp/list/compound"

    response = requests.get(url)
    compounds = dict()

    if response.status_code == 200:
        lines = response.text.split("\n")
        for compound in lines:
            info = compound.split("\t")
            if len(info) > 1:
                compoundId = info[0]            
                compoundName = info[1].split(';')[0]
                compounds[compoundId] = compoundName

    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    
    return compounds

def parseGraph(graph, node_positions, compounds):
    graphInfo = {}

    node_colors = nx.get_node_attributes(graph, "color")
    node_types = nx.get_node_attributes(graph, "node_type")
    node_cids = nx.get_node_attributes(graph, "cid")

    print(compounds)
    graphInfo['nodes'] = []
    for node in graph.nodes():
        nodeInfo = {}
        nodeInfo['id'] = node
        if graph.nodes[node]['node_type'] != 'reaction':
            nodeInfo['label'] = compounds[getNodeLabel(node)]
        else:
            nodeInfo['label'] = node

        nodeInfo['x'] = node_positions[node][0]
        nodeInfo['y'] = node_positions[node][1]
        nodeInfo['color'] = node_colors[node]
        nodeInfo['type'] = node_types[node]
        nodeInfo['cid'] = node_cids[node]

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

    print(getGraphInfo)
    return str(graphInfo)

def parseJsonToNx(graphInfo):
    print(graphInfo)
    json_data = json.loads(graphInfo)
    graph = nx.DiGraph()

    # Add nodes
    for node_info in json_data['nodes']:
        node_id = node_info['id']
        node_label = node_info['label']
        node_color = node_info['color']
        node_type = node_info['type']
        node_position = (node_info['x'], node_info['y'])
        graph.add_node(node_id, label=node_label, color=node_color, node_type=node_type, position=node_position)

    # Add edges
    for edge_info in json_data['edges']:
        from_node = edge_info['from']
        to_node = edge_info['to']
        relationship = edge_info['relationship']
        graph.add_edge(from_node, to_node, relationship=relationship)

    return graph

def getNodeInfo(graph, node):
    predecessors, successors = [],[]
    print(node)
    print("Predecessors:")
    for pred in graph.predecessors(node):
        print("- ", pred)
        predecessors.append(pred)
    print("Successors")
    for suc in graph.successors(node):
        print("- ", suc)
        successors.append(suc)
    
    if len(predecessors) == 0:
        predecessors.append("None")
    if len(successors) == 0:
        successors.append("None")

    return predecessors, successors

def countLevels(poses):

    # for node in centralNodes:
    #     centralLevel = poses[node][1]
    #     print("Central Node:", node, "Central Level:", centralLevel)

    levels = dict()
    new_poses = dict()

    for node in poses:
        level = poses[node][1]
        if level in levels:
            levels[level].append(node)
        else:
            levels[level] = [node]
        

    for level in levels:
        nodes = [nodes for nodes in levels[level]]  
        nodes.sort(key=lambda x: poses[x][0])

        if nodes[0][0] != 'R':
            # print("Compounds")
            offset = 1

            for node in nodes:
                if offset == 1:
                    offset = -1
                else:
                    offset = 1
                # print(node, poses[node][0])
                new_poses[node] = (poses[node][0], level*2 + 15*offset)
        else:
            # print("Reactions")
            for node in nodes:
                # print(node, poses[node][0])

                new_poses[node] = (poses[node][0], level*2)
            
    print("Number of Levels: ", len(levels))
    for i, key in enumerate(sorted(levels)):
        print(i,':',key)
    return new_poses
    # print(levels)

def staggerLayers(graph, poses):
    #Computing betweeness
    # betCent = nx.betweenness_centrality(graph, normalized=True, endpoints=True)

    #Descending order sorting betweeness
    # betCent_sorted=sorted(betCent.items(), key=lambda item: item[1],reverse=True)

    # print("Bet centrality", betCent_sorted)

    # H = graph.to_undirected()
    # center = nx.center(H)

    return countLevels(poses)

def checkMaxCCSize(graph):

    H = graph.to_undirected()
    S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

    while len(S[0].nodes()) > 1000:
        node, degree = getHighestDegreeNode(graph)
        splitHighDegreeComponents(graph,degree)

        print("Largest CC size ", len(S[0].nodes()))
        print("Node info: ", node, degree)

        H = graph.to_undirected()
        S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

def defineNodeCID(graph, nodes, cid):
    for node in nodes:
        graph.nodes[node]['cid'] = cid
        # print(node, graph.nodes[node]['cid'])

def getGraphPositions(graph, N = 1.5):
    connected = isConnected(graph)
    poses = {}
    changeSourceAndSinkNodeType(graph)
    setColorNodeType(graph)  

    if connected:
        poses = sugiyama(graph, N)
        defineNodeCID(graph, graph.nodes(), 0)

    else:
            H = graph.to_undirected()
            S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

            xMax = 0
            currentMaxX = 0
            for cid, c in enumerate(S):
                subGraph = graph.subgraph(c).copy()
                subGraph.to_directed()
                new_poses = sugiyama(subGraph)
                for pos in new_poses:
                    new_poses[pos] = (currentMaxX + new_poses[pos][0], new_poses[pos][1])
                    if new_poses[pos][0] > xMax:
                        xMax = new_poses[pos][0]
                poses.update(new_poses)
                currentMaxX = xMax + 200
                
                defineNodeCID(graph, subGraph.nodes(), cid)

    poses = staggerLayers(graph, poses)
    return poses
