"""
Example of how a set of points can be turned into Voronoi partitions using SciPy
"""

from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
from random import randint

# Generate 200 random points between 0-500, 0-500
points = [(randint(0, 500), randint(0, 500)) for _ in range(200)]

vor = Voronoi(points)
voronoi_plot_2d(vor)
plt.show()