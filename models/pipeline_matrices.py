import numpy as np

def get_view_matrix(eye, center, up):
    z = eye - center
    z = z / np.linalg.norm(z)
    x = np.cross(up, z)
    x = x / np.linalg.norm(x)
    y = np.cross(z, x)

    m = np.identity(4)
    m[0, :3] = x
    m[1, :3] = y
    m[2, :3] = z
    t = np.identity(4)
    t[:3, 3] = -eye

    return m @ t

def get_projection_matrix(fov, aspect, near, far):
    f = 1 / np.tan(np.radians(fov) / 2)
    m = np.zeros((4, 4))
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1
    return m

def get_viewport_matrix(width, height):
    m = np.identity(4)
    m[0, 0] = width / 2
    m[1, 1] = -height / 2
    m[0, 3] = width / 2
    m[1, 3] = height / 2
    return m
