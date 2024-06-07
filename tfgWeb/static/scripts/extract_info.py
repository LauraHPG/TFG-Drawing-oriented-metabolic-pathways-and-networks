import networkx as nx
import sys
import auxiliar_methods as funcs
import matplotlib.pyplot as plt
import os
import time

G = nx.DiGraph()    
reactions = []
poses = {}

input_directory = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/tfgWeb/static/inputGraphs'
output_directory = '/home/laura/Desktop/Results'  # Specify your output directory

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get a list of all files in the input directory
filenames = os.listdir(input_directory)

# Filter out directories, only keep files
filenames = [f for f in filenames if os.path.isfile(os.path.join(input_directory, f))]

# mode = input("mode: 0 (cross per high degree), 1 (num nodes, num edges), 2 (numCross)")
# # Process each file
# mode = '2'
# for i in range(20):
mode = '0'
print("highestDegreeNode, highestDegree, numCrossings, numCCS, numNodes, meanEdgeLengths, maxLengthEdge, sumLengthsEdges, meanAngles [0-pi], 2),  stdAngles, percentageHorizontal")

for filename in sorted(filenames):
    G = nx.DiGraph()    


    funcs.read_graph_from_txt(G, os.path.join(input_directory, filename))

    if len(G.nodes()) < 1001:
        print(filename)

        if mode == '0':
            x_data = []
            y_data = []

            x_labels = []

            fig, ax = plt.subplots(figsize=(12, 6))  # Increase the figure size
            line, = ax.plot(x_data, y_data)

            highestDegreeNode, highestDegree = funcs.getHighestDegreeNode(G) 
            
            poses = funcs.getGraphPositions(G, 1.5)
            numCrossings = funcs.countCrossings(G, poses)
            # for i in range(0, highestDegree):
            i = 0
            while numCrossings > 0:

                poses = funcs.getGraphPositions(G, 1.5)
                numCrossings = funcs.countCrossings(G, poses)
                edgeLengthInfo = funcs.computeDistances(G,poses)
                edgeAnglesInfo = funcs.computeAngles(G,poses)
                x_data.append(i)
                y_data.append(numCrossings)
                x_labels.append(highestDegreeNode)
                
                line.set_xdata(x_data)
                line.set_ydata(y_data)
                
                ax.set_xticks(x_data)  # Set the x-ticks to the positions in x_data
                ax.set_xticklabels(x_labels, rotation=90, fontsize=10)  # Adjust the font size and rotate labels
                
                ax.relim()  # Recalculate limits
                ax.autoscale_view()  # Autoscale the view to fit the data
                plt.draw()
                plt.pause(0.1)  # Pause to allow the plot to update
                # print("Iteration:", i, "Current Highest Degree Node:", highestDegreeNode, "Current Highest Degree:", highestDegree, "Crossings:", numCrossings)
                
                
                print(f"({highestDegreeNode},{highestDegree}),{numCrossings},{funcs.getNumCCs(G)},{len(G.nodes())},{edgeLengthInfo},{edgeAnglesInfo}")
                # funcs.splitHighDegreeComponents(G, highestDegree)
                funcs.duplicateNode(G,highestDegreeNode)
                highestDegreeNode, highestDegree = funcs.getHighestDegreeNode(G) 

                i += 1

            plt.tight_layout()  # Automatically adjust subplot parameters to give specified padding
            # Save the plot to the specified output directory with the filename
            output_path = os.path.join(output_directory, f"{filename}.png")
            plt.savefig(output_path)
            plt.close(fig)  # Close the figure to free up memory
            

        elif mode == '1':
            H = G.to_undirected()
            S = [H.subgraph(c).copy() for c in sorted(nx.connected_components(H), key=len, reverse=True)]
            print(len(S))
            if len(S) > 1:
                subGraph = G.subgraph(S[0]).copy()
                subGraph.to_directed()
                print(len(subGraph.nodes()))
                subGraph = G.subgraph(S[1]).copy()
                subGraph.to_directed()
                print(subGraph.nodes())
        elif mode == '2':
                start_time = time.time()

                poses = funcs.getGraphPositions(G, 1.5)
                cross = funcs.countCrossings(G, poses)

                end_time = time.time()
                elapsed_time = end_time - start_time
                # print("Elapsed time get_graph_info: {:.6f} seconds".format(elapsed_time), "Crossings:", cross, "Edges:", len(G.edges()))    
                print(f"{filename};{elapsed_time};{cross};{len(G.edges)}")
        elif mode == '3':
            if len(G.nodes()) < 1001:

                poses = funcs.getGraphPositions(G, 1.5)
                colors = funcs.setColorNodeType(G)  

                    # depth = input("Do you want to arrange it by depth? (y/n)")

                nx.draw(G, pos=poses, with_labels=True, node_color=colors, node_shape='s')
                plt.show()
                output_path = os.path.join(output_directory, f"{filename}_init_vis.png")
                plt.savefig(output_path)
        elif mode == '4':
            print(len(G.nodes()))

        elif mode == '5':
            print(funcs.getNumSources(G))