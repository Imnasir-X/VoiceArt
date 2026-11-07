"""Render a still frame of the visualiser to docs/preview.png without a mic.

Usage: SDL_VIDEODRIVER=dummy python scripts/render_preview.py
"""

import os
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame  # noqa: E402

from visualizer import Visualizer  # noqa: E402


def main(frames=150, width=1280, height=720):
    pygame.init()
    surface = pygame.Surface((width, height))
    vis = Visualizer(width, height)
    rng = np.random.default_rng(7)
    for i in range(frames):
        volume = 0.55 + 0.35 * np.sin(i / 9)
        freq = np.clip(np.abs(np.sin(np.arange(16) / 3 + i / 15)) + rng.normal(0, 0.05, 16), 0, 1)
        vis.update(float(volume), freq)
    surface.fill((0, 0, 0))
    vis.render(surface)
    out = ROOT / "docs" / "preview.png"
    out.parent.mkdir(exist_ok=True)
    pygame.image.save(surface, str(out))
    pygame.quit()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
