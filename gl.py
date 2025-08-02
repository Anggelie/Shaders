import pygame
import numpy as np

WHITE = (255, 255, 255)

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.clear_color = (50, 50, 50)  # Fondo más oscuro para mejor contraste
        self.color = WHITE
        self.zbuffer = np.full((screen.get_height(), screen.get_width()), float('inf'))

    def clear(self):
        self.screen.fill(self.clear_color)
        self.zbuffer.fill(float('inf'))

    def draw_point(self, x, y, color=None):
        if 0 <= x < self.screen.get_width() and 0 <= y < self.screen.get_height():
            self.screen.set_at((int(x), int(y)), color or self.color)
    
    def draw_line(self, x0, y0, x1, y1, color=None):
        """Dibuja una línea usando el algoritmo de Bresenham"""
        color = color or self.color
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        steep = dy > dx
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
            dx, dy = dy, dx
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        ystep = 1 if y0 < y1 else -1
        error = dx // 2
        y = y0
        
        for x in range(x0, x1 + 1):
            if steep:
                if 0 <= y < self.screen.get_width() and 0 <= x < self.screen.get_height():
                    self.screen.set_at((y, x), color)
            else:
                if 0 <= x < self.screen.get_width() and 0 <= y < self.screen.get_height():
                    self.screen.set_at((x, y), color)
            
            error -= dy
            if error < 0:
                y += ystep
                error += dx
    
    def draw_triangle_wireframe(self, v0, v1, v2, color=None):
        """Dibuja un triángulo en modo wireframe"""
        self.draw_line(v0[0], v0[1], v1[0], v1[1], color)
        self.draw_line(v1[0], v1[1], v2[0], v2[1], color)
        self.draw_line(v2[0], v2[1], v0[0], v0[1], color)