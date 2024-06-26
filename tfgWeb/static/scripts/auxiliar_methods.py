import networkx as nx
import sys
import os

import grandalf
from grandalf.layouts import SugiyamaLayout

import poly_point_isect as bent

import json
import requests

import numpy as np

import math
from scipy.stats import hmean

from queue import PriorityQueue

import signal
from contextlib import contextmanager

try:
    class TimeoutException(Exception): pass

    @contextmanager
    def time_limit(seconds):
        def signal_handler(signum, frame):
            raise TimeoutException("Timed out!")
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
except:
    print("No timeout for removing cycles.")

DEBUG = False

MAX_SIZE_LARGE = 1000
MAX_SIZE_MEDIUM = 300
'''
Reading the graph
'''
def read_graph(graph, check = True):
    nx.set_node_attributes(graph, {})
    path = sys.argv[1]
    info = read_graph_from_file(graph, path)

    if check:
        checkMaxCCSize(graph)

def read_graph_from_file(graph, path):
    for line in open(path):
        reaction, substrates, products = line.rstrip().split(" : ")

        graph.add_node(reaction, node_type='reaction', status='original')

        for substrate in substrates.split(" "):

            graph.add_edge(substrate, reaction, relationship='substrate-reaction')
            graph.add_node(substrate, node_type='component', status='original')


        for product in products.split(" "):
            graph.add_edge(reaction, product, relationship='reaction-substrate')
            graph.add_node(product, node_type='component', status='original')

'''
Parsing the graph
'''
def parseGraph(graph, node_positions, compounds):
    graphInfo = {}

    node_colors = nx.get_node_attributes(graph, "color")
    node_types = nx.get_node_attributes(graph, "node_type")
    node_cids = nx.get_node_attributes(graph, "cid")
    node_status = nx.get_node_attributes(graph, "status")

    # if DEBUG: print(compounds)
    graphInfo['nodes'] = []
    for node in graph.nodes():
        nodeInfo = {}
        nodeInfo['id'] = node
        if graph.nodes[node]['node_type'] != 'reaction':
            nodeInfo['label'] = compounds[getNodeLabel(node)]
        else: nodeInfo['label'] = getNodeLabel(node)

        nodeInfo['x'] = node_positions[node][0]
        nodeInfo['y'] = node_positions[node][1]
        nodeInfo['color'] = node_colors[node]
        nodeInfo['type'] = node_types[node]
        nodeInfo['cid'] = node_cids[node]
        nodeInfo['status'] = node_status[node]

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

    # if DEBUG: print(getGraphInfo)
    return str(graphInfo)

def parseJsonToNx(graphInfo):
    # if DEBUG: print(graphInfo)
    print("Parsing to NX")
    json_data = json.loads(graphInfo)
    graph = nx.DiGraph()

    # Add nodes
    for node_info in json_data['nodes']:
        node_id = node_info['id']
        node_label = node_info['label']
        node_color = node_info['color']
        node_type = node_info['type']
        node_position = (node_info['x'], node_info['y'])
        status= node_info['status']
        graph.add_node(node_id, label=node_label, color=node_color, node_type=node_type, position=node_position, status=status)

    # Add edges
    for edge_info in json_data['edges']:
        from_node = edge_info['from']
        to_node = edge_info['to']
        relationship = edge_info['relationship']
        graph.add_edge(from_node, to_node, relationship=relationship)

    print("Finished parsing to NX")

    return graph

'''
Graph Modifiers
'''

def checkMaxCCSize(graph):

    if len(graph.nodes()) >= MAX_SIZE_LARGE:
        # print("Large Graph")
        res = checkLargeGraph(graph)
        updateGraphFromSubgraphs(graph, res)

        res = checkMediumGraph(graph)
        updateGraphFromSubgraphs(graph, res)

        removeAllCycles(graph)

    elif len(graph.nodes()) > MAX_SIZE_MEDIUM:
        # print("Medium Graph")

        res = checkMediumGraph(graph)
        updateGraphFromSubgraphs(graph, res)
        
        removeAllCycles(graph)

        

    else:
        # print("Small Graph")

        checkSmallGraph(graph)
        
        removeAllCycles(graph)

        
