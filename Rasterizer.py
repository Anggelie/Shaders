import pygame
import numpy as np
import math
from PIL import Image

try:
    from gl import Renderer
    from OBJ import load_obj_with_mtl
    from model import Model
    from models.pipeline_matrices import get_view_matrix, get_projection_matrix, get_viewport_matrix
except ImportError as e:
    print(f"Error importando módulos: {e}")

WIDTH, HEIGHT = 800, 800
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pikachu 3D")

class SimpleRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.clear_color = (30, 30, 40)  # Fondo oscuro
        
    def clear(self):
        self.screen.fill(self.clear_color)

r = SimpleRenderer(screen)

# Cargar modelo
try:
    vertices, faces, materials, texcoords = load_obj_with_mtl("./source/Pikachu.obj")
    model = Model(vertices, faces, texcoords, materials)
    print(f"Modelo cargado: {len(vertices)} vértices, {len(faces)} caras")
except Exception as e:
    print(f"Error cargando modelo: {e}")
    pygame.quit()
    exit()

# Cargar textura principal
texture_pixels = None
try:
    texture_img = Image.open("./textures/PikachuDh.png")
    texture_pixels = np.array(texture_img)
    print(f"Textura cargada: {texture_pixels.shape}")
except Exception as e:
    print(f"Error cargando textura: {e}")
    # Crear textura amarilla por defecto
    texture_pixels = np.full((256, 256, 3), [255, 220, 0], dtype=np.uint8)

def get_color_from_uv(uv):
    """Obtiene color de la textura"""
    if uv is None or texture_pixels is None:
        return (255, 220, 0)  # Amarillo Pikachu
    
    u, v = uv
    u = max(0.0, min(1.0, u))
    v = max(0.0, min(1.0, v))
    
    h, w = texture_pixels.shape[:2]
    px = int(u * (w - 1))
    py = int((1 - v) * (h - 1))  # Invertir V
    
    px = max(0, min(w - 1, px))
    py = max(0, min(h - 1, py))
    
    color = texture_pixels[py, px]
    return tuple(color)

# Normalización del modelo
v_array = np.array(vertices)
min_vals = v_array.min(axis=0)
max_vals = v_array.max(axis=0)
center = (min_vals + max_vals) / 2
size = max_vals - min_vals
scale = 200.0 / max(size)  # Escala para que se vea bien

print(f"Centro del modelo: {center}")
print(f"Tamaño: {size}")
print(f"Escala: {scale}")

# Matrices de transformación
def create_transform_matrix(rotation_y=0, scale_factor=1.0):
    # Matriz de escala
    scale_matrix = np.diag([scale_factor, scale_factor, scale_factor, 1.0])
    
    # Matriz de rotación en Y
    cos_y = np.cos(rotation_y)
    sin_y = np.sin(rotation_y)
    rotation_matrix = np.array([
        [cos_y, 0, sin_y, 0],
        [0, 1, 0, 0],
        [-sin_y, 0, cos_y, 0],
        [0, 0, 0, 1]
    ])
    
    # Matriz de traslación para centrar
    translation_matrix = np.array([
        [1, 0, 0, -center[0]],
        [0, 1, 0, -center[1]],
        [0, 0, 1, -center[2]],
        [0, 0, 0, 1]
    ])
    
    return rotation_matrix @ scale_matrix @ translation_matrix

def project_vertex(vertex, transform_matrix):
    """Proyecta un vértice 3D a 2D"""
    # Aplicar transformación
    v_homogeneous = np.array([vertex[0], vertex[1], vertex[2], 1.0])
    v_transformed = transform_matrix @ v_homogeneous
    
    # Proyección perspectiva simple
    x, y, z = v_transformed[:3]
    
    # Distancia de la cámara
    camera_distance = 400
    z_offset = z + camera_distance
    
    if z_offset <= 0:
        return None
    
    # Proyección
    screen_x = (x * 300 / z_offset) + WIDTH // 2
    screen_y = (-y * 300 / z_offset) + HEIGHT // 2  # Invertir Y
    
    return (int(screen_x), int(screen_y)), z

def is_front_facing(p1, p2, p3):
    """Verifica si un triángulo está mirando hacia adelante (backface culling)"""
    # Calcular vectores del triángulo
    v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])
    v2 = np.array([p3[0] - p1[0], p3[1] - p1[1]])
    
    # Producto cruz en 2D (componente Z)
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]
    
    return cross_product > 0

