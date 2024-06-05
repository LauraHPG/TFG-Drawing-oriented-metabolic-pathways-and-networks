
import networkx as nx
import sys

import auxiliar_methods as funcs

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
|     9: Generate graph cycle-crossings                     |
|     10: Generate graph highDegree-crossings               |
└───────────────────────────────────────────────────────────┘                 
(q) Quit
''')

        match op:
            case '0':


                poses = funcs.getGraphPositions(G)
                colors = funcs.setColorNodeType(G)  

                # depth = input("Do you want to arrange it by depth? (y/n)")

                nx.draw(G, pos=poses, with_labels=True, node_color=colors)
                
                plt.show()

            case '1':


                poses = funcs.getGraphPositions(G, 1.5)


                funcs.getGraphInfo(G, poses)

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
                funcs.getNodeInfo(G, node)

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
                nth = input("Select nth CC:")
                n = int(nth)

                subGraph = funcs.getConnectedComponents(G, n)
                
                funcs.changeSourceAndSinkNodeType(subGraph)
                colors = funcs.setColorNodeType(subGraph)                
                poses = funcs.sugiyama(subGraph)

                funcs.getGraphInfo(subGraph, poses)
                nx.draw(subGraph, pos=poses, with_labels=True, node_color=colors)
                
                plt.show()
            
            case '9':
                x_data = []
                y_data = []
                
                x_labels = []
                
                plt.ion()  # Turn on interactive mode
                fig, ax = plt.subplots()
                line, = ax.plot(x_data, y_data)

                numCycles = len(nx.recursive_simple_cycles(G))
                nodeInMostCycles = funcs.getNodeInMostCycles(G)

                poses = funcs.getGraphPositions(G, 1.5)

                numCrossings = funcs.countCrossings(G,poses)
                i = 0
                
                while numCycles > 0:

                    x_data.append(i)
                    y_data.append(numCrossings)
                    x_labels.append(highestDegreeNode)
                    
                    line.set_xdata(x_data)
                    line.set_ydata(y_data)
                    
                    ax.set_xticks(x_data)  # Set the x-ticks to the positions in x_data
                    ax.set_xticklabels(x_labels)  # Set the x-tick labels to the labels in x_labels
                    ax.set_xticklabels(x_labels, rotation=90) 

                    ax.relim()  # Recalculate limits
                    ax.autoscale_view()  # Autoscale the view to fit the data
                    plt.draw()
                    plt.pause(0.1)  # Pause to allow the plot to update

                    funcs.duplicateNode(G, nodeInMostCycles)


                    numCycles = len(nx.recursive_simple_cycles(G))
                    nodeInMostCycles = funcs.getNodeInMostCycles(G)

                    poses = funcs.getGraphPositions(G, 1.5)
                    numCrossings = funcs.countCrossings(G,poses)
                    highestDegree -= 1
                    i += 1

                plt.ioff()
                plt.show()

            case '10':
                x_data = []
                y_data = []
                
                x_labels = []
                
                plt.ion()  # Turn on interactive mode
                fig, ax = plt.subplots()
                line, = ax.plot(x_data, y_data)

                highestDegreeNode, highestDegree = funcs.getHighestDegreeNode(G) 
                poses = funcs.getGraphPositions(G, 1.5)

                numCrossings = funcs.countCrossings(G,poses)
                
                for i in range(0, highestDegree):

                    x_data.append(i)
                    y_data.append(numCrossings)
                    x_labels.append(highestDegreeNode)
                    
                    line.set_xdata(x_data)
                    line.set_ydata(y_data)
                    
                    ax.set_xticks(x_data)  # Set the x-ticks to the positions in x_data
                    ax.set_xticklabels(x_labels)  # Set the x-tick labels to the labels in x_labels
                    ax.set_xticklabels(x_labels, rotation=90) 
                    
                    ax.relim()  # Recalculate limits
                    ax.autoscale_view()  # Autoscale the view to fit the data
                    plt.draw()
                    plt.pause(0.1)  # Pause to allow the plot to update


                    funcs.splitHighDegreeComponents(G, highestDegree - i)

                    poses = funcs.getGraphPositions(G, 1.5)
                    numCrossings = funcs.countCrossings(G,poses)
                    highestDegree -= 1

                plt.ioff()
                plt.show()

            case '11':
                poses = funcs.getGraphPositions(G)
                funcs.computeDistances(G, poses)
            
            case '12':
                poses = funcs.getGraphPositions(G)
                funcs.computeAngles(G, poses)
            
            case '13':
                poses = funcs.getDefaultSugiyamaPositions(G)
                colors = funcs.setColorNodeType(G)  

                # depth = input("Do you want to arrange it by depth? (y/n)")

                nx.draw(G, pos=poses, with_labels=True, node_color=colors)
                
                plt.show()
            case 'p':

                funcs.changeSourceAndSinkNodeType(G)
                poses = funcs.sugiyama(G)

                funcs.parseGraph(G,poses)
            case 'x':
                funcs.retrieveNodeNames()
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