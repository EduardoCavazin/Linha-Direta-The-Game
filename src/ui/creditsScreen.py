import sys
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

import pygame

from src.core.screenUtils import get_optimal_screen_size, center_window
from src.core.constants import Rendering
from src.core.logging_utils import log_error
from src.ui.ui_components import (
    create_particle_system, update_and_draw_particles,
    WHITE, GOLD
)


Color = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]


def make_vertical_gradient(size: Tuple[int, int], top: Color, bottom: Color) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h)).convert()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf


def draw_rounded_bg(surface: pygame.Surface, rect: pygame.Rect, color_rgba: RGBA, radius: int, pad: Tuple[int, int]=(12, 6)) -> None:
    w = rect.width + pad[0] * 2
    h = rect.height + pad[1] * 2
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bg, color_rgba, bg.get_rect(), border_radius=radius)
    surface.blit(bg, (rect.x - pad[0], rect.y - pad[1]))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    cur = words[0]
    for w in words[1:]:
        test = f"{cur} {w}"
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


@dataclass
class BlockSpec:
    lines: List[str]
    font: pygame.font.Font
    color: Color
    center_x: int
    center_y: int
    bg_rgba: Optional[RGBA] = (0, 0, 0, 120)
    radius: int = 10
    antialias: bool = True
    line_spacing: int = 6


class CreditsScreen:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.white: Color = WHITE
        self.gold: Color = GOLD
        self.subtle: Color = (220, 220, 220)

        self.particles = create_particle_system(screen_width, screen_height, 50)

        base_w, base_h = 1280, 720
        scale = min(screen_width / base_w, screen_height / base_h)
        def s(px: int) -> int:
            return max(1, int(round(px * scale)))

        self.font_large  = pygame.font.Font(None, s(72))  
        self.font_large.set_bold(True)
        self.font_medium = pygame.font.Font(None, s(48))  
        self.font_small  = pygame.font.Font(None, s(36)) 

        base_path = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(base_path, "../.."))
        background_path = os.path.join(project_root, 'assets', 'ui', 'menu', 'creditos.png')
        
        try:
            self.bg = pygame.image.load(background_path)
            self.bg = pygame.transform.scale(self.bg, (screen_width, screen_height))
        except (FileNotFoundError, pygame.error) as e:
            log_error(f"Erro ao carregar background dos créditos", "creditsScreen", e)
            self.bg = make_vertical_gradient(
                (screen_width, screen_height),
                top=(45, 45, 45),
                bottom=(75, 75, 75)
            )

        center_x = screen_width // 2
        spacing  = s(30)
        y_start  = screen_height // 2 - s(220)
        max_text_width = int(screen_width * 0.82)

        def w(font, txt): return wrap_text(txt, font, max_text_width)

        blocks: List[BlockSpec] = [
            BlockSpec(["Linha Direta - The Game"], self.font_medium, self.white, center_x, y_start + spacing * 1, (0, 0, 0, 120), s(10)),

            BlockSpec(["Orientador:"], self.font_medium, self.gold, center_x, y_start + spacing * 4, (0, 0, 0, 100), s(10)),
            BlockSpec(w(self.font_small, "Professor Dr. Eduardo Henrique Molina Cruz"), self.font_small, self.white, center_x, y_start + spacing * 5.5),

            BlockSpec(["Desenvolvedores:"], self.font_medium, self.gold, center_x, y_start + spacing * 8, (0, 0, 0, 100), s(10)),
            BlockSpec(w(self.font_small, "Caue Grande Yanagihara - Programação, Design, Arte, Música"), self.font_small, self.white, center_x, y_start + spacing * 9.5),
            BlockSpec(["Eduardo Tormena Cavazin - Programação"], self.font_small, self.white, center_x, y_start + spacing * 11),
            BlockSpec(w(self.font_small, "Vinicius Margonar - Programação, Design, Arte, Música"), self.font_small, self.white, center_x, y_start + spacing * 12.5),

            BlockSpec(["Python + Pygame"], self.font_small, self.white, center_x, y_start + spacing * 15),

            BlockSpec(["Obrigado por jogar!"], self.font_small, self.gold, center_x, y_start + spacing * 17.5, (0, 0, 0, 140), s(10)),

            BlockSpec(["ESC/Enter/Backspace: Voltar"], self.font_small, self.subtle, center_x, y_start + spacing * 20, (0, 0, 0, 90), s(8)),
        ]

        self.rendered: List[Tuple[pygame.Surface, pygame.Rect, Optional[RGBA], int]] = []
        for b in blocks:
            line_surfs: List[pygame.Surface] = [b.font.render(t, b.antialias, b.color).convert_alpha() for t in b.lines]
            heights = [ls.get_height() for ls in line_surfs]
            total_h = sum(heights) + b.line_spacing * (len(heights) - 1)

            top = int(b.center_y - total_h // 2)
            for ls in line_surfs:
                rect = ls.get_rect()
                rect.centerx = b.center_x
                rect.y = top
                top += ls.get_height() + b.line_spacing
                self.rendered.append((ls, rect, b.bg_rgba, b.radius))

        self.fade_time_ms = 650
        self.start_ticks = pygame.time.get_ticks()

    def _current_alpha(self) -> int:
        elapsed = pygame.time.get_ticks() - self.start_ticks
        t = max(0.0, min(1.0, elapsed / self.fade_time_ms))
        return int(255 * t)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.bg, (0, 0))

        update_and_draw_particles(self.particles, screen)

        alpha = self._current_alpha()
        for surf, rect, bg_rgba, radius in self.rendered:
            if bg_rgba:
                draw_rounded_bg(screen, rect, bg_rgba, radius)
            if alpha < 255:
                tmp = surf.copy()
                tmp.set_alpha(alpha)
                screen.blit(tmp, rect)
            else:
                screen.blit(surf, rect)


def _should_go_back(event: pygame.event.Event) -> bool:
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE):
        return True
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.JOYBUTTONDOWN):
        return True
    return False


def run_credits_screen(screen_width: int, screen_height: int) -> str:
    pygame.init()
    pygame.display.set_allow_screensaver(True)

    center_window(screen_width, screen_height)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Créditos - Linha Direta")

    credits_screen = CreditsScreen(screen_width, screen_height)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if _should_go_back(event):
                return "back"

        credits_screen.draw(screen)
        pygame.display.flip()
        clock.tick(Rendering.TARGET_FPS)


if __name__ == "__main__":
    w, h = get_optimal_screen_size()
    run_credits_screen(w, h)
