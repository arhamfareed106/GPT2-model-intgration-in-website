import numpy as np

class ConceptMapping:
    def __init__(self, num_vertices):
        self.num_vertices = num_vertices
        self.concept_to_vertex = {}
        self.vertex_to_concept = {}

    def add_mapping(self, concept_embedding, vertex_id):
        if vertex_id < 0 or vertex_id >= self.num_vertices:
            raise ValueError("Vertex ID must be within the range of the hypercube.")
        self.concept_to_vertex[tuple(concept_embedding)] = vertex_id
        self.vertex_to_concept[vertex_id] = concept_embedding

    def get_vertex_id(self, concept_embedding):
        return self.concept_to_vertex.get(tuple(concept_embedding), None)

    def get_concept_embedding(self, vertex_id):
        return self.vertex_to_concept.get(vertex_id, None)

    def get_all_mappings(self):
        return self.concept_to_vertex, self.vertex_to_concept

    def clear_mappings(self):
        self.concept_to_vertex.clear()
        self.vertex_to_concept.clear()
