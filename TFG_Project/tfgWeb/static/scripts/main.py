
import networkx as nx
from pyvis.network import Network
import sys

import auxiliar_methods as funcs
import layouts as lyts

import matplotlib.pyplot as plt


G = nx.DiGraph()    
reactions = []
poses = {}

def main():
    print("Reading Graph")
    reactions, components = funcs.read_graph(G)
    while True:
        op = input('''
┌───────────────────────────────────────────────────────────┐
|  Select operation:                                        |
|     0: Visualise graph                                    |
|     1: Show graph information                             |
|     2: Split high degree components                       |
|     3: Remove cycles                                      |
|     4: Get node information                               |                
|     5: Duplicate node                                     |
|     6: Delete node                                        |
|     7: Delete edge                                        |
|     8: Visualise connected component (largest first)      |
└───────────────────────────────────────────────────────────┘                 
(q) Quit
''')

        match op:
            case '0':

                funcs.changeSourceAndSinkNodeType(G)
                colors = funcs.setColorNodeType(G)                
                poses = funcs.sugiyama(G)

                nx.draw(G, pos=poses, with_labels=True, node_color=colors)
                
                plt.show()

            case '1':
                poses = funcs.sugiyama(G)

                funcs.printGraphInfo(G, poses)

            case '2':

                threshholdInput = input("Set threshhold: (default value == 10)")
                threshhold = 10
                if threshholdInput.isdigit():
                    threshhold = int(threshholdInput) #default value = 10

                funcs.splitHighDegreeComponents(G, threshhold)

            case '3':

                funcs.removeCyclesByNodeInMostCycles(G)
            
            case '4':
                
                node = input("Write node id:")
                funcs.printNodeInfo(G, node)

            case '5':
                node = input("Write node id:")
                funcs.duplicateNode(G, node)
            case '6':
                node = input("Write node id:")
                G.remove_node(node)
            case '7':
                origin_node = input("Write origin node id:")
                destination_node = input("Write destination node id:")
                G.remove_edge(origin_node, destination_node)

            case '8':

                subGraph = funcs.getConnectedComponents(G)
                
                funcs.changeSourceAndSinkNodeType(subGraph)
                colors = funcs.setColorNodeType(subGraph)                
                poses = funcs.sugiyama(subGraph)

                nx.draw(subGraph, pos=poses, with_labels=True, node_color=colors)
                
                plt.show()

            case 'p':

                funcs.changeSourceAndSinkNodeType(G)
                colors = funcs.setColorNodeType(G)   
                poses = funcs.sugiyama(G)

                funcs.parseGraph(G,poses)
                
            case 'q':
                return
            
                
def oldExecution():

    reactions, components = funcs.read_graph(G)

    funcs.isConnected(G)
    
    funcs.removeCyclesByNodeInMostCycles(G)
    result = funcs.getLargestCC(G)

    if result == -1: # 1 CC

        funcs.changeSourceAndSinkNodeType(G)

        colors = funcs.setColorNodeType(G)
        
        poses = funcs.sugiyama(G)
        

    else: # largest CC

        funcs.changeSourceAndSinkNodeType(result)

        colors = funcs.setColorNodeType(result)
        
        poses = funcs.sugiyama(result)
    

    funcs.rearangeSources(G, poses)
    # funcs.countCrossings(G,poses)

    funcs.parseGraph(G, poses)

    nx.draw(G, pos=poses, with_labels=True, node_color=colors)
    
    plt.show()

    # nt = Network(directed=True)
    # nt.from_nx(graph)
    # nt.show_buttons(filter_=['layout'])
    # nt.show('nx.html', notebook=False)

if __name__ == "__main__":
    main()