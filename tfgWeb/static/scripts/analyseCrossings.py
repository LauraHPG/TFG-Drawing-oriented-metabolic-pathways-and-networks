import matplotlib.pyplot as plt
import numpy as np

# Define the paths to the files
file_path_before = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/TFG_Project/tfgWeb/static/scripts/numCrossWoRearrange.txt'
file_path_after = '/home/laura/Documents/TFG-Drawing-oriented-metabolic-pathways-and-networks/TFG_Project/tfgWeb/static/scripts/numCrossWRearrange.txt'

# Function to read data from a file and compute mean crossings
def compute_mean_crossings(file_path):
    crossings_dict = {}
    with open(file_path, 'r') as file:
        header = file.readline().strip().split(';')
        for line in file:
            parts = line.strip().split(';')
            name = parts[0]
            crossings = int(parts[2])
            if name not in crossings_dict:
                crossings_dict[name] = []
            crossings_dict[name].append(crossings)
    mean_crossings = {key: np.mean(values) for key, values in crossings_dict.items()}
    return mean_crossings

# Compute mean crossings for both files
mean_crossings_before = compute_mean_crossings(file_path_before)
mean_crossings_after = compute_mean_crossings(file_path_after)

# # Sort the dictionaries by map name to ensure consistent order in the plot
# mean_crossings_before = dict(sorted(mean_crossings_before.items()))
# mean_crossings_after = dict(sorted(mean_crossings_after.items()))

# # Calculate percentage decrease
# percentage_decrease = {
#     key: ((mean_crossings_after[key] - mean_crossings_before[key]) / mean_crossings_before[key]) * 100
#     for key in mean_crossings_before.keys()
# }

# # Generate the bar plot
# labels = mean_crossings_before.keys()
# before_means = [mean_crossings_before[label] for label in labels]
# after_means = [mean_crossings_after[label] for label in labels]

# x = np.arange(len(labels))

# fig, ax = plt.subplots(figsize=(12, 8))

# bar_width = 0.4
# bar1 = ax.bar(x - bar_width/2, before_means, bar_width, label='Before', color='orange')
# bar2 = ax.bar(x + bar_width/2, after_means, bar_width, label='After', color='blue')

# # Adding labels and title
# ax.set_xlabel('Map Name')
# ax.set_ylabel('Mean Crossings')
# ax.set_title('Mean Number of Crossings Before and After Rearranging Sources')
# ax.set_xticks(x)
# ax.set_xticklabels(labels, rotation=90)
# ax.legend()

# # Display the percentage decrease above the bars
# # for i, label in enumerate(labels):
# #     height_before = before_means[i]
# #     height_after = after_means[i]
# #     percentage = percentage_decrease[label]
# #     ax.text(x[i] - bar_width/2, height_before + 5, f'{percentage:.2f}%', ha='center', color='black', fontsize=8)

# plt.tight_layout()
# plt.show()

# # Print the percentage decrease
# print("Percentage Decrease:")
# for key, value in percentage_decrease.items():
#     print(f"{key}: {value:.2f}%")


# mean_decrease = np.mean(list(percentage_decrease.values()))
# print("Mean decrease: ", mean_decrease)

print(mean_crossings_before)
for key in mean_crossings_after:
    print(mean_crossings_after[key])