def removeAllCycles(graph):
    H = graph.to_undirected()
    S = [graph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    for s in S:
        numReactions = [node for node in s.nodes() if graph.nodes[node]['node_type'] == 'reaction']

        if len(numReactions) > 1:
            try:
                try:
                    with time_limit(20):
                        node = getNodeInMostCycles(s)   

                    while node:
                        duplicateNode(s, node)
                        duplicateNode(graph, node)
                        try:
                            with time_limit(10):
                                node = getNodeInMostCycles(s)                
                        except TimeoutException as e:
                            print("Timed out!")

                except TimeoutException as e:
                    print("Timed out!")
            except:
                node = getNodeInMostCycles(s)   
                while node:
                    duplicateNode(s, node)
                    duplicateNode(graph, node)

                    node = getNodeInMostCycles(s)                

            

def splitHighDegreeComponents(graph, threshhold, duplicationLetter = 'D'):

    ordered_nodes = nodes_ordered_by_degree(graph)
    if DEBUG: print(f"Initial number of nodes: {graph.number_of_nodes()}")
    for node, degree in ordered_nodes:
        if degree >= threshhold and graph.nodes[node]['node_type'] != 'reaction':
                duplicateNode(graph, node, duplicationLetter)

    if DEBUG: print(f"Final number of nodes: {graph.number_of_nodes()}")


def duplicateNode(graph, node, letter = 'D'):

    if graph.nodes[node]['status'] != 'duplicated':
        out_edges = graph.out_edges([node])
        in_edges = graph.in_edges([node])
        node_type = graph.nodes[node]['node_type']

        i = 0
        for out_edge in out_edges:
            new_node = letter + str(i) + '_' + node
            i += 1
            graph.add_edge(new_node, out_edge[1], relationship='substrate-reaction')
            graph.add_node(new_node, node_type=node_type, status='duplicated')

        for in_edge in in_edges:
            new_node = letter + str(i) + '_'  + node
            i += 1
            graph.add_edge(in_edge[0], new_node, relationship='reaction-substrate')
            graph.add_node(new_node, node_type=node_type, status='duplicated')

        graph.remove_node(node)





def removeCyclesByNodeInMostCycles(graph):

    cycles = nx.recursive_simple_cycles(graph)

    if DEBUG: print(f"Number of cycles: {len(cycles)}")

    appearances = {}
    for cycle in cycles:
        for node in cycle:
            if node[0] == 'C':
                if node in appearances:
                    appearances[node] += 1
                else:
                    appearances[node] = 1


    sortedAppearances = sorted(appearances.items(), key=lambda x:x[1],reverse=True)

    if DEBUG: print(f"{len(appearances)} nodes from {len(graph.nodes())} appear in a cycle")

    while True:
        if DEBUG: print("(Node in most cycles, number of cycles it appears in): ", sortedAppearances[0])
        node = next(iter(sortedAppearances))[0]
        duplicateNode = input(f"Do you want to duplicate {node}? (Y/n)")
        if duplicateNode == "y" or duplicateNode == "Y":
            if DEBUG: print(f"Initial number of nodes: {graph.number_of_nodes()}")

            out_edges = graph.out_edges([node])
            in_edges = graph.in_edges([node])

            i = 0
            for out_edge in out_edges:
                new_node = "D" + str(i) + '_' + node
                i += 1

                graph.add_edge(new_node, out_edge[1], relationship='substrate-reaction')
                graph.add_node(new_node, node_type='component', status='duplicated')

            for in_edge in in_edges:
                new_node = "D" + str(i) + '_'  + node
                i += 1
                graph.add_edge(in_edge[0], new_node, relationship='reaction-substrate')
                graph.add_node(new_node, node_type='component', status='duplicated')

            graph.remove_node(node)


        else:
            return

        if DEBUG: print(f"Final number of nodes: {graph.number_of_nodes()}")
        cycles = nx.recursive_simple_cycles(graph)
        
        if DEBUG: print(f"Number of cycles: {len(cycles)}")
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
        if DEBUG: print(f"Number of connected components: {nx.number_connected_components(H)}")

        # Measure
        poses = sugiyama(graph)
        countCrossings(graph, poses)


def setColorNodeType(graph):

    node_colors = {node: get_color(data['node_type'],data['status']) for node, data in graph.nodes(data=True)}
    nx.set_node_attributes(graph, node_colors, 'color')

    colors = [data['color'] for _, data in graph.nodes(data=True)]

    return colors

def changeSourceAndSinkNodeType(graph):
    for node in graph.nodes():
        in_edges = graph.in_edges(node)
        out_edges = graph.out_edges(node)

        if len(in_edges) == 0:
            graph.nodes[node]['node_type'] = 'source'
        elif len(out_edges) == 0:
            graph.nodes[node]['node_type'] = 'sink'


def defineNodeCID(graph, nodes, cid):
    for node in nodes:
        graph.nodes[node]['cid'] = cid
        if DEBUG: print(node, graph.nodes[node]['cid'])

def reverseReaction(graph, reaction):

    in_edges = list(graph.in_edges(reaction))
    out_edges = list(graph.out_edges(reaction))

    if graph.nodes[reaction]['status'] == 'reversed':
        graph.nodes[reaction]['status'] = 'original'
    else:
        graph.nodes[reaction]['status'] = 'reversed'
        
    graph.remove_edges_from(in_edges)
    graph.remove_edges_from(out_edges)

    for edge in in_edges:
        graph.add_edge(edge[1],edge[0], relationship='reaction-substrate')

    for edge in out_edges:
        graph.add_edge(edge[1],edge[0], relationship='substrate-reaction')


'''
Information
'''
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
    degree_list = [(node, degree) for node, degree in graph.degree(nodes) if not graph.nodes[node]['node_type'] == 'reaction']

    # Sort the list by degree in descending order
    degree_list.sort(key=lambda x: x[1], reverse=True)


    # Extract the nodes from the sorted list
    #nodes_sorted_by_degree = [node for node, _ in degree_list]

    #return nodes_sorted_by_degree
    return degree_list

def getNodeInMostCycles(graph):

    cycles = nx.recursive_simple_cycles(graph)

    if DEBUG: print(f"Number of cycles: {len(cycles)}")

    if len(cycles) == 0:
        return None

    appearances = {}
    for cycle in cycles:
        for node in cycle:
            if graph.nodes[node]['node_type'] == 'component' and graph.nodes[node]['status'] == 'original':
                if node in appearances:
                    appearances[node] += 1
                else:
                    appearances[node] = 1


    # sortedAppearances = sorted(appearances.items(), key=lambda x:x[1],reverse=True)
    sortedAppearances = sorted(appearances.items(), key=lambda x: (-x[1], x[0]))
    if DEBUG: print("(Node in most cycles, number of cycles it appears in): ", sortedAppearances[0])

    return sortedAppearances[0][0]

def get_color(node_type, status):
    if node_type == 'reaction':
        if status == 'original':
            return 'blue'
        else:
            return '#800080'
    if node_type == 'source':
        return 'orange'
    if node_type == 'sink':
        return 'green'
    return 'red'

def getNumSources(graph):
    sources = 0

    for node in graph.nodes():
        if graph.in_degree(node) == 0:
            sources += 1

    return sources
def countCrossings(graph,pos):

    numCCs = getNumCCs(graph)
    totalNumCrossings = 0

    H = graph.to_undirected()
    S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

    for i in range(0,numCCs):
        numCrossings = 0
        

        segments_x = []
        # segments_y = []
        for edge in S[i].edges():
            # bentley ottman does not cover vertial lines -> change x by y, no two adjacent nodes will be at the same height
            segments_x.append(((pos[edge[0]][1],pos[edge[0]][0]), (pos[edge[1]][1],pos[edge[1]][0])))
                # segments_y.append(((pos[edge[0]][0],pos[edge[0]][1]), (pos[edge[1]][0],pos[edge[1]][1])))

        numCrossings = bent.isect_segments(segments_x, validate=True)
        if DEBUG: print(f"{len(numCrossings)} in CC {i}")
        totalNumCrossings += len(numCrossings)
        # try:
        # except:
        #     try:
        #         numCrossings = bent.isect_segments(segments_y, validate=True)
        #     except:
        #         numCrossings = []
        #         if DEBUG: print("Could not compute number of crossings")

    if DEBUG: print("Number of crossings:", numCrossings)
    return totalNumCrossings

def isConnected(graph):
    H = graph.to_undirected()
    numCC = nx.number_connected_components(H)
    if DEBUG: print(f"Number of connected components: {numCC}")

    if numCC > 1:
        return False

    return True

def getNumCCs(graph):
    H = graph.to_undirected()
    return  nx.number_connected_components(H)

def getFrequencies(graph):
    H = graph.to_undirected()
    numNodesCC = [len(H.subgraph(c).nodes()) for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    frequencies = dict()
    for n in numNodesCC:
        if n in frequencies:
            frequencies[n] += 1
        else:
            frequencies[n] = 1
    return frequencies
def getGraphInfo(graph,poses):
    numNodes = len(graph.nodes())
    if DEBUG: print("Num Nodes:", numNodes)
    numEdges = len(graph.edges())
    if DEBUG: print("Num Edges:", numEdges)
    numCrossings = countCrossings(graph,poses)
    H = graph.to_undirected()
    numCCs = nx.number_connected_components(H)
    numNodesCC = [len(H.subgraph(c).nodes()) for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    frequencies = dict()
    for n in numNodesCC:
        if n in frequencies:
            frequencies[n] += 1
        else:
            frequencies[n] = 1
    isConnected(graph)

    highestDegreeNodes, highestDegree = getHighestDegreeNodes(graph)
    if DEBUG: print("High Degree nodes:", highestDegreeNodes)

    infoEdgeLengths = computeDistances(graph, poses)
    infoEdgeAngles = computeAngles(graph, poses)

    # return numNodes, numEdges, numCrossings, numCCs, highestDegreeNodes, highestDegree, infoEdgeLengths, infoEdgeAngles, frequencies
    return numNodes, numEdges, numCrossings, numCCs, highestDegreeNodes, highestDegree, numNodesCC, infoEdgeLengths, infoEdgeAngles

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

def getHighestDegreeNodes(graph):
    '''
    Returns -> [(node)], degree
    '''
    ordered_nodes = nodes_ordered_by_degree(graph)
    result = []
    for node in ordered_nodes:
        if node[1] == ordered_nodes[0][1]:
            result.append(node[0])
    return result, ordered_nodes[0][1]


def computeDistances(graph,poses):
    res = []
    maxLengthEdge = 0
    sumLengths = 0
    for edge in graph.edges():
        euclid_dist = np.linalg.norm(np.array(poses[edge[0]]) - np.array(poses[edge[1]]))
        res.append(euclid_dist)
        sumLengths += euclid_dist

        if euclid_dist > maxLengthEdge:
            maxLengthEdge = euclid_dist
    
    if DEBUG: print(np.mean(res))
    return round(np.mean(res),2), round(maxLengthEdge,2), round(sumLengths,2)


def computeAngles(graph,poses):
    res = []
    horizontalLines = 0
    for edge in graph.edges():
        
        vector_1 = np.array(poses[edge[0]]) - np.array(poses[edge[1]])
        vector_2 = [0, -1]

        unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
        unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        angle = np.arccos(dot_product)

        res.append(angle)
        
        if angle > math.pi/4 and angle < 3*math.pi/4: horizontalLines += 1

        if DEBUG: print(angle)

    if DEBUG: print(hmean(res))
    if DEBUG: print(np.mean(res), np.std(res))
    if DEBUG: print("Percentage 'horizontal' lines", horizontalLines/len(res))
    return round(np.mean(res), 2),  round(np.std(res),2), round(horizontalLines/len(res),2)

''''
Positions updaters
'''
def rearangeSources(graph, pos):
    new_positions = {}
    for node in pos:
        if graph.in_degree(node) == 0:
            # if DEBUG: print("source node:", node, "out degree:", graph.out_degree(node))
            neighbors = [n for n in graph.neighbors(node)]
            neighbor = neighbors[0]

            posNeigh = pos[neighbor]
            # if DEBUG: print("Neighbor:", neighbor, "NPosition:", posNeigh)
            newPosX = 0
            if pos[node][0] < posNeigh[0]:
                newPosX = posNeigh[0]-40
            else:
                newPosX = posNeigh[0]+40

            # if the only neighbor lower of neighbor is node, put node at same x as neighbor
            belowNeighbors = 0
            for neigh in graph.predecessors(neighbor):
                # if DEBUG: print(neigh, pos[neigh])
                if pos[neigh][1] < posNeigh[1]:
                    belowNeighbors += 1

            for neigh in graph.successors(neighbor):
                # if DEBUG: print(neigh, pos[neigh])
                if pos[neigh][1] < posNeigh[1]:
                    belowNeighbors += 1


            # if DEBUG: print(belowNeighbors)

            # it is the only under neigh, we put it under the upper one
            if belowNeighbors == 1:
                newPosX = posNeigh[0]

            new_positions[node] = (newPosX, posNeigh[1] - 40)
        else:
            new_positions[node] = pos[node]

    return new_positions
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

def getConnectedComponents(graph, n):
    H = graph.to_undirected()
    S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    subGraph = graph.subgraph(S[n]).copy()
    subGraph.to_directed()

    return subGraph

def getNodeLabel(name):
    if "_" in name:
        return name.split("_")[-1]
    else: return name
 

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
                compoundName = info[1].split(';')[0].replace("'", '`')
                compounds[compoundId] = compoundName

    else:
        if DEBUG: print("Failed to retrieve data. Status code:", response.status_code)

    return compounds


def getNodeInfo(graph, node):
    predecessors, successors = [],[]
    if DEBUG: print(node)
    if DEBUG: print("Predecessors:")
    for pred in graph.predecessors(node):
        if DEBUG: print("- ", pred)
        predecessors.append(pred)
    if DEBUG: print("Successors")
    for suc in graph.successors(node):
        if DEBUG: print("- ", suc)
        successors.append(suc)

    if len(predecessors) == 0:
        predecessors.append("None")
    if len(successors) == 0:
        successors.append("None")

    return predecessors, successors

'''
Positions
'''
def getDefaultSugiyamaPositions(graph):
    poses = {}
    changeSourceAndSinkNodeType(graph)
    setColorNodeType(graph)
    defineNodeCID(graph, graph.nodes(), 0)

    g = grandalf.utils.convert_nextworkx_graph_to_grandalf(graph)


    class defaultview(object):
        w, h = 20, 20


    for v in g.C[0].sV:
        v.view = defaultview()

    sug = SugiyamaLayout(g.C[0])
    sug.init_all()  # roots = [V[0]])
    sug.draw()  # Calculate positions

    poses = {v.data: (v.view.xy[0], v.view.xy[1]) for v in g.C[0].sV}  # Extract positions

    return poses


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
    poses  = rearangeSources(graph,poses)
    poses = staggerLayers(poses)

    return poses



def staggerLayers(poses):

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
            # if DEBUG: print("Compounds")
            offset = 1

            for node in nodes:
                if offset == 1:
                    offset = -1
                else:
                    offset = 1
                # if DEBUG: print(node, poses[node][0])
                new_poses[node] = (poses[node][0], level*2 + 15*offset)
        else:
            # if DEBUG: print("Reactions")
            for node in nodes:
                # if DEBUG: print(node, poses[node][0])

                new_poses[node] = (poses[node][0], level*2)

    if DEBUG: print("Number of Levels: ", len(levels))
    for i, key in enumerate(sorted(levels)):
        if DEBUG: print(i,':',key)
    return new_poses




def getGraphPositions(graph, N = 1.5):
    freqs = dict()
    connected = isConnected(graph)
    poses = {}
    changeSourceAndSinkNodeType(graph)
    setColorNodeType(graph)

    if connected:
        poses = sugiyama(graph, N)
        defineNodeCID(graph, graph.nodes(), 0)

        freqs[len(graph.nodes())] = 1

    else:
            H = graph.to_undirected()
            S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

            xMax = 0
            currentMaxX = 0
            for cid, c in enumerate(S):
                subGraph = graph.subgraph(c).copy()
                subGraph.to_directed()

                if len(subGraph.nodes()) in freqs:
                    freqs[len(subGraph.nodes())]+= 1
                else:
                    freqs[len(subGraph.nodes())] = 1

                new_poses = sugiyama(subGraph)
                
                for pos in new_poses:
                    new_poses[pos] = (currentMaxX + new_poses[pos][0], new_poses[pos][1])
                    if new_poses[pos][0] > xMax:
                        xMax = new_poses[pos][0]
                currentMaxX = xMax + 200
            
                poses.update(new_poses)

                defineNodeCID(graph, subGraph.nodes(), cid)

    return poses



def updateGraphFromSubgraphs(original_graph, subgraphs):
    original_graph.clear()  # Clear the original graph's nodes and edges
    for subgraph in subgraphs:
        original_graph.add_nodes_from(subgraph.nodes(data=True))
        original_graph.add_edges_from(subgraph.edges(data=True))


def checkLargeGraph(graph):
    q = PriorityQueue()

    H = graph.to_undirected()
    S = [graph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

    for s in S:
        size = len(s.nodes())
        q.put((size*(-1),s))
    
    subGraph = q.get()[1]
    size = len(subGraph.nodes())
    while size >=  MAX_SIZE_LARGE:
        _, degree = getHighestDegreeNode(subGraph)
        splitHighDegreeComponents(subGraph, degree, 'L')

        H = subGraph.to_undirected()
        S = [subGraph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

        for s in S:
            size = len(s.nodes())
            q.put((size*(-1),s))
        
        subGraph = q.get()[1]
        size = len(subGraph.nodes())
    
    result = [subGraph]

    while not q.empty():
        result.append(q.get()[1])

    return result

def checkMediumGraph(graph):
    q = PriorityQueue()

    H = graph.to_undirected()
    S = [graph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

    suma = 0
    for s in S:
        size = len(s.nodes())
        q.put((size*(-1),s))
    
    subGraph = q.get()[1]
    size = len(subGraph.nodes())
    while size >=  MAX_SIZE_MEDIUM:
        degree = getConnectedThreshold(subGraph)
        splitHighDegreeComponents(subGraph, degree, 'M')

        H = subGraph.to_undirected()
        S = [subGraph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]

        for s in S:
            size = len(s.nodes())
            q.put((size*(-1),s))
        
        subGraph = q.get()[1]
        size = len(subGraph.nodes())
    
    result = [subGraph]

    while not q.empty():
        result.append(q.get()[1])

    return result

def checkSmallGraph(graph):
    degree = getConnectedThreshold(graph)
    splitHighDegreeComponents(graph, degree, 'S')
    
    while degree > 12:
        print(degree)

        H = graph.to_undirected()
        S = [graph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
        
        degree = getConnectedThreshold(S[0])
        splitHighDegreeComponents(graph, degree, 'S')



def getNumIsolatedReactions(graph):
    H = graph.to_undirected()
    S = [graph.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
    res = 0
    for s in S:
        numReactions = [node for node in s.nodes() if graph.nodes[node]['node_type'] == 'reaction']
        if len(numReactions) == 1: res += 1  
    return res

def getConnectedThreshold(graph):

    _, i = getHighestDegreeNode(graph)
    H = graph.copy()

    while True:
        splitHighDegreeComponents(H,i)

        if getNumCCs(H) != 1:
            
            return i
        H = graph.copy()

        i -= 1 