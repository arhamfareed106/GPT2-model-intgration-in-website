import numpy as np

class Hypercube:
    def __init__(self, dimension):
        self.dimension = dimension
        self.vertices = self._generate_vertices(dimension)
        self.edges = self._generate_edges(self.vertices)

    def _generate_vertices(self, dimension):
        """Generate vertices of the hypercube."""
        return [np.array(list(bin(i)[2:].zfill(dimension)), dtype=int) for i in range(2 ** dimension)]

    def _generate_edges(self, vertices):
        """Generate edges based on Hamming distance of 1."""
        edges = []
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                if np.sum(np.abs(vertices[i] - vertices[j])) == 1:
                    edges.append((i, j))
        return edges

    def get_vertex(self, index):
        """Get the vertex at a specific index."""
        return self.vertices[index]

    def get_edges(self):
        """Get all edges of the hypercube."""
        return self.edges

    def __repr__(self):
        return f"Hypercube(dimension={self.dimension}, vertices={len(self.vertices)}, edges={len(self.edges)})"
