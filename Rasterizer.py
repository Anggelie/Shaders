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
pygame.display.set_caption("Pikachu 3D - 2 Shaders Lab")

# SHADER 1: BREATHING PIKACHU (SE INFLA)

def vertex_shader_breathing(vertex, time=0, **kwargs):
    """Vertex Shader 1: Breathing - Pikachu se infla y desinfla"""
    x, y, z = vertex
    # Respiración más pronunciada
    breathing_factor = 1 + 0.3 * math.sin(time * 1.2)
    # Pequeño movimiento vertical
    bounce = 0.05 * math.sin(time * 2)
    return (x * breathing_factor, y * breathing_factor + bounce, z * breathing_factor)

def fragment_shader_breathing(color, time=0, **kwargs):
    """Fragment Shader 1: Color normal con pulso suave"""
    r, g, b = color
    # Pulso suave de brillo
    pulse = 1 + 0.1 * math.sin(time * 1.5)
    return (
        int(min(255, r * pulse)),
        int(min(255, g * pulse)),
        int(min(255, b * pulse))
    )

# SHADER 2: ELECTRIC LIGHTNING (RAYOS)

def vertex_shader_electric(vertex, time=0, **kwargs):
    """Vertex Shader 2: Electric - Temblor eléctrico"""
    x, y, z = vertex
    electric_intensity = 0.05
    noise_x = math.sin(time * 20 + x * 30) * electric_intensity
    noise_y = math.cos(time * 25 + y * 35) * electric_intensity
    noise_z = math.sin(time * 18 + z * 28) * electric_intensity * 0.5
    return (x + noise_x, y + noise_y, z + noise_z)

