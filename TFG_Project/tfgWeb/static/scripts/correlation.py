import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

# Data
data = {
    "map00010.oriented": (-6.62, 9),
    "map00020.oriented": (2.06, 3),
    "map00030.oriented": (-11.49, 11),
    "map00040.oriented": (1.98, 11),
    "map00051.oriented": (-0.29, 9),
    "map00052.oriented": (-17.83, 14),
    "map00053.oriented": (-1.43, 13),
    "map00500.oriented": (2.66, 11),
    "map00520.oriented": (4.12, 16),
    "map00562.oriented": (-6.98, 10),
    "map00620.oriented": (-10.63, 15),
    "map00630.oriented": (-8.13, 19),
    "map00640.oriented": (1.35, 12),
    "map00650.oriented": (-11.53, 13),
    "map00660.oriented": (-7.08, 4),
    "map01200.oriented": (-0.89, 13),
    "map01210.oriented": (-5.51, 20),
    "map01212.oriented": (-10.07, 12),
    "map01220.oriented": (1.55, 47),
    "map01230.oriented": (-3.16, 20),
    "map01232.oriented": (0.64, 5),
    "map01240.oriented": (-4.68, 49),
    "map01250.oriented": (-11.09, 56)
}

# Extract percentage decreases and number of sources
percentage_decreases = [value[0] for value in data.values()]
num_sources = [value[1] for value in data.values()]

# Calculate the correlation coefficient
correlation_coefficient, _ = pearsonr(percentage_decreases, num_sources)

# Plot the correlation
plt.figure(figsize=(10, 6))
plt.scatter(num_sources, percentage_decreases, color='blue')
plt.xlabel('Number of Sources')
plt.ylabel('Percentage Decrease')
plt.title(f'Correlation between Percentage Decrease and Number of Sources\nCorrelation Coefficient: {correlation_coefficient:.2f}')
plt.grid(True)
plt.show()

# Print the correlation coefficient
print(f"Correlation Coefficient: {correlation_coefficient:.2f}")