import numpy as np
import math

def vertex_shader_identity(vertex):
    """Shader de vértice básico - sin transformación"""
    return vertex

def vertex_shader_wave(vertex, time=0):
    """Shader de vértice que crea efecto de onda"""
    x, y, z = vertex
    wave_amplitude = 0.05
    wave_frequency = 3.0
    wave_offset = math.sin(time + x * wave_frequency + z * wave_frequency) * wave_amplitude
    return (x, y + wave_offset, z)

def vertex_shader_morphing_pikachu(vertex, time=0):
    """Shader de vértice que hace que Pikachu se deforme ligeramente"""
    x, y, z = vertex
    morph_factor = 0.05
    morph = morph_factor * math.sin(time * 2 + z * 8 + x * 4)
    breathing = 1 + 0.03 * math.sin(time * 1.5)
    return (x * breathing + morph, y * breathing - morph * 0.5, z * breathing)

def vertex_shader_bounce(vertex, time=0):
    """Shader que hace que Pikachu rebote"""
    x, y, z = vertex
    bounce = abs(math.sin(time * 2)) * 0.2
    return (x, y + bounce, z)

def fragment_shader_pikachu_cartoon(color=(255, 255, 0), normal=None, light_dir=(0, 1, 0)):
    """Shader de fragmento que da un look cartoon a Pikachu"""
    r, g, b = color
    
    # Cuantización de colores para efecto cartoon
    if r > 240 and g > 240:  # Amarillo brillante
        return (255, 255, 100)
    elif r > 200 and g > 200:  # Amarillo medio
        return (240, 240, 60)
    elif r < 100:  # Sombras oscuras
        return (180, 180, 40)
    else:
        return (220, 220, 80)

def fragment_shader_cell_shading(color=(255, 255, 0), lighting=1.0):
    """Shader de cel shading para look anime"""
    r, g, b = color
    
    # Discretizar la iluminación
    if lighting > 0.8:
        factor = 1.0
    elif lighting > 0.6:
        factor = 0.8
    elif lighting > 0.4:
        factor = 0.6
    elif lighting > 0.2:
        factor = 0.4
    else:
        factor = 0.2
    
    return (int(r * factor), int(g * factor), int(b * factor))

def fragment_shader_outline(vertex1, vertex2, threshold=2):
    """Shader para detectar y dibujar contornos"""
    dx = vertex2[0] - vertex1[0]
    dy = vertex2[1] - vertex1[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < threshold:
        return (0, 0, 0)  # Negro para contornos
    return None  # No dibujar nada

def fragment_shader_pikachu_disco(vertex, time=0):
    """Shader psicodélico para Pikachu"""
    x, y, z = vertex
    t = time * 2
    
    r = int((math.sin(x * 0.1 + t) + 1) * 127)
    g = int((math.sin(y * 0.1 + t + 2) + 1) * 127)
    b = int((math.sin(z * 0.1 + t + 4) + 1) * 127)
    
    return (r, g, b)

def fragment_shader_electric(vertex, time=0):
    """Shader que simula efectos eléctricos"""
    x, y, z = vertex
    
    # Crear efecto de rayos eléctricos
    electric_factor = abs(math.sin(time * 10 + x * 5)) * abs(math.cos(time * 8 + y * 3))
    
    if electric_factor > 0.8:
        return (255, 255, 255)  # Destellos blancos
    elif electric_factor > 0.6:
        return (255, 255, 100)  # Amarillo eléctrico
    else:
        return (255, 200, 0)    # Amarillo normal

def fragment_shader_gradient(color, position, center=(400, 400)):
    """Shader que aplica un gradiente desde el centro"""
    r, g, b = color
    dx = position[0] - center[0]
    dy = position[1] - center[1]
    distance = math.sqrt(dx*dx + dy*dy) / 400.0  # Normalizar
    
    factor = max(0.3, 1.0 - distance * 0.5)
    return (int(r * factor), int(g * factor), int(b * factor))

def fragment_shader_metallic(color, normal=None, view_dir=None):
    """Shader que da apariencia metálica"""
    r, g, b = color
    
    # Simular reflexión metálica
    metallic_factor = 0.7
    base_color = (int(r * 0.3), int(g * 0.3), int(b * 0.3))
    highlight = (255, 255, 255)
    
    # Mezclar color base con highlight metálico
    final_r = int(base_color[0] * (1 - metallic_factor) + highlight[0] * metallic_factor)
    final_g = int(base_color[1] * (1 - metallic_factor) + highlight[1] * metallic_factor)
    final_b = int(base_color[2] * (1 - metallic_factor) + highlight[2] * metallic_factor)
    
    return (min(255, final_r), min(255, final_g), min(255, final_b))

def fragment_shader_toon_with_outline(color, depth, outline_threshold=0.1):
    """Shader que combina toon shading con contornos"""
    r, g, b = color
    
    # Aplicar toon shading
    if depth > outline_threshold:
        # Contorno
        return (20, 20, 20)
    else:
        # Color normal con cuantización
        levels = 4
        r = int((r // (256 // levels)) * (256 // levels))
        g = int((g // (256 // levels)) * (256 // levels))
        b = int((b // (256 // levels)) * (256 // levels))
        return (r, g, b)

def apply_lighting(color, normal, light_dir=(0, 1, 0), ambient=0.3):
    """Aplica iluminación básica a un color"""
    if normal is None:
        return color
    
    # Normalizar vectores
    normal = np.array(normal) / np.linalg.norm(normal)
    light_dir = np.array(light_dir) / np.linalg.norm(light_dir)
    
    # Calcular iluminación difusa
    dot_product = max(0, np.dot(normal, light_dir))
    lighting = ambient + (1 - ambient) * dot_product
    
    r, g, b = color
    return (int(r * lighting), int(g * lighting), int(b * lighting))

def fragment_shader_pokemon_glow(color, time=0, intensity=0.5):
    """Shader que da un efecto de resplandor tipo Pokémon"""
    r, g, b = color
    
    # Efecto de pulso
    pulse = (math.sin(time * 3) + 1) * 0.5 * intensity
    
    # Añadir resplandor
    glow_r = min(255, int(r + pulse * 100))
    glow_g = min(255, int(g + pulse * 100))
    glow_b = min(255, int(b + pulse * 50))
    
    return (glow_r, glow_g, glow_b)