def fragment_shader_electric(color, time=0, position=None, **kwargs):
    """Fragment Shader 2: Rayos eléctricos intensos"""
    r, g, b = color
    
    if position:
        x, y = position
        lightning1 = abs(math.sin(time * 12 + x * 0.08)) * abs(math.cos(time * 10 + y * 0.06))
        lightning2 = abs(math.sin(time * 15 + x * 0.12 + y * 0.08))
        lightning3 = abs(math.cos(time * 8 + x * 0.05 + y * 0.1))
        
        max_lightning = max(lightning1, lightning2, lightning3)
        
        if max_lightning > 0.9:
            return (255, 255, 255)
        elif max_lightning > 0.8:
            return (255, 255, 150)
        elif max_lightning > 0.7:
            return (100, 150, 255)
        elif max_lightning > 0.6:
            return (200, 100, 255)

    electric_base = int(40 * abs(math.sin(time * 6)))
    return (
        min(255, r + electric_base),
        min(255, g + electric_base),
        min(255, b + electric_base//2)
    )

# SHADER 3: SOAP BUBBLE (BURBUJA)

def vertex_shader_bubble(vertex, time=0, **kwargs):
    """Vertex Shader 3: Bubble - Pikachu como burbuja flotante"""
    x, y, z = vertex
    float_y = 0.1 * math.sin(time * 0.8)
    bubble_wave = 0.05 * math.sin(time * 3 + x * 5) * math.cos(time * 2 + z * 4)
    return (x + bubble_wave, y + float_y + bubble_wave * 0.5, z + bubble_wave * 0.3)

def fragment_shader_bubble(color, time=0, position=None, **kwargs):
    """Fragment Shader 3: Colores iridiscentes como burbuja de jabón"""
    r, g, b = color
    
    if position:
        x, y = position
        distance = math.sqrt((x - WIDTH//2)**2 + (y - HEIGHT//2)**2)
        angle = math.atan2(y - HEIGHT//2, x - WIDTH//2)
        
        iridescent_factor = math.sin(time * 2 + distance * 0.02 + angle * 3)
        
        if iridescent_factor > 0.5:
            return (255, int(150 + 50 * math.sin(time)), int(200 + 55 * math.cos(time * 1.5)))
        elif iridescent_factor > 0:
            return (int(100 + 80 * math.cos(time)), int(180 + 60 * math.sin(time * 1.2)), 255)
        elif iridescent_factor > -0.5:
            return (int(120 + 60 * math.sin(time * 0.8)), 255, int(180 + 50 * math.cos(time)))
        else:
            return (255, 255, int(100 + 80 * math.sin(time * 1.8)))
    
    pearl_shine = int(30 * abs(math.sin(time * 1.5)))
    return (min(255, r + pearl_shine), min(255, g + pearl_shine), min(255, b + pearl_shine))

# SHADER 4: HOLOGRAM (HOLOGRAMA FUTURISTA)

def vertex_shader_hologram(vertex, time=0, **kwargs):
    """Vertex Shader 4: Hologram - Efecto de holograma inestable"""
    x, y, z = vertex
    glitch_intensity = 0.02
    glitch_x = math.sin(time * 25 + y * 40) * glitch_intensity if math.sin(time * 8) > 0.3 else 0
    glitch_y = math.cos(time * 30 + x * 35) * glitch_intensity if math.cos(time * 12) > 0.4 else 0
    
    scanline_offset = 0.01 * math.sin(y * 50 + time * 15)
    
    return (x + glitch_x + scanline_offset, y + glitch_y, z)

def fragment_shader_hologram(color, time=0, position=None, **kwargs):
    """Fragment Shader 4: Efecto de holograma con scanlines y interferencia"""
    r, g, b = color
    
    if position:
        x, y = position
        
        scanline_intensity = math.sin(y * 0.5 + time * 10)
        if scanline_intensity > 0.8:
            return (min(255, int(r * 0.3) + 200), min(255, int(g * 0.3) + 250), 255)
        
        noise = abs(math.sin(x * 0.3 + time * 20)) * abs(math.cos(y * 0.2 + time * 15))
        if noise > 0.9:
            return (0, 255, 255)
        
        # Efecto de "transmission loss"
        transmission = abs(math.sin(time * 3)) * 0.7 + 0.3
        
        # Colores holográficos (azul/cyan dominante)
        holo_r = int((r * 0.2 + 100) * transmission)
        holo_g = int((g * 0.4 + 150) * transmission)
        holo_b = int((b * 0.1 + 200) * transmission)
        
        return (min(255, holo_r), min(255, holo_g), min(255, holo_b))
    
    # Base holográfica
    base_transmission = abs(math.sin(time * 2)) * 0.5 + 0.5
    return (
        int(r * 0.3 * base_transmission + 80),
        int(g * 0.5 * base_transmission + 120),
        int(min(255, b * 0.2 * base_transmission + 180))
    )

# SISTEMA DE SHADERS

SHADERS = [
    {
        "name": "BREATHING PIKACHU",
        "vertex": vertex_shader_breathing,
        "fragment": fragment_shader_breathing
    },
    {
        "name": "ELECTRIC LIGHTNING",
        "vertex": vertex_shader_electric,
        "fragment": fragment_shader_electric
    },
    {
        "name": "SOAP BUBBLE",
        "vertex": vertex_shader_bubble,
        "fragment": fragment_shader_bubble
    },
    {
        "name": "HOLOGRAM",
        "vertex": vertex_shader_hologram,
        "fragment": fragment_shader_hologram
    }
]

class SimpleRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.clear_color = (10, 10, 15)  # Fondo muy oscuro
        
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
    py = int((1 - v) * (h - 1))
    
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
scale = 200.0 / max(size)

def create_transform_matrix(rotation_y=0, scale_factor=1.0):
    scale_matrix = np.diag([scale_factor, scale_factor, scale_factor, 1.0])
    
    cos_y = np.cos(rotation_y)
    sin_y = np.sin(rotation_y)
    rotation_matrix = np.array([
        [cos_y, 0, sin_y, 0],
        [0, 1, 0, 0],
        [-sin_y, 0, cos_y, 0],
        [0, 0, 0, 1]
    ])
    
    translation_matrix = np.array([
        [1, 0, 0, -center[0]],
        [0, 1, 0, -center[1]],
        [0, 0, 1, -center[2]],
        [0, 0, 0, 1]
    ])
    
    return rotation_matrix @ scale_matrix @ translation_matrix

def project_vertex(vertex, transform_matrix):
    v_homogeneous = np.array([vertex[0], vertex[1], vertex[2], 1.0])
    v_transformed = transform_matrix @ v_homogeneous
    
    x, y, z = v_transformed[:3]
    camera_distance = 400
    z_offset = z + camera_distance
    
    if z_offset <= 0:
        return None
    
    screen_x = (x * 300 / z_offset) + WIDTH // 2
    screen_y = (-y * 300 / z_offset) + HEIGHT // 2
    
    return (int(screen_x), int(screen_y)), z

def is_front_facing(p1, p2, p3):
    v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])
    v2 = np.array([p3[0] - p1[0], p3[1] - p1[1]])
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]
    return cross_product > 0

# Variables de control
rotation = 0
current_shader = 0
auto_rotate = True
animation_time = 0
clock = pygame.time.Clock()
running = True

print("=== CONTROLES ===")
print("1: Breathing Pikachu (se infla)")
print("2: Electric Lightning (rayos)")
print("3: Soap Bubble (burbuja iridiscente)")
print("4: Hologram (holograma futurista)")
print("ESPACIO: Auto-rotación ON/OFF")
print("← →: Rotación manual")
print("ESC: Salir")
print("=================")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Cambiar shaders
            if event.key == pygame.K_1:
                current_shader = 0
                print("Shader: BREATHING PIKACHU (se infla)")
            elif event.key == pygame.K_2:
                current_shader = 1
                print("Shader: ELECTRIC LIGHTNING (rayos)")
            elif event.key == pygame.K_3:
                current_shader = 2
                print("Shader: SOAP BUBBLE (burbuja iridiscente)")
            elif event.key == pygame.K_4:
                current_shader = 3
                print("Shader: HOLOGRAM (holograma futurista)")
            
            # Otros controles
            elif event.key == pygame.K_SPACE:
                auto_rotate = not auto_rotate
                print(f"Auto-rotación: {'ON' if auto_rotate else 'OFF'}")
            elif event.key == pygame.K_LEFT:
                rotation -= 0.1
            elif event.key == pygame.K_RIGHT:
                rotation += 0.1
            elif event.key == pygame.K_ESCAPE:
                running = False

    r.clear()
    animation_time += 0.05
    
    if auto_rotate:
        rotation += 0.02
    
    # Obtener shader actual
    shader = SHADERS[current_shader]
    vertex_shader_func = shader["vertex"]
    fragment_shader_func = shader["fragment"]
    
    # Crear matriz de transformación
    transform_matrix = create_transform_matrix(rotation, scale)
    
    triangles = []
    
    for face_data in faces:
        face, material = face_data
        
        if len(face) < 3:
            continue
            
        for i in range(1, len(face) - 1):
            try:
                v0_idx = face[0][0]
                v1_idx = face[i][0]
                v2_idx = face[i + 1][0]
                
                uv0_idx = face[0][1] if len(face[0]) > 1 and face[0][1] is not None else None
                uv1_idx = face[i][1] if len(face[i]) > 1 and face[i][1] is not None else None
                uv2_idx = face[i + 1][1] if len(face[i + 1]) > 1 and face[i + 1][1] is not None else None
                
                # Aplicar vertex shader
                v0_original = vertices[v0_idx]
                v1_original = vertices[v1_idx]
                v2_original = vertices[v2_idx]
                
                v0_modified = vertex_shader_func(v0_original, time=animation_time)
                v1_modified = vertex_shader_func(v1_original, time=animation_time)
                v2_modified = vertex_shader_func(v2_original, time=animation_time)
                
                # Proyectar vértices modificados
                proj0 = project_vertex(v0_modified, transform_matrix)
                proj1 = project_vertex(v1_modified, transform_matrix)
                proj2 = project_vertex(v2_modified, transform_matrix)
                
                if proj0 is None or proj1 is None or proj2 is None:
                    continue
                
                screen0, z0 = proj0
                screen1, z1 = proj1
                screen2, z2 = proj2
                
                if (screen0[0] < -100 or screen0[0] > WIDTH + 100 or
                    screen1[0] < -100 or screen1[0] > WIDTH + 100 or
                    screen2[0] < -100 or screen2[0] > WIDTH + 100):
                    continue
                
                if not is_front_facing(screen0, screen1, screen2):
                    continue
                
                uv0 = texcoords[uv0_idx] if uv0_idx is not None and uv0_idx < len(texcoords) else None
                uv1 = texcoords[uv1_idx] if uv1_idx is not None and uv1_idx < len(texcoords) else None
                uv2 = texcoords[uv2_idx] if uv2_idx is not None and uv2_idx < len(texcoords) else None
                
                avg_depth = (z0 + z1 + z2) / 3
                
                triangles.append({
                    'points': [screen0, screen1, screen2],
                    'uvs': [uv0, uv1, uv2],
                    'depth': avg_depth,
                    'material': material
                })
                
            except (IndexError, TypeError):
                continue
    
    # Ordenar y dibujar triángulos
    triangles.sort(key=lambda t: t['depth'], reverse=True)
    
    for triangle in triangles:
        points = triangle['points']
        uvs = triangle['uvs']
        
        # Obtener colores base
        colors = []
        for uv in uvs:
            color = get_color_from_uv(uv)
            colors.append(color)
        
        if colors:
            avg_color = tuple(sum(c[i] for c in colors) // len(colors) for i in range(3))
        else:
            avg_color = (255, 220, 0)
        
        # Aplicar fragment shader
        center_point = (
            sum(p[0] for p in points) // 3,
            sum(p[1] for p in points) // 3
        )
        
        final_color = fragment_shader_func(
            avg_color,
            time=animation_time,
            position=center_point,
            depth=triangle['depth']
        )
        
        # Aplicar sombreado de profundidad
        depth_factor = max(0.4, 1.2 - triangle['depth'] * 0.002)
        shaded_color = tuple(int(min(255, c * depth_factor)) for c in final_color)
        
        try:
            pygame.draw.polygon(screen, shaded_color, points)
        except (ValueError, TypeError):
            continue
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("")