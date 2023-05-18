import os
import io
import pygame
import itertools
import subprocess

from .colors import BLACK, WHITE, GREY
from . import shapes

STATUS_HEIGHT = 40
DEFAULT_COLOR = (255, 255, 0)
# Nice orange
SELECTED_COLOR = (255, 128, 0)

OUTPUT_FILENAME = "/tmp/annotated.jpg"


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


class BigSmallBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "󰧴")

    def execute(self):
        if shapes.WIDGET_SCALE == 1:
            shapes.WIDGET_SCALE = 2
            self.bg = SELECTED_COLOR
        else:
            shapes.WIDGET_SCALE = 1
            self.bg = GREY


class SaveBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "")

    def execute(self):
        pygame.image.save(self.gui.canvas, OUTPUT_FILENAME)


class CopyBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "")

    def execute(self):
        if os.environ.get("WAYLAND_DISPLAY"):
            proc = subprocess.Popen(
                ["wl-copy", "-t", "image/png"], stdin=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(
                ["xclip", "-selection", "clipboard", "-t", "image/png"],
                stdin=subprocess.PIPE,
            )
        buffer = io.BytesIO()
        pygame.image.save(self.gui.canvas, buffer, "png")
        proc.communicate(input=buffer.getvalue())


class BackBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "󰕌")

    def execute(self):
        if self.gui.objects:
            self.gui.objects[-1].instance_removed()
            self.gui.objects = self.gui.objects[:-1]


class ClearBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "󰗩")

    def execute(self):
        for obj in self.gui.objects:
            obj.instance_removed()
            # Clear all the shapes
        self.gui.objects = []


class StatusBar:
    margin = 5
    separation = 20
    # List of distinctive colors
    available_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (0, 255, 255),
        (255, 255, 0),
        (255, 0, 255),
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
    def fitsScreen(cls, width, buttons, icon_size):
        return not width < icon_size * (
            len(buttons) + len(cls.available_colors) + len(cls.available_shapes)
        ) + (cls.separation * 2)

    def __init__(self, screen, buttons=[]):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, screen.get_width(), STATUS_HEIGHT)
        self.icon_size = STATUS_HEIGHT
        self.selected_color = DEFAULT_COLOR
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
        pygame.draw.rect(self.screen, GREY, self.rect)

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
                    isFake=True,
                )
            icon.shape.draw(self.screen)

        for color in self.available_colors:
            idx = next(icon_counter)
            icon = self.icons[idx]
            if color == self.selected_color:
                pygame.draw.rect(
                    self.screen, SELECTED_COLOR, icon.rect, border_radius=radius
                )
            pygame.draw.circle(
                self.screen, color, icon.rect.center, icon.rect.width // 2 - 2
            )

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
                    break


class GUI:
    def __init__(self, background):
        global STATUS_HEIGHT
        self.objects: list[shapes.Shape] = []
        self.dragging = False
        self.canvas: None | pygame.Surface = None
        self.but_undo = BackBut(self)
        self.but_save = SaveBut(self)
        self.but_clear = ClearBut(self)
        self.but_copy = CopyBut(self)
        buttons = [
            self.but_undo,
            self.but_copy,
            self.but_save,
            BigSmallBut(self),
            self.but_clear,
        ]
        bg_rect = background.get_rect()
        STATUS_HEIGHT = StatusBar.getHeight(bg_rect.width, buttons)
        self.screen = pygame.display.set_mode(
            (bg_rect.width, bg_rect.height + STATUS_HEIGHT)
        )

        self.background = background.convert_alpha()
        self.status_bar = StatusBar(self.screen, buttons)

    def handle_event(self, event):
        if event.pos[1] < STATUS_HEIGHT:
            return self.status_bar.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left mouse button
                self.dragging = True

                # Add a shape to the list of shapes
                start_pos = list(event.pos)
                start_pos[1] -= STATUS_HEIGHT
                shape = self.status_bar.selected_shape(
                    color=self.status_bar.selected_color,
                    start=start_pos,
                    end=start_pos,
                )
                self.objects.append(shape)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left mouse button
                if self.dragging:
                    pos = list(event.pos)
                    pos[1] -= STATUS_HEIGHT
                    self.objects[-1].end = pos
                    self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                pos = list(event.pos)
                pos[1] -= STATUS_HEIGHT
                if self.objects:
                    self.objects[-1].end = pos

    def draw(self):
        #         print("******************************************")
        self.status_bar.draw()

        surf = self.background.copy()
        self.canvas = surf

        for shape in self.objects:
            shape.draw(surf)
        self.screen.blit(surf, (0, STATUS_HEIGHT))

        pygame.display.update()


def main(image_path: str):
    pygame.init()
    pygame.display.set_caption("Draw Shapes")

    background = pygame.image.load(image_path)

    # Create the GUI
    gui = GUI(background)

    clock = pygame.time.Clock()
    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if event.type in (
                    pygame.MOUSEBUTTONDOWN,
                    pygame.MOUSEBUTTONUP,
                    pygame.MOUSEMOTION,
                    pygame.BUTTON_WHEELDOWN,
                    pygame.BUTTON_WHEELUP,
                ):
                    gui.handle_event(event)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            gui.but_save.execute()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_c:
                            gui.but_clear.execute()
                        elif event.key == pygame.K_BACKSPACE:
                            gui.but_undo.execute()
                        elif event.key == pygame.K_r:
                            gui.status_bar.selected_shape = shapes.Rectangle
                        elif event.key == pygame.K_a:
                            gui.status_bar.selected_shape = shapes.Arrow
                        elif event.key == pygame.K_e:
                            gui.status_bar.selected_shape = shapes.Bullet

        # Update the screen
        gui.draw()
        clock.tick(60)
        pygame.display.flip()

    gui.but_copy.execute()
    # Quit pygame
    pygame.quit()
