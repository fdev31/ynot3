import os
import io
import pygame
import subprocess

from .colors import GREY, SELECTED_COLOR
from .widgets import Button
from . import shapes

OUTPUT_FILENAME = os.environ.get("ANNOTATED", "/tmp/annotated.jpg")


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
        if self.gui.objects:
            self.gui.dirty_annotation = True


class SaveBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "")

    def execute(self):
        pygame.image.save(self.gui.get_annotated_image(), OUTPUT_FILENAME)


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
        pygame.image.save(self.gui.get_annotated_image(), buffer, "png")
        proc.communicate(input=buffer.getvalue())


class BackBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "󰕌")

    def execute(self):
        if self.gui.objects:
            self.gui.objects[-1].instance_removed()
            self.gui.objects = self.gui.objects[:-1]
            self.gui.dirty_annotation = True


class ClearBut(Button):
    def __init__(self, gui):
        super().__init__(gui, "󰗩")

    def execute(self):
        for obj in self.gui.objects:
            obj.instance_removed()
            # Clear all the shapes
        self.gui.objects = []
        self.gui.dirty_annotation = True
