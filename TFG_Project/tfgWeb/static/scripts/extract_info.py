import networkx as nx
import sys
import auxiliar_methods as funcs
import layouts as lyts
import matplotlib.pyplot as plt
import os

G = nx.DiGraph()    
reactions = []
poses = {}

input_directory = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/TFG_Project/tfgWeb/static/inputGraphs'
output_directory = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/Results'  # Specify your output directory

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get a list of all files in the input directory
filenames = os.listdir(input_directory)

# Filter out directories, only keep files
filenames = [f for f in filenames if os.path.isfile(os.path.join(input_directory, f))]

# Process each file
for filename in sorted(filenames):
    G = nx.DiGraph()    

    print(filename)

    info = funcs.read_graph_from_txt(G, os.path.join(input_directory, filename))

    x_data = []
    y_data = []

    x_labels = []

    fig, ax = plt.subplots(figsize=(12, 6))  # Increase the figure size
    line, = ax.plot(x_data, y_data)

    highestDegreeNode, highestDegree = funcs.getHighestDegreeNode(G) 
    poses = funcs.getGraphPositions(G, 1.5)
    currentMaxDegree = highestDegree
    numCrossings = funcs.countCrossings(G, poses)

    # for i in range(0, highestDegree):
    i = 0
    while highestDegree > 1:
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


        poses = funcs.getGraphPositions(G, 1.5)
        numCrossings = funcs.countCrossings(G, poses)

        print("Iteration:", i, "Current Highest Degree Node:", highestDegreeNode, "Current Highest Degree:", highestDegree, "Crossings:", numCrossings)
        
        funcs.splitHighDegreeComponents(G, highestDegree)
        highestDegreeNode, highestDegree = funcs.getHighestDegreeNode(G) 

        highestDegree -= 1
        i += 1

    plt.tight_layout()  # Automatically adjust subplot parameters to give specified padding
    # Save the plot to the specified output directory with the filename
    output_path = os.path.join(output_directory, f"{filename}.png")
    plt.savefig(output_path)
    plt.close(fig)  # Close the figure to free up memory