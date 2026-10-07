import pygame

SPEED = 4

# Jump strengths
NORMAL_JUMP = -13
SPRING_JUMP = -22


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms, width):
        dx = 0
        landed_platform = None

        # -----------------------------------------
        # HORIZONTAL MOVEMENT
        # -----------------------------------------

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        # -----------------------------------------
        # JUMP
        # -----------------------------------------

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
        ) and self.on_ground:

            self.vel_y = NORMAL_JUMP
            self.on_ground = False

        # -----------------------------------------
        # GRAVITY
        # -----------------------------------------

        self.vel_y = min(
            self.vel_y + 0.55,
            12
        )

        # -----------------------------------------
        # HORIZONTAL POSITION
        # -----------------------------------------

        self.rect.x = max(
            0,
            min(
                width - self.rect.width,
                self.rect.x + dx
            )
        )

        # -----------------------------------------
        # PLATFORM COLLISION FIX
        # -----------------------------------------

        # Remember where the player's feet were
        # BEFORE vertical movement.
        previous_bottom = self.rect.bottom

        # Move vertically.
        self.rect.y += int(self.vel_y)

        # Assume the player is in the air.
        self.on_ground = False

        # -----------------------------------------
        # LANDING
        # -----------------------------------------

        # Only check platforms while FALLING.
        if self.vel_y > 0:

            for platform in platforms:

                # Check horizontal overlap.
                horizontal_overlap = (
                    self.rect.right > platform.rect.left
                    and self.rect.left < platform.rect.right
                )

                # Check that the player crossed the
                # TOP of the platform while falling.
                crossed_top = (
                    previous_bottom <= platform.rect.top
                    and self.rect.bottom >= platform.rect.top
                )

                if horizontal_overlap and crossed_top:

                    # Put player's feet exactly
                    # on the platform.
                    self.rect.bottom = platform.rect.top

                    # Spring platform
                    if platform.kind == "spring":
                        self.vel_y = SPRING_JUMP

                    # Normal/crumbling platform
                    else:
                        self.vel_y = 0

                    self.on_ground = True

                    # Remember which platform
                    # the player landed on.
                    landed_platform = platform

                    break

        # Return the platform that was landed on.
        return landed_platform

    def draw(self, screen, cam_y):
        dr = self.rect.move(
            0,
            -int(cam_y)
        )

        # Draw player body
        pygame.draw.rect(
            screen,
            self.color,
            dr,
            border_radius=6
        )

        # Draw player's face
        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (
                dr.centerx,
                dr.top + 8
            ),
            7
        )