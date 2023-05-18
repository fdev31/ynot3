import os
import pygame

from .widgets import StatusBar
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

        self.background = background.convert_alpha()
        self.statusbar = StatusBar(self.screen, buttons, self.statusbar_height)

    def handle_event(self, event):
        if event.pos[1] < self.statusbar_height:
            return self.statusbar.handle_event(event)

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
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left mouse button
                if self.dragging:
                    pos = Snap.getSnapped(event.pos)
                    pos[1] -= self.statusbar_height
                    self.objects[-1].end = pos
                    self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                pos = list(event.pos)
                pos[1] -= self.statusbar_height
                if self.objects:
                    self.objects[-1].end = pos

    def draw(self):
        self.statusbar.draw()

        surf = self.background.copy()
        self.canvas = surf

        for shape in self.objects:
            shape.draw(surf)
        self.screen.blit(surf, (0, self.statusbar_height))

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
                            gui.statusbar.selected_shape = shapes.Rectangle
                        elif event.key == pygame.K_a:
                            gui.statusbar.selected_shape = shapes.Arrow
                        elif event.key == pygame.K_e:
                            gui.statusbar.selected_shape = shapes.Bullet

        # Update the screen
        gui.draw()
        clock.tick(60)
        pygame.display.flip()

    gui.but_copy.execute()
    # Quit pygame
    pygame.quit()
