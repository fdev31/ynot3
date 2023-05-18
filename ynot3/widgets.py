import pygame
import itertools

from . import shapes
from .colors import BLACK, GREY, SELECTED_COLOR


class Icon:
    _index = 0

    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.index = Icon._index
        Icon._index += 1
        self.shape = None


class Button:
    def __init__(self, gui, label="X"):
        self.gui = gui
        font = pygame.font.SysFont("Symbols Nerd Font", 20)
        self.text = font.render(label, True, BLACK)
        self.bg = GREY

    def draw(self, surface, rect):
        pygame.draw.rect(surface, self.bg, rect, border_radius=5)
        sz = self.text.get_size()
        pos = tuple((rect.center[0] - sz[0] // 2, rect.center[1] - sz[1] // 2))
        surface.blit(self.text, pos)


class StatusBar:
    margin = 5
    separation = 20
    # List of distinctive colors
    available_colors = [
        (128, 0, 0),
        (230, 25, 75),
        (255, 255, 25),
        (60, 180, 75),
        (70, 240, 240),
        (240, 50, 230),
        (0, 130, 200),
        (255, 255, 255),
        (0, 0, 0),
    ]
    available_shapes = shapes.all_shapes

    @classmethod
    def getHeight(cls, width, buttons):
        if cls.fitsScreen(width, buttons, 40):
            return 40
        return 20

    @classmethod
    def estimateWidth(cls, buttons, icon_size):
        nb_icons = len(buttons) + len(cls.available_colors) + len(cls.available_shapes)
        return icon_size * nb_icons + cls.margin * (nb_icons - 4) + 2 * cls.separation

    @classmethod
    def fitsScreen(cls, width, buttons, icon_size):
        return not width < cls.estimateWidth(buttons, icon_size)

    def __init__(self, screen, buttons: list, icon_size: int):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, screen.get_width(), icon_size)
        self.icon_size = icon_size
        self.selected_color = self.available_colors[0]
        self.selected_shape = self.available_shapes[0]
        self.available_buttons = buttons

        x_offset = self.margin

        self.icons = []
        for _ in self.available_shapes:
            self.icons.append(Icon(x_offset, 0, self.icon_size))
            x_offset += self.icon_size + self.margin

        x_offset += self.separation
        for _ in self.available_colors:
            self.icons.append(Icon(x_offset, 0, self.icon_size))
            x_offset += self.icon_size

        x_offset += self.separation
        for _ in self.available_buttons:
            self.icons.append(Icon(x_offset, 0, self.icon_size))
            x_offset += self.icon_size + self.margin

    def icon_action(self, index):
        nbs = len(self.available_shapes)
        nbc = len(self.available_colors)
        if index < nbs:
            self.selected_shape = self.available_shapes[index]
        elif index < nbs + nbc:
            self.selected_color = self.available_colors[index - nbs]
        else:
            self.available_buttons[index - nbs - nbc].execute()

    def draw(self):
        # Draw the status bar background

        icon_counter = itertools.count(0)

        radius = 3

        for shape in self.available_shapes:
            color = SELECTED_COLOR if shape == self.selected_shape else GREY
            idx = next(icon_counter)
            icon = self.icons[idx]
            pygame.draw.rect(self.screen, color, icon.rect, border_radius=radius)
            if icon.shape is None:
                icon.shape = shape(
                    color=BLACK,
                    start=icon.rect.topleft,
                    end=icon.rect.bottomright,
                    isDummy=True,
                )
            icon.shape.draw(self.screen)

        for color in self.available_colors:
            idx = next(icon_counter)
            icon = self.icons[idx]
            if color == self.selected_color:
                pygame.draw.rect(
                    self.screen, SELECTED_COLOR, icon.rect, border_radius=radius
                )
            if not getattr(icon, "surface", None):
                icon.surface = shapes.make_color_shape(
                    color, icon.rect.width, icon.rect.height
                )
            self.screen.blit(icon.surface, icon.rect)

        for but in self.available_buttons:
            idx = next(icon_counter)
            icon = self.icons[idx]
            but.draw(self.screen, icon.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, shape in enumerate(self.icons):
                # detect if shape is under cursor
                if shape.rect.collidepoint(event.pos):
                    self.icon_action(idx)
                    return True
