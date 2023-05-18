import os
import pygame

from .widgets import StatusBar
from .colors import GREY
from .buttons import BigSmallBut, SaveBut, CopyBut, BackBut, ClearBut
from . import shapes


class Snap:
    level = int(os.environ.get("SNAPPING", 8))

    @classmethod
    def getSnapped(cls, coord: tuple[int, int]) -> list[int]:
        l = cls.level
        if not l:
            return list(coord)
        return [((l // 2 + coord[0]) // l) * l, ((l // 2 + coord[1]) // l) * l]


class GUI:
    statusbar_height = 40

    def __init__(self, background: pygame.Surface) -> None:
        self.objects: list[shapes.Shape] = []
        self.dragging = False
        self.but_undo = BackBut(self)
        self.but_save = SaveBut(self)
        self.but_clear = ClearBut(self)
        self.but_copy = CopyBut(self)
        self.dirty_statusbar = True
        self.dirty_annotation = True
        buttons = [
            self.but_undo,
            self.but_copy,
            self.but_save,
            BigSmallBut(self),
            self.but_clear,
        ]
        bg_rect = background.get_rect()
        self.statusbar_height = StatusBar.getHeight(bg_rect.width, buttons)
        self.screen = pygame.display.set_mode(
            (
                max(
                    bg_rect.width,
                    StatusBar.estimateWidth(buttons, self.statusbar_height),
                ),
                bg_rect.height + self.statusbar_height,
            )
        )

        self.background = background
        self.statusbar_surface = pygame.Surface(
            (self.screen.get_width(), self.statusbar_height), pygame.SRCALPHA
        ).convert_alpha()
        self.statusbar = StatusBar(
            self.statusbar_surface, buttons, self.statusbar_height
        )
        self.annotation_overlay = pygame.Surface(
            self.background.get_size(), pygame.SRCALPHA
        ).convert_alpha()

    def get_annotated_image(self):
        surface = pygame.Surface(self.background.get_size(), pygame.SRCALPHA)
        surface.blit(self.background, (0, 0))
        surface.blit(self.annotation_overlay, (0, 0))
        return surface

    def handle_event(self, event):
        if event.pos[1] < self.statusbar_height:
            if self.statusbar.handle_event(event):
                self.dirty_statusbar = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left mouse button
                self.dragging = True

                # Add a shape to the list of shapes
                start_pos = Snap.getSnapped(event.pos)
                start_pos[1] -= self.statusbar_height
                shape = self.statusbar.selected_shape(
                    color=self.statusbar.selected_color,
                    start=start_pos,
                    end=start_pos,
                )
                self.objects.append(shape)
                self.dirty_annotation = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left mouse button
                if self.dragging:
                    pos = Snap.getSnapped(event.pos)
                    pos[1] -= self.statusbar_height
                    self.objects[-1].end = pos
                    self.dragging = False
                    self.dirty_annotation = True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                pos = list(event.pos)
                pos[1] -= self.statusbar_height
                if self.objects:
                    self.objects[-1].end = pos
                    self.dirty_annotation = True

    def draw(self):
        if self.dirty_statusbar:
            self.statusbar_surface.fill(GREY)
            self.statusbar.draw()
            self.screen.blit(self.statusbar_surface, (0, 0))
            self.dirty_statusbar = False

        if self.dirty_annotation:
            self.screen.blit(self.background, (0, self.statusbar_height))
            self.annotation_overlay.fill((0, 0, 0, 0))

            for shape in self.objects:
                shape.draw(self.annotation_overlay)

            self.screen.blit(self.annotation_overlay, (0, self.statusbar_height))
            self.dirty_annotation = False

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
                            gui.dirty_annotation = True
                        elif event.key == pygame.K_BACKSPACE:
                            gui.but_undo.execute()
                            gui.dirty_annotation = True
                        elif event.key == pygame.K_r:
                            gui.statusbar.selected_shape = shapes.Rectangle
                            gui.dirty_statusbar = True
                        elif event.key == pygame.K_a:
                            gui.statusbar.selected_shape = shapes.Arrow
                            gui.dirty_statusbar = True
                        elif event.key == pygame.K_e:
                            gui.statusbar.selected_shape = shapes.Bullet
                            gui.dirty_statusbar = True

        # Update the screen
        gui.draw()
        clock.tick(60)
        pygame.display.flip()

    gui.but_copy.execute()
    # Quit pygame
    pygame.quit()
