import pygame
import math
import random
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

class Visualizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = pygame.Surface((width, height))
        self.wave_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.equalizer_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.particle_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.fractal_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.time = 0
        self.particle_count = 0
        self.particles = []
        self.base_hue = random.uniform(0, 360)
        self.palette = self._generate_palette()
        self.waves = [
            {'amplitude': 30 + i * 15, 'frequency': 0.005 + i * 0.002,
             'phase': random.uniform(0, 2 * math.pi), 'color': self.palette[i % len(self.palette)]}
            for i in range(5)
        ]
        self.fractal_type = 'tree'
        self.fractal_x = width // 2
        self.fractal_y = height
        self.fractal_size = 120
        self.max_depth = 6
        self.color_shift = 0
        self.cosmic_phase = 0
        self.stars = [(random.randint(0, width), random.randint(0, height), random.uniform(0.5, 2)) for _ in range(150)]
        self.planets = [
            {'name': 'Sun', 'x': width * 0.25, 'y': height * 0.5, 'radius': 30, 'color': (255, 204, 0), 'orbit': 0},
            {'name': 'Mercury', 'x': 0, 'y': 0, 'radius': 5, 'color': (169, 169, 169), 'orbit': 50},
            {'name': 'Venus', 'x': 0, 'y': 0, 'radius': 8, 'color': (255, 215, 0), 'orbit': 80},
            {'name': 'Earth', 'x': 0, 'y': 0, 'radius': 10, 'color': (0, 191, 255), 'orbit': 110},
            {'name': 'Mars', 'x': 0, 'y': 0, 'radius': 7, 'color': (255, 99, 71), 'orbit': 140},
            {'name': 'Jupiter', 'x': 0, 'y': 0, 'radius': 20, 'color': (210, 180, 140), 'orbit': 200},
            {'name': 'Saturn', 'x': 0, 'y': 0, 'radius': 18, 'color': (238, 232, 170), 'orbit': 260},
            {'name': 'Uranus', 'x': 0, 'y': 0, 'radius': 14, 'color': (173, 216, 230), 'orbit': 310},
            {'name': 'Neptune', 'x': 0, 'y': 0, 'radius': 13, 'color': (65, 105, 225), 'orbit': 350}
        ]

    def _generate_palette(self):
        palette = []
        for i in range(5):
            hue = (self.base_hue + i * 40) % 360
            sat = 0.8 + 0.2 * (i % 2)
            val = 0.9 - 0.1 * (i % 3)
            palette.append(self._hsv_to_rgb(hue, sat, val))
        return palette

    def _hsv_to_rgb(self, h, s, v):
        h = h % 360
        h = h / 60.0
        i = math.floor(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        if i == 0: r, g, b = v, t, p
        elif i == 1: r, g, b = q, v, p
        elif i == 2: r, g, b = p, v, t
        elif i == 3: r, g, b = p, q, v
        elif i == 4: r, g, b = t, p, v
        else: r, g, b = v, p, q
        return (int(r * 255), int(g * 255), int(b * 255))

    def create_bubble_surface(self, size, hue):
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        for radius in range(size, 0, -1):
            alpha = int(255 * (radius / size) * 0.9)
            color = self._hsv_to_rgb(hue, 1.0, 1.0 - (radius / size) * 0.3)
            pygame.draw.circle(surf, (*color, alpha), (size, size), radius)
        return surf

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.background = pygame.Surface((width, height))
        self.wave_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.equalizer_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.particle_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.fractal_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.fractal_x = width // 2
        self.fractal_y = height
        self.stars = [(random.randint(0, width), random.randint(0, height), random.uniform(0.5, 2)) for _ in range(150)]
        self.planets[0]['x'] = width * 0.25
        self.planets[0]['y'] = height * 0.5

    def update_particles(self, volume, freq_data):
        """Bubbles form patterns based on frequency."""
        if volume > 0.1:
            # Analyze frequency bands
            low_freq = np.mean(freq_data[:5])  # Low: 0-4
            mid_freq = np.mean(freq_data[5:11])  # Mid: 5-10
            high_freq = np.mean(freq_data[11:])  # High: 11-15
            dominant = max(low_freq, mid_freq, high_freq)

            pattern = 'spiral' if dominant == low_freq else 'radial' if dominant == mid_freq else 'wave'
            bubble_count = int(volume * 10)
            
            for _ in range(bubble_count):
                hue = (self.base_hue + random.uniform(0, 360)) % 360
                size = int(10 + volume * 15 + dominant * 10)
                bubble_surf = self.create_bubble_surface(size, hue)
                spawn_x = self.width // 2
                spawn_y = self.height * 0.4
                
                if pattern == 'spiral':  # Low freq: tight spiral
                    angle = self.time * 0.1 + _ * (2 * math.pi / bubble_count)
                    radius = volume * 50
                    vel_x = math.cos(angle) * 2
                    vel_y = math.sin(angle) * 2
                elif pattern == 'radial':  # Mid freq: starburst
                    angle = _ * (2 * math.pi / bubble_count)
                    speed = 2 + volume * 3
                    vel_x = math.cos(angle) * speed
                    vel_y = math.sin(angle) * speed
                else:  # High freq: scattered waves
                    angle = random.uniform(0, 2 * math.pi)
                    speed = 1 + volume * 2
                    vel_x = math.cos(angle) * speed
                    vel_y = math.sin(angle) * speed * 0.5

                self.particles.append({
                    'pos': [spawn_x, spawn_y],
                    'vel': [vel_x, vel_y],
                    'size': size,
                    'base_size': size,
                    'hue': hue,
                    'surface': bubble_surf,
                    'life': 90,
                    'wave_phase': random.uniform(0, 2 * math.pi),
                    'freq_idx': random.randint(0, len(freq_data) - 1),
                    'trail': [],
                    'pattern': pattern
                })

        self.particle_layer.fill((0, 0, 0, 0))
        for p in self.particles[:]:
            freq_amplitude = freq_data[p['freq_idx']] if freq_data.any() else 0.5
            wave_factor = math.sin(self.time * 0.03 + p['wave_phase']) * freq_amplitude * 1.5
            
            if p['pattern'] == 'spiral':
                p['pos'][0] += p['vel'][0] + wave_factor * 0.5
                p['pos'][1] += p['vel'][1] + wave_factor * 0.5
            elif p['pattern'] == 'radial':
                p['pos'][0] += p['vel'][0]
                p['pos'][1] += p['vel'][1]
            else:  # wave
                p['pos'][0] += p['vel'][0] + wave_factor
                p['pos'][1] += p['vel'][1] + wave_factor * 0.5
            
            p['pos'][1] = min(p['pos'][1], self.height * 0.8)  # Keep above equalizer
            
            p['size'] = p['base_size'] * (1 + freq_amplitude * 0.3 * math.sin(self.time * 0.08 + p['wave_phase']))
            p['hue'] = (p['hue'] + 3 + freq_amplitude * 5) % 360
            p['surface'] = self.create_bubble_surface(int(p['size']), p['hue'])
            
            p['trail'].append((int(p['pos'][0]), int(p['pos'][1])))
            if len(p['trail']) > 3:
                p['trail'].pop(0)
            for i, pos in enumerate(p['trail']):
                alpha = int(255 * (i + 1) / len(p['trail']) * (p['life'] / 90) * 0.4)
                pygame.draw.circle(self.particle_layer, (*self._hsv_to_rgb(p['hue'], 1.0, 0.7), alpha), pos, int(p['size'] * 0.3))
            
            if p['life'] > 0:
                surf_size = p['surface'].get_width()
                self.particle_layer.blit(p['surface'], 
                                        (int(p['pos'][0] - surf_size // 2), 
                                         int(p['pos'][1] - surf_size // 2)))
                p['life'] -= 1
            else:
                self.particles.remove(p)
        self.particle_count = len(self.particles)

    def draw_fractal(self, volume):
        self.fractal_layer.fill((0, 0, 0, 0))
        self.fractal_size = 120 + volume * 70
        self.color_shift = (self.color_shift + volume * 15) % 360
        if self.fractal_type == 'tree':
            self._draw_branch(self.fractal_layer, self.fractal_x, self.fractal_y,
                            self.fractal_size, self.max_depth, -math.pi / 2)
        else:
            p1 = (self.fractal_x, self.fractal_y - self.fractal_size)
            p2 = (self.fractal_x - self.fractal_size * 0.866, self.fractal_y + self.fractal_size * 0.5)
            p3 = (self.fractal_x + self.fractal_size * 0.866, self.fractal_y + self.fractal_size * 0.5)
            self._draw_sierpinski(self.fractal_layer, p1, p2, p3, self.max_depth)

    def _draw_branch(self, surface, x, y, length, depth, angle):
        if depth <= 0 or length < 2:
            return
        end_x = x + math.cos(angle) * length
        end_y = y - math.sin(angle) * length
        hue = (self.color_shift + depth * 40) % 360
        saturation = 0.8 - depth / self.max_depth * 0.2
        value = 0.9 - depth / self.max_depth * 0.2
        color = self._hsv_to_rgb(hue, saturation, value)
        thickness = max(1, int(depth * 1.5))
        pygame.draw.line(surface, color, (int(x), int(y)), (int(end_x), int(end_y)), thickness)
        branch_angle = 0.35 + (1 - depth / self.max_depth) * 0.25
        new_length = length * 0.75
        self._draw_branch(surface, end_x, end_y, new_length, depth - 1, angle + branch_angle)
        self._draw_branch(surface, end_x, end_y, new_length, depth - 1, angle - branch_angle)

    def _draw_sierpinski(self, surface, p1, p2, p3, depth):
        if depth <= 0:
            hue = (self.color_shift + depth * 50) % 360
            color = self._hsv_to_rgb(hue, 0.9, 1.0)
            pygame.draw.polygon(surface, color, [p1, p2, p3])
            return
        p12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        p23 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
        p31 = ((p3[0] + p1[0]) / 2, (p3[1] + p1[1]) / 2)
        self._draw_sierpinski(surface, p1, p12, p31, depth - 1)
        self._draw_sierpinski(surface, p12, p2, p23, depth - 1)
        self._draw_sierpinski(surface, p31, p23, p3, depth - 1)

    def draw_waves(self, volume):
        self.wave_layer.fill((0, 0, 0, 0))
        for wave in self.waves:
            points = []
            for x in range(0, self.width + 10, 5):
                y = self.height // 2 + math.sin(x * wave['frequency'] + self.time * 0.02 + wave['phase']) * wave['amplitude'] * (1 + volume * 1.2)
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(self.wave_layer, wave['color'], False, points, 3)

    def draw_equalizer(self, freq_data):
        self.equalizer_layer.fill((0, 0, 0, 0))
        bar_width = self.width // (len(freq_data) * 2)
        bar_spacing = bar_width * 1.5
        for i, amplitude in enumerate(freq_data):
            height = int(amplitude * self.height * 0.5)
            hue = (self.base_hue + i * 30 + self.time * 5) % 360
            bloom_size = int(bar_width * 0.8 + amplitude * 10)
            bloom = self.create_bubble_surface(bloom_size, hue)
            pulse = math.sin(self.time * 0.1 + i) * amplitude * 10
            x_pos = i * bar_spacing + bar_width // 2
            y_pos = self.height - height - pulse
            self.equalizer_layer.blit(bloom, 
                                    (int(x_pos - bloom_size), 
                                     int(y_pos - bloom_size // 2)))

    def update(self, volume, freq_data):
        self.update_particles(volume, freq_data)
        self.draw_waves(volume)
        self.draw_fractal(volume)
        self.draw_equalizer(freq_data)
        self.time += 1
        self.cosmic_phase += 0.005
        if random.random() < 0.01:
            self.fractal_type = 'sierpinski' if self.fractal_type == 'tree' else 'tree'

    def render(self, surface):
        try:
            self.background.fill((5, 5, 15))
            for x, y, size in self.stars:
                brightness = (math.sin(self.cosmic_phase + x * 0.01 + y * 0.01) + 1) * 0.5
                color = (int(200 * brightness), int(220 * brightness), int(255 * brightness))
                pygame.draw.circle(self.background, color, (x, y), int(size * brightness))

            sun_x, sun_y = self.planets[0]['x'], self.planets[0]['y']
            for planet in self.planets[1:]:
                orbit_radius = planet['orbit']
                for angle in range(0, 360, 10):
                    x = sun_x + math.cos(math.radians(angle)) * orbit_radius
                    y = sun_y + math.sin(math.radians(angle)) * orbit_radius
                    pygame.draw.circle(self.background, (50, 50, 60), (int(x), int(y)), 1)

            for i, planet in enumerate(self.planets[1:], 1):
                orbit_angle = self.cosmic_phase * (10 / (i + 1))
                planet['x'] = sun_x + math.cos(orbit_angle) * planet['orbit']
                planet['y'] = sun_y + math.sin(orbit_angle) * planet['orbit']
                pygame.draw.circle(self.background, planet['color'], (int(planet['x']), int(planet['y'])), planet['radius'])

            sun_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            for r in range(40, 0, -1):
                alpha = int(100 * (r / 40))
                pygame.draw.circle(sun_surf, (*self.planets[0]['color'], alpha), (40, 40), r)
            self.background.blit(sun_surf, (int(sun_x - 40), int(sun_y - 40)))

            surface.blit(self.background, (0, 0))
            surface.blit(self.wave_layer, (0, 0))
            surface.blit(self.fractal_layer, (0, 0))
            surface.blit(self.equalizer_layer, (0, 0))
            surface.blit(self.particle_layer, (0, 0))
        except Exception as e:
            logging.error(f"Error rendering: {e}")

    def quit(self):
        pass