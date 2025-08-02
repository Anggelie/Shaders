import os

def load_obj_with_mtl(filename):
    vertices = []
    texcoords = []
    faces = []
    materials = {}

    mtl_file = None
    current_material = None

    with open(filename, "r") as f:
        for line in f:
            if line.startswith("mtllib"):
                mtl_file = os.path.join(os.path.dirname(filename), line.strip().split()[1])
            elif line.startswith("v "):
                vertices.append(tuple(map(float, line.strip().split()[1:4])))
            elif line.startswith("vt "):
                texcoords.append(tuple(map(float, line.strip().split()[1:3])))
            elif line.startswith("usemtl"):
                current_material = line.strip().split()[1]
            elif line.startswith("f "):
                face = []
                for part in line.strip().split()[1:]:
                    vals = part.split('/')
                    face.append((int(vals[0])-1, int(vals[1])-1 if len(vals) > 1 and vals[1] else None))
                faces.append((face, current_material))

    if mtl_file and os.path.exists(mtl_file):
        with open(mtl_file) as mtl:
            name = None
            for line in mtl:
                if line.startswith("newmtl"):
                    name = line.strip().split()[1]
                    materials[name] = {}
                elif line.startswith("map_Kd") and name:
                    materials[name]['texture'] = os.path.join(os.path.dirname(mtl_file), line.strip().split()[1])

    return vertices, faces, materials, texcoords
