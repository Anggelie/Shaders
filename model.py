class Model:
    def __init__(self, vertices, faces, texcoords=None, materials=None):
        self.vertices = vertices
        self.faces = faces
        self.texcoords = texcoords
        self.materials = materials
