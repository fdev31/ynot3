import math
import pygame

from .colors import BLACK, WHITE

WIDGET_SCALE = 1
SUPERSAMPLE = 4

OUTPUT_FILENAME = "/tmp/annotated.jpg"


def make_color_shape(color: tuple[int, int, int], width: int, height: int):
    w = width * SUPERSAMPLE
    h = height * SUPERSAMPLE
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(list(color) + [0])
    pygame.draw.circle(surf, (50, 50, 50), (w / 2 - 4, h / 2 + 4), int(0.4 * w))
    pygame.draw.circle(surf, color, (w / 2, h / 2), int(0.4 * w))
    return pygame.transform.smoothscale(surf, (width, height))


class Shape:
    _name = "unknown"
    _surface = None
    shadow = (3 * SUPERSAMPLE, 3 * SUPERSAMPLE)
    shadow_color = (0, 0, 0, 150)

    def __init__(
        self,
        color: tuple[int, int, int] | list[int],
        start: tuple[int, int] | list[int],
        end: tuple[int, int] | list[int],
        isDummy=False,
    ):
        self.color = color
        self.start = start
        self.end = end
        self.isDummy = isDummy

    @property
    def inv_color(self):
        r, g, b = self.color

        # Calculate relative luminance
        L = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0

        # Choose white or black text color based on luminance
        if L > 0.5:
            return BLACK
        else:
            return WHITE

    @property
    def rect(self):
        return pygame.Rect(
            self.start, (self.end[0] - self.start[0], self.end[1] - self.start[1])
        )

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError(
            "Missing draw implementation for the {} class.".format(self._name)
        )

    def instance_removed(self):
        pass


class Arrow(Shape):
    thickness = 5
    arrowhead_size = 20
    _name = "arrow"
    _old_pos = None
    _ssurface = None

    @property
    def fixed_size(self):
        if self.isDummy:
            return self.arrowhead_size
        else:
            return self.arrowhead_size * WIDGET_SCALE

    def draw(self, surface):
        start = [SUPERSAMPLE * i for i in self.start]
        end = [SUPERSAMPLE * i for i in self.end]

        if not self._surface or self._old_pos != (start, end, WIDGET_SCALE):
            self._old_pos = (start, end, WIDGET_SCALE)

            if self.isDummy:
                # add some padding
                end[0] -= 5
                end[1] -= 5
                start[0] += 10
                start[1] += 10

            # Calculate the angle of the line from start to end
            angle = math.atan2(end[1] - start[1], end[0] - start[0])
            if not self._ssurface:
                supersampled_surface = pygame.Surface(
                    tuple(SUPERSAMPLE * i for i in surface.get_size()), pygame.SRCALPHA
                )
                self._ssurface = supersampled_surface
            else:
                self._ssurface.fill((0, 0, 0, 0))

            # Calculate the endpoint of the line from start to end
            line_length = math.sqrt((end[1] - start[1]) ** 2 + (end[0] - start[0]) ** 2)
            end_point = (
                int(start[0] + line_length * math.cos(angle)),
                int(start[1] + line_length * math.sin(angle)),
            )

            if self.isDummy:
                sz = int(self.fixed_size * SUPERSAMPLE * 0.7)
            else:
                sz = (
                    self.fixed_size
                    * SUPERSAMPLE
                    * (WIDGET_SCALE * 0.5 if WIDGET_SCALE > 1 else 1)
                )
            # shadow
            if not self.isDummy:
                pygame.draw.polygon(
                    self._ssurface,
                    self.shadow_color,
                    (
                        end_point,
                        (
                            (end_point[0] - sz * math.cos(angle - math.pi / 6))
                            - self.shadow[0],
                            (end_point[1] - sz * math.sin(angle - math.pi / 6))
                            + self.shadow[1],
                        ),
                        (
                            (end_point[0] - sz * math.cos(angle + math.pi / 6))
                            - self.shadow[0],
                            (end_point[1] - sz * math.sin(angle + math.pi / 6))
                            + self.shadow[1],
                        ),
                    ),
                )
                sline_length = line_length - (sz // 2)
                send_point = (
                    int(start[0] - self.shadow[0] + sline_length * math.cos(angle)),
                    int(start[1] + self.shadow[1] + sline_length * math.sin(angle)),
                )
                # Draw the line from start to end
                pygame.draw.line(
                    self._ssurface,
                    self.shadow_color,
                    start,
                    send_point,
                    self.thickness * WIDGET_SCALE * SUPERSAMPLE + 5,
                )
            # real shape
            # Draw a circle t point A
            pygame.draw.circle(
                self._ssurface,
                self.color,
                start,
                2 * (1 if self.isDummy else WIDGET_SCALE * SUPERSAMPLE),
            )
            # Draw the arrowhead at point B
            pygame.draw.polygon(
                self._ssurface,
                self.color,
                (
                    (end_point[0], end_point[1]),
                    (
                        end_point[0] - sz * math.cos(angle - math.pi / 6),
                        end_point[1] - sz * math.sin(angle - math.pi / 6),
                    ),
                    (
                        end_point[0] - sz * math.cos(angle + math.pi / 6),
                        end_point[1] - sz * math.sin(angle + math.pi / 6),
                    ),
                ),
            )
            line_length -= sz // 2
            end_point = (
                int(start[0] + line_length * math.cos(angle)),
                int(start[1] + line_length * math.sin(angle)),
            )
            # Draw the line from start to end
            pygame.draw.line(
                self._ssurface,
                self.color,
                start,
                end_point,
                self.thickness * (2 if self.isDummy else WIDGET_SCALE * SUPERSAMPLE),
            )
            self._surface = pygame.transform.smoothscale(
                self._ssurface, surface.get_size()
            )
        surface.blit(self._surface, (0, 0))


class Bullet(Shape):
    _name = "bullet"
    size = 12
    _counter = 0

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        if not self.isDummy:
            Bullet._counter += 1
        self.counter = Bullet._counter
        self._old_scale = 0
        self._surface = None

    def instance_removed(self):
        Bullet._counter -= 1

    @property
    def corrected_size(self):
        return self.size * SUPERSAMPLE

    def draw(self, surface):
        if WIDGET_SCALE != self._old_scale:
            self._font = pygame.font.SysFont(
                "Arial",
                48
                * (
                    1
                    if self.isDummy
                    else (WIDGET_SCALE // 2 if WIDGET_SCALE > 1 else 1)
                ),
                bold=True,
            )
            self.text = self._font.render(
                "2" if self.isDummy else str(self.counter), True, self.inv_color
            )
            self._surface = None

        if not self._surface:
            border_sz = int(
                SUPERSAMPLE * 3 * (WIDGET_SCALE * 0.5 if WIDGET_SCALE > 1 else 1)
            )
            side = max(self.text.get_size()[0] + 10, self.corrected_size) + border_sz

            supersampled_surface = pygame.Surface(
                (side + border_sz, side + border_sz), pygame.SRCALPHA
            )
            supersampled_surface.fill((0, 0, 0, 0))
            corrected_rect = pygame.Rect(0, 0, side, side)
            corrected_rect[0] += border_sz // 2
            corrected_rect[1] += border_sz // 2

            if not self.isDummy:  # draw shadow
                pygame.draw.circle(
                    supersampled_surface,
                    self.shadow_color,
                    (corrected_rect.center[0] - 4, corrected_rect.center[1] + 4),
                    (side // 2),
                )
            pygame.draw.circle(
                supersampled_surface, self.inv_color, corrected_rect.center, (side // 2)
            )
            pygame.draw.circle(
                supersampled_surface,
                self.color,
                corrected_rect.center,
                (side - border_sz) // 2,
            )

            pos = list(corrected_rect.center)
            text_size = self.text.get_size()
            pos[0] -= text_size[0] // 2
            pos[1] -= text_size[1] // 2
            supersampled_surface.blit(self.text, pos)
            sz = self.rect.size[0] if self.isDummy else (self.size * WIDGET_SCALE * 2)
            self._surface = pygame.transform.smoothscale(supersampled_surface, (sz, sz))

        if self.isDummy:
            surface.blit(
                self._surface, [i - self.rect.width // 2 for i in self.rect.center]
            )
        else:
            surface.blit(
                self._surface,
                (
                    self.start[0] - self.size * WIDGET_SCALE,
                    self.start[1] - self.size * WIDGET_SCALE,
                ),
            )


class Rectangle(Shape):
    _name = "rectangle"
    thickness = 3

    def draw(self, surface):
        if self.isDummy:
            rect = self.rect.copy()
            rect.width -= 6
            rect.height -= 6
            rect.x += 3
            rect.y += 3
            pygame.draw.rect(surface, self.color, rect, width=2)
        else:
            pygame.draw.rect(
                surface,
                list(self.color) + [50],
                self.rect,
            )
            pygame.draw.rect(
                surface,
                self.color,
                self.rect,
                width=1 if self.isDummy else self.thickness * WIDGET_SCALE,
            )

    @property
    def rect(self):
        x = min(self.start[0], self.end[0])
        y = min(self.start[1], self.end[1])
        width = max(self.start[0], self.end[0]) - x
        height = max(self.start[1], self.end[1]) - y
        return pygame.Rect(x, y, width, height)


all_shapes = [Rectangle, Arrow, Bullet]
