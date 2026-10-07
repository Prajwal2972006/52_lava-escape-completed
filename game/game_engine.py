import pygame

from game.player import Player
from game.world import generate_platforms, draw_lava


WIDTH, HEIGHT = 500, 640
FPS = 60

BG = (20, 15, 30)

GROUND_Y = HEIGHT + 200


class GameEngine:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption("Lava Escape")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            20,
            bold=True
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            42,
            bold=True
        )

        self.reset()

    def reset(self):

        self.platforms = generate_platforms(
            WIDTH,
            GROUND_Y
        )

        self.player = Player(
            WIDTH // 2 - 16,
            GROUND_Y - 50
        )

        self.cam_y = 0

        self.lava_y = GROUND_Y + 60

        # Normal lava speed
        self.lava_rise = 0.4

        self.score = 0

        self.game_over = False
        self.won = False

        self.top_y = self.platforms[-1].rect.y

        self.frame = 0

        # -----------------------------
        # Lava burst settings
        # -----------------------------

        self.surge_active = False
        self.surge_end_frame = 0
        self.next_surge_frame = FPS * 15

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                self.reset()

        return True

    def update(self):

        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()

        # ---------------------------------
        # UPDATE PLAYER
        # ---------------------------------

        landed_platform = self.player.update(
            keys,
            self.platforms,
            WIDTH
        )

        # ---------------------------------
        # CRUMBLING PLATFORM
        # ---------------------------------

        if landed_platform is not None:

            if landed_platform.kind == "crumble":

                landed_platform.start_crumbling()

        # ---------------------------------
        # UPDATE PLATFORMS
        # ---------------------------------

        remaining_platforms = []

        for platform in self.platforms:

            should_remove = platform.update()

            if not should_remove:
                remaining_platforms.append(platform)

        self.platforms = remaining_platforms

        # ---------------------------------
        # CAMERA
        # ---------------------------------

        target = (
            self.player.rect.centery
            - HEIGHT // 2
        )

        if target < self.cam_y:
            self.cam_y = target

        # ---------------------------------
        # LAVA BURST
        # ---------------------------------

        if (
            self.frame >= self.next_surge_frame
            and not self.surge_active
        ):

            self.surge_active = True

            self.surge_end_frame = (
                self.frame + FPS * 3
            )

        # End lava burst
        if (
            self.surge_active
            and self.frame >= self.surge_end_frame
        ):

            self.surge_active = False

            self.next_surge_frame = (
                self.frame + FPS * 12
            )

        # ---------------------------------
        # LAVA SPEED
        # ---------------------------------

        if self.surge_active:

            current_rise = self.lava_rise * 2.5

        else:

            current_rise = self.lava_rise

        self.lava_y -= current_rise

        # Gradually increase normal lava speed
        self.lava_rise = min(
            1.2,
            self.lava_rise + 0.0003
        )

        # ---------------------------------
        # HEIGHT
        # ---------------------------------

        self.score = max(
            0,
            (GROUND_Y - self.player.rect.y) // 10
        )

        self.frame += 1

        # ---------------------------------
        # LAVA COLLISION
        # ---------------------------------

        if self.player.rect.bottom >= self.lava_y:

            self.game_over = True

        # ---------------------------------
        # VICTORY
        # ---------------------------------

        if self.player.rect.top <= self.top_y - 20:

            self.won = True

    def draw(self):

        self.screen.fill(BG)

        # ---------------------------------
        # DRAW PLATFORMS
        # ---------------------------------

        for platform in self.platforms:

            platform.draw(
                self.screen,
                self.cam_y,
                self.frame
            )

        # ---------------------------------
        # DRAW PLAYER
        # ---------------------------------

        self.player.draw(
            self.screen,
            self.cam_y
        )

        # ---------------------------------
        # DRAW LAVA
        # ---------------------------------

        draw_lava(
            self.screen,
            self.lava_y,
            self.cam_y,
            WIDTH,
            HEIGHT,
            self.frame
        )

        # ---------------------------------
        # HEIGHT HUD
        # ---------------------------------

        height_text = self.font.render(
            f"Height: {self.score}m",
            True,
            (220, 200, 180)
        )

        self.screen.blit(
            height_text,
            (8, 8)
        )

        # ---------------------------------
        # DANGER HUD
        # ---------------------------------

        danger_text = self.font.render(
            "LAVA DANGER",
            True,
            (255, 220, 180)
        )

        self.screen.blit(
            danger_text,
            (8, 38)
        )

        meter_x = 8
        meter_y = 64
        meter_width = 180
        meter_height = 18

        # Background of danger meter
        pygame.draw.rect(
            self.screen,
            (70, 70, 70),
            (
                meter_x,
                meter_y,
                meter_width,
                meter_height
            ),
            border_radius=4
        )

        # Calculate danger level
        danger = min(
            1.0,
            self.lava_rise / 1.2
        )

        if self.surge_active:

            danger = min(
                1.0,
                danger + 0.25
            )

        fill_width = int(
            meter_width * danger
        )

        pygame.draw.rect(
            self.screen,
            (230, 70, 40),
            (
                meter_x,
                meter_y,
                fill_width,
                meter_height
            ),
            border_radius=4
        )

        # ---------------------------------
        # LAVA SPEED
        # ---------------------------------

        speed_text = self.font.render(
            f"Speed: {self.lava_rise:.2f}",
            True,
            (220, 200, 180)
        )

        self.screen.blit(
            speed_text,
            (200, 60)
        )

        # ---------------------------------
        # LAVA BURST WARNING
        # ---------------------------------

        if self.surge_active:

            warning = self.big_font.render(
                "LAVA BURST!",
                True,
                (255, 100, 40)
            )

            self.screen.blit(
                warning,
                (
                    WIDTH // 2
                    - warning.get_width() // 2,
                    100
                )
            )

        # ---------------------------------
        # GAME OVER
        # ---------------------------------

        if self.game_over:

            self._msg(
                "LAVA GOT YOU!",
                (220, 80, 40)
            )

        # ---------------------------------
        # VICTORY
        # ---------------------------------

        if self.won:

            self._msg(
                "ESCAPED!",
                (80, 220, 100)
            )

        pygame.display.flip()

    def _msg(self, text, color):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        message = self.big_font.render(
            text,
            True,
            color
        )

        restart = self.font.render(
            "Press R to Play Again",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            message,
            (
                WIDTH // 2
                - message.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            restart,
            (
                WIDTH // 2
                - restart.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()