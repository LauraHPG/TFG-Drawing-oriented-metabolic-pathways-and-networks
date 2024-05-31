import matplotlib.pyplot as plt

# Data
maps = [
    ("map00010", 241, 1311, 0.335553), ("map00020", 138, 432, 0.119871), 
    ("map00030", 229, 714, 0.180458), ("map00040", 326, 3497, 0.806146), 
    ("map00051", 325, 2111, 0.489439), ("map00052", 223, 582, 0.174863), 
    ("map00053", 282, 1423, 0.339729), ("map00500", 279, 2235, 0.450512), 
    ("map00520", 577, 5181, 1.337604), ("map00562", 245, 1318, 0.282319), 
    ("map00620", 396, 4943, 1.077644), ("map00630", 349, 2473, 0.670718), 
    ("map00640", 285, 2098, 0.480160), ("map00650", 316, 2573, 0.664057), 
    ("map00660", 138, 220, 0.107145), ("map01200", 917, 21641, 6.982419), 
    ("map01210", 720, 16072, 4.739817), ("map01212", 527, 7363, 2.060131), 
    ("map01220", 1240, 50292, 14.684756), ("map01230", 711, 13009, 4.269774), 
    ("map01232", 571, 13820, 3.347483), ("map01240", 1516, 36968, 17.936422), 
    ("map01250", 790, 10185, 2.800503)
]

# Sort by number of edges
maps_sorted_by_edges = sorted(maps, key=lambda x: x[1])

# Unpack sorted data
map_names_sorted, num_edges_sorted, num_crossings_sorted, elapsed_time_sorted = zip(*maps_sorted_by_edges)

# Create bar plot for number of crossings
plt.figure(figsize=(14, 8))
plt.bar(map_names_sorted, elapsed_time_sorted, color='purple')
plt.title("Elapsed Time for Each Map (Sorted by Number of Edges)")
plt.xlabel("Map")
plt.ylabel("Number of Crossings")
plt.xticks(rotation=90)
plt.grid(axis='y')
plt.tight_layout()

# Show plot
plt.show()