# Variables de animación
rotation = 0
clock = pygame.time.Clock()
running = True

print("Iniciando renderizado...")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                rotation -= 0.1
            elif event.key == pygame.K_RIGHT:
                rotation += 0.1

    r.clear()
    
    rotation += 0.01
    
    transform_matrix = create_transform_matrix(rotation, scale)
    
    triangles = []
    
    # Procesar caras
    for face_data in faces:
        face, material = face_data
        
        if len(face) < 3:
            continue
            
        # Convertir polígono a triángulos
        for i in range(1, len(face) - 1):
            try:
                # Índices de vértices
                v0_idx = face[0][0]
                v1_idx = face[i][0]
                v2_idx = face[i + 1][0]
                
                # Índices de coordenadas UV
                uv0_idx = face[0][1] if len(face[0]) > 1 and face[0][1] is not None else None
                uv1_idx = face[i][1] if len(face[i]) > 1 and face[i][1] is not None else None
                uv2_idx = face[i + 1][1] if len(face[i + 1]) > 1 and face[i + 1][1] is not None else None
                
                # Obtener vértices
                v0 = vertices[v0_idx]
                v1 = vertices[v1_idx]
                v2 = vertices[v2_idx]
                
                # Proyectar vértices
                proj0 = project_vertex(v0, transform_matrix)
                proj1 = project_vertex(v1, transform_matrix)
                proj2 = project_vertex(v2, transform_matrix)
                
                if proj0 is None or proj1 is None or proj2 is None:
                    continue
                
                screen0, z0 = proj0
                screen1, z1 = proj1
                screen2, z2 = proj2
                
                # Verificar que esté en pantalla
                if (screen0[0] < -100 or screen0[0] > WIDTH + 100 or
                    screen1[0] < -100 or screen1[0] > WIDTH + 100 or
                    screen2[0] < -100 or screen2[0] > WIDTH + 100):
                    continue
                
                # Backface culling - solo dibujar caras que miran hacia adelante
                if not is_front_facing(screen0, screen1, screen2):
                    continue
                
                # Obtener coordenadas UV
                uv0 = texcoords[uv0_idx] if uv0_idx is not None and uv0_idx < len(texcoords) else None
                uv1 = texcoords[uv1_idx] if uv1_idx is not None and uv1_idx < len(texcoords) else None
                uv2 = texcoords[uv2_idx] if uv2_idx is not None and uv2_idx < len(texcoords) else None
                
                # Calcular profundidad promedio
                avg_depth = (z0 + z1 + z2) / 3
                
                triangles.append({
                    'points': [screen0, screen1, screen2],
                    'uvs': [uv0, uv1, uv2],
                    'depth': avg_depth,
                    'material': material
                })
                
            except (IndexError, TypeError):
                continue
    
    # Ordenar triángulos por profundidad (más lejanos primero) - Z-BUFFER
    triangles.sort(key=lambda t: t['depth'], reverse=True)
    
    # Dibujar triángulos
    for triangle in triangles:
        points = triangle['points']
        uvs = triangle['uvs']
        material = triangle['material']
        
        # Obtener colores de los vértices usando UV
        colors = []
        for uv in uvs:
            color = get_color_from_uv(uv)
            # Aplicar colores específicos según el material
            if material and 'Eye' in material:
                # Hacer los ojos más oscuros
                color = tuple(min(255, int(c * 0.3)) for c in color)
            elif material and 'Mouth' in material:
                # Hacer la boca rojiza
                color = (min(255, color[0] + 50), max(0, color[1] - 50), max(0, color[2] - 50))
            colors.append(color)
        
        # Color promedio
        if colors:
            avg_color = tuple(sum(c[i] for c in colors) // len(colors) for i in range(3))
        else:
            avg_color = (255, 220, 0)  # Amarillo por defecto
        
        # Aplicar sombreado básico más pronunciado
        depth_factor = max(0.4, 1.2 - triangle['depth'] * 0.002)
        shaded_color = tuple(int(min(255, c * depth_factor)) for c in avg_color)
        
        # Dibujar triángulo
        try:
            pygame.draw.polygon(screen, shaded_color, points)
            # Añadir contorno sutil para mejor definición
            pygame.draw.polygon(screen, tuple(max(0, c - 30) for c in shaded_color), points, 1)
        except (ValueError, TypeError):
            continue
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Programa terminado")