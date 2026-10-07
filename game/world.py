import pygame
import random
import math


class Platform:
    def __init__(self, x, y, width, height=16, kind="normal"):
        self.rect = pygame.Rect(x, y, width, height)
        self.kind = kind

        # Crumbling platform settings
        self.crumble_timer = None
        self.crumble_duration = 60  # 1 second at 60 FPS

    def start_crumbling(self):
        if self.kind == "crumble" and self.crumble_timer is None:
            self.crumble_timer = self.crumble_duration

    def update(self):
        # Countdown for crumbling platforms
        if self.crumble_timer is not None:
            self.crumble_timer -= 1

            if self.crumble_timer <= 0:
                return True

        return False

    def draw(self, screen, cam_y, frame):

        draw_rect = self.rect.move(
            0,
            -int(cam_y)
        )

        # Shake while crumbling
        if self.crumble_timer is not None:

            shake = int(
                math.sin(frame * 0.8) * 3
            )

            draw_rect.x += shake

        # Platform colours
        if self.kind == "crumble":
            color = (190, 120, 50)

        elif self.kind == "spring":
            color = (240, 210, 40)

        else:
            color = (100, 80, 50)

        pygame.draw.rect(
            screen,
            color,
            draw_rect,
            border_radius=4
        )


def generate_platforms(width, base_y, count=30):

    platforms = []

    # Starting ground
    platforms.append(
        Platform(
            0,
            base_y,
            width,
            20,
            "normal"
        )
    )

    y = base_y - 110

    for i in range(count):

        platform_width = random.randint(80, 200)

        x = random.randint(
            0,
            width - platform_width
        )

        # Choose platform type
        random_value = random.random()

        if random_value < 0.20:
            # 20% crumbling
            kind = "crumble"

        elif random_value < 0.35:
            # 15% spring
            kind = "spring"

        else:
            # 65% normal
            kind = "normal"

        platforms.append(
            Platform(
                x,
                y,
                platform_width,
                16,
                kind
            )
        )

        y -= random.randint(80, 130)

    return platforms


def draw_lava(
    screen,
    lava_y,
    cam_y,
    width,
    height,
    frame
):
    """
    Draw the rising lava with a moving wave effect.
    """

    # Convert world position to screen position
    ly = int(lava_y - cam_y)

    # Only draw if lava is visible
    if ly < height:

        points = [(0, ly)]

        # Create a wavy lava surface
        for x in range(0, width + 20, 20):

            wave_y = ly + int(
                math.sin(
                    x * 0.08 + frame * 0.1
                ) * 8
            )

            points.append(
                (x, wave_y)
            )

        # Fill the bottom of the screen
        points.append(
            (width, height)
        )

        points.append(
            (0, height)
        )

        pygame.draw.polygon(
            screen,
            (220, 60, 20),
            points
        )

        # Lava glow
        glow = pygame.Surface(
            (width, 30),
            pygame.SRCALPHA
        )

        for i in range(15):

            alpha = max(
                0,
                60 - i * 4
            )

            pygame.draw.line(
                glow,
                (255, 100, 0, alpha),
                (0, i),
                (width, i)
            )

        screen.blit(
            glow,
            (0, ly - 15)
        )