import pygame
import numpy as np
import math
import os
from datetime import datetime
from PIL import Image

try:
    from gl import Renderer
    from OBJ import load_obj_with_mtl
    from model import Model
    from models.pipeline_matrices import get_view_matrix, get_projection_matrix, get_viewport_matrix
except ImportError as e:
    print(f"Error importando módulos: {e}")

WIDTH, HEIGHT = 800, 800

class ScreenCapture:
    def __init__(self, base_folder="shader_captures"):
        self.base_folder = base_folder
        os.makedirs(base_folder, exist_ok=True)
    
    def save_screenshot(self, screen, shader_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{shader_name}_{timestamp}.png"
        filepath = os.path.join(self.base_folder, filename)
        pygame.image.save(screen, filepath)
        print(f"Captura guardada: {filepath}")
    
    def auto_capture_all_shaders(self, screen, current_shader_name):
        """Guarda automáticamente cada 5 segundos si ha cambiado el shader"""
        timestamp = datetime.now().strftime("%H%M%S")
        if hasattr(self, 'last_shader') and self.last_shader == current_shader_name:
            return
        
        filename = f"auto_{current_shader_name}_{timestamp}.png"
        filepath = os.path.join(self.base_folder, filename)
        pygame.image.save(screen, filepath)
        self.last_shader = current_shader_name

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pikachu 3D - 7 Shaders Lab")

# Vertex Shaders
def vs_breathing(vertex, time=0, **kwargs):
    x, y, z = vertex
    factor = 1 + 0.3 * math.sin(time * 1.2)
    bounce = 0.05 * math.sin(time * 2)
    return (x * factor, y * factor + bounce, z * factor)

def vs_electric(vertex, time=0, **kwargs):
    x, y, z = vertex
    intensity = 0.05
    nx = math.sin(time * 20 + x * 30) * intensity
    ny = math.cos(time * 25 + y * 35) * intensity
    nz = math.sin(time * 18 + z * 28) * intensity * 0.5
    return (x + nx, y + ny, z + nz)

def vs_bubble(vertex, time=0, **kwargs):
    x, y, z = vertex
    float_y = 0.1 * math.sin(time * 0.8)
    wave = 0.05 * math.sin(time * 3 + x * 5) * math.cos(time * 2 + z * 4)
    return (x + wave, y + float_y + wave * 0.5, z + wave * 0.3)

def vs_hologram(vertex, time=0, **kwargs):
    x, y, z = vertex
    intensity = 0.02
    gx = math.sin(time * 25 + y * 40) * intensity if math.sin(time * 8) > 0.3 else 0
    gy = math.cos(time * 30 + x * 35) * intensity if math.cos(time * 12) > 0.4 else 0
    scan = 0.01 * math.sin(y * 50 + time * 15)
    return (x + gx + scan, y + gy, z)

def vs_lava(vertex, time=0, **kwargs):
    x, y, z = vertex
    melt_factor = max(0, -y + 0.5)
    melt = 0.15 * melt_factor * abs(math.sin(time * 2 + x * 3))
    bubble = 0.08 * math.sin(time * 4 + x * 10 + z * 8) * melt_factor
    return (x, y - melt + bubble, z)

def vs_crystal(vertex, time=0, **kwargs):
    x, y, z = vertex
    factor = 0.03
    fx = factor * math.floor(math.sin(time * 1.5 + x * 8) * 5) / 5
    fy = factor * math.floor(math.cos(time * 1.2 + y * 6) * 4) / 4
    fz = factor * math.floor(math.sin(time * 0.8 + z * 7) * 3) / 3
    return (x + fx, y + fy, z + fz)

def vs_matrix(vertex, time=0, **kwargs):
    x, y, z = vertex
    noise = 0.02 * math.sin(time * 30 + y * 50) if math.sin(time * 10 + x * 20) > 0.7 else 0
    return (x + noise, y, z + noise * 0.5)

# Fragment Shaders
def fs_breathing(color, time=0, **kwargs):
    r, g, b = color
    pulse = 1 + 0.1 * math.sin(time * 1.5)
    return (int(min(255, r * pulse)), int(min(255, g * pulse)), int(min(255, b * pulse)))

def fs_electric(color, time=0, position=None, **kwargs):
    r, g, b = color
    if position:
        x, y = position
        l1 = abs(math.sin(time * 12 + x * 0.08)) * abs(math.cos(time * 10 + y * 0.06))
        l2 = abs(math.sin(time * 15 + x * 0.12 + y * 0.08))
        l3 = abs(math.cos(time * 8 + x * 0.05 + y * 0.1))
        max_l = max(l1, l2, l3)
        
        if max_l > 0.9: return (255, 255, 255)
        elif max_l > 0.8: return (255, 255, 150)
        elif max_l > 0.7: return (100, 150, 255)
        elif max_l > 0.6: return (200, 100, 255)
    
    base = int(40 * abs(math.sin(time * 6)))
    return (min(255, r + base), min(255, g + base), min(255, b + base//2))

def fs_bubble(color, time=0, position=None, **kwargs):
    if position:
        x, y = position
        dist = math.sqrt((x - WIDTH//2)**2 + (y - HEIGHT//2)**2)
        angle = math.atan2(y - HEIGHT//2, x - WIDTH//2)
        factor = math.sin(time * 2 + dist * 0.02 + angle * 3)
        
        if factor > 0.5: return (255, int(150 + 50 * math.sin(time)), int(200 + 55 * math.cos(time * 1.5)))
        elif factor > 0: return (int(100 + 80 * math.cos(time)), int(180 + 60 * math.sin(time * 1.2)), 255)
        elif factor > -0.5: return (int(120 + 60 * math.sin(time * 0.8)), 255, int(180 + 50 * math.cos(time)))
        else: return (255, 255, int(100 + 80 * math.sin(time * 1.8)))
    
    r, g, b = color
    shine = int(30 * abs(math.sin(time * 1.5)))
    return (min(255, r + shine), min(255, g + shine), min(255, b + shine))

def fs_hologram(color, time=0, position=None, **kwargs):
    r, g, b = color
    if position:
        x, y = position
        scan = math.sin(y * 0.5 + time * 10)
        if scan > 0.8: return (min(255, int(r * 0.3) + 200), min(255, int(g * 0.3) + 250), 255)
        
        noise = abs(math.sin(x * 0.3 + time * 20)) * abs(math.cos(y * 0.2 + time * 15))
        if noise > 0.9: return (0, 255, 255)
        
        trans = abs(math.sin(time * 3)) * 0.7 + 0.3
        return (min(255, int((r * 0.2 + 100) * trans)), min(255, int((g * 0.4 + 150) * trans)), min(255, int((b * 0.1 + 200) * trans)))
    
    base_trans = abs(math.sin(time * 2)) * 0.5 + 0.5
    return (int(r * 0.3 * base_trans + 80), int(g * 0.5 * base_trans + 120), int(min(255, b * 0.2 * base_trans + 180)))

def fs_lava(color, time=0, position=None, **kwargs):
    if position:
        x, y = position
        flow = math.sin(time * 3 + x * 0.05) * math.cos(time * 2 + y * 0.03)
        heat = abs(flow)
        
        if heat > 0.8: return (255, 255, 200)
        elif heat > 0.6: return (255, 200, 50)
        elif heat > 0.4: return (255, 100, 0)
        elif heat > 0.2: return (200, 50, 0)
        else: return (100, 20, 0)
    
    r, g, b = color
    pulse = int(50 * abs(math.sin(time * 3)))
    return (min(255, r + pulse), max(0, g - 50), max(0, b - 100))

def fs_crystal(color, time=0, position=None, depth=0, **kwargs):
    r, g, b = color
    if position:
        x, y = position
        angle = math.atan2(y - HEIGHT//2, x - WIDTH//2)
        dist = math.sqrt((x - WIDTH//2)**2 + (y - HEIGHT//2)**2)
        reflection = abs(math.sin(angle * 6 + time * 2)) * abs(math.cos(dist * 0.02 + time))
        
        if reflection > 0.85: return (255, 255, 255)
        elif reflection > 0.7: return (200, 230, 255)
        elif reflection > 0.5: return (150, 200, 255)
        
        ice = 0.3 + 0.2 * abs(math.sin(time * 1.5))
        return (int(r * 0.7 + 100 * ice), int(g * 0.8 + 150 * ice), min(255, int(b * 0.5 + 200 * ice)))
    
    return (int(r * 0.8), int(g * 0.9), min(255, int(b * 1.2)))

def fs_matrix(color, time=0, position=None, **kwargs):
    if position:
        x, y = position
        col = int(x // 20)
        speed = 5 + (col % 3)
        rain_y = (y + time * speed * 30) % HEIGHT
        char_pos = int(rain_y // 15)
        prob = abs(math.sin(col * 1.7 + char_pos * 0.3 + time * 0.1))
        
        if prob > 0.85: return (150, 255, 150)
        elif prob > 0.7: return (50, 200, 50)
        elif prob > 0.5: return (20, 150, 20)
        elif prob > 0.3: return (10, 100, 10)
        
        bg = int(20 * abs(math.sin(time * 0.5)))
        return (0, bg, 0)
    
    r, g, b = color
    return (0, min(255, int(g * 0.3 + 50)), 0)

SHADERS = [
    ("BREATHING", vs_breathing, fs_breathing),
    ("ELECTRIC", vs_electric, fs_electric),
    ("BUBBLE", vs_bubble, fs_bubble),
    ("HOLOGRAM", vs_hologram, fs_hologram),
    ("LAVA", vs_lava, fs_lava),
    ("CRYSTAL", vs_crystal, fs_crystal),
    ("MATRIX", vs_matrix, fs_matrix)
]

class SimpleRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.clear_color = (10, 10, 15)
    
    def clear(self):
        self.screen.fill(self.clear_color)

r = SimpleRenderer(screen)
capturer = ScreenCapture()

try:
    vertices, faces, materials, texcoords = load_obj_with_mtl("./source/Pikachu.obj")
    model = Model(vertices, faces, texcoords, materials)
except Exception as e:
    print(f"Error: {e}")
    pygame.quit()
    exit()

try:
    texture_img = Image.open("./textures/PikachuDh.png")
    texture_pixels = np.array(texture_img)
except:
    texture_pixels = np.full((256, 256, 3), [255, 220, 0], dtype=np.uint8)

def get_color_from_uv(uv):
    if uv is None or texture_pixels is None:
        return (255, 220, 0)
    
    u, v = max(0.0, min(1.0, uv[0])), max(0.0, min(1.0, uv[1]))
    h, w = texture_pixels.shape[:2]
    px, py = int(u * (w - 1)), int((1 - v) * (h - 1))
    return tuple(texture_pixels[max(0, min(h-1, py)), max(0, min(w-1, px))])

v_array = np.array(vertices)
center = (v_array.min(axis=0) + v_array.max(axis=0)) / 2
scale = 200.0 / max(v_array.max(axis=0) - v_array.min(axis=0))

def create_transform_matrix(rotation_y=0):
    cos_y, sin_y = np.cos(rotation_y), np.sin(rotation_y)
    return np.array([
        [cos_y * scale, 0, sin_y * scale, -center[0] * scale * cos_y - center[2] * scale * sin_y],
        [0, scale, 0, -center[1] * scale],
        [-sin_y * scale, 0, cos_y * scale, center[0] * scale * sin_y - center[2] * scale * cos_y],
        [0, 0, 0, 1]
    ])

def project_vertex(vertex, transform_matrix):
    v = transform_matrix @ np.array([*vertex, 1])
    z_offset = v[2] + 400
    if z_offset <= 0: return None
    return (int(v[0] * 300 / z_offset + WIDTH//2), int(-v[1] * 300 / z_offset + HEIGHT//2)), v[2]

def is_front_facing(p1, p2, p3):
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]) > 0

rotation, current_shader, auto_rotate, animation_time = 0, 0, True, 0
clock = pygame.time.Clock()
running = True
last_capture_time = 0

print("Controles: 1-7 (shaders), ESPACIO (auto-rotate), C (captura), A (auto-captura)")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_7:
                current_shader = event.key - pygame.K_1
                current_shader = min(current_shader, len(SHADERS) - 1)
                print(f"Shader: {SHADERS[current_shader][0]}")
            elif event.key == pygame.K_SPACE:
                auto_rotate = not auto_rotate
            elif event.key == pygame.K_c:
                capturer.save_screenshot(screen, SHADERS[current_shader][0])
            elif event.key == pygame.K_a:
                capturer.auto_capture_all_shaders(screen, SHADERS[current_shader][0])
            elif event.key == pygame.K_LEFT:
                rotation -= 0.1
            elif event.key == pygame.K_RIGHT:
                rotation += 0.1

    r.clear()
    animation_time += 0.05
    if auto_rotate: rotation += 0.02
    
    shader_name, vertex_func, fragment_func = SHADERS[current_shader]
    transform_matrix = create_transform_matrix(rotation)
    triangles = []
    
    for face_data in faces:
        face, material = face_data
        if len(face) < 3: continue
            
        for i in range(1, len(face) - 1):
            try:
                indices = [face[0][0], face[i][0], face[i + 1][0]]
                uv_indices = [face[j][1] if len(face[j]) > 1 and face[j][1] is not None else None for j in [0, i, i + 1]]
                
                modified_verts = [vertex_func(vertices[idx], time=animation_time) for idx in indices]
                projections = [project_vertex(v, transform_matrix) for v in modified_verts]
                
                if any(p is None for p in projections): continue
                
                screen_coords = [p[0] for p in projections]
                depths = [p[1] for p in projections]
                
                if any(sc[0] < -100 or sc[0] > WIDTH + 100 for sc in screen_coords): continue
                if not is_front_facing(*screen_coords): continue
                
                uvs = [texcoords[idx] if idx is not None and idx < len(texcoords) else None for idx in uv_indices]
                avg_depth = sum(depths) / 3
                
                triangles.append({
                    'points': screen_coords,
                    'uvs': uvs,
                    'depth': avg_depth
                })
            except (IndexError, TypeError):
                continue
    
    triangles.sort(key=lambda t: t['depth'], reverse=True)
    
    for triangle in triangles:
        colors = [get_color_from_uv(uv) for uv in triangle['uvs']]
        avg_color = tuple(sum(c[i] for c in colors) // len(colors) for i in range(3)) if colors else (255, 220, 0)
        
        center_point = (sum(p[0] for p in triangle['points']) // 3, sum(p[1] for p in triangle['points']) // 3)
        final_color = fragment_func(avg_color, time=animation_time, position=center_point, depth=triangle['depth'])
        
        depth_factor = max(0.4, 1.2 - triangle['depth'] * 0.002)
        shaded_color = tuple(int(min(255, c * depth_factor)) for c in final_color)
        
        try:
            pygame.draw.polygon(screen, shaded_color, triangle['points'])
        except:
            continue
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()