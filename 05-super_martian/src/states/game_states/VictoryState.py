import pygame

from gale.animation import Animation
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings


class VictoryState(BaseState):
    def enter(self, player) -> None:
        self.player = player
        self.martian_animation = Animation(settings.FRAMES["martian"][9:], 0.15)
        self.martian_texture = settings.TEXTURES["martian"]

        pygame.mixer.music.load(
            settings.BASE_DIR / "assets" / "sounds" / "music_intro.ogg"
        )
        pygame.mixer.music.play(loops=-1)

    def exit(self) -> None:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def update(self, dt: float) -> None:
        self.martian_animation.update(dt)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "enter" and input_data.pressed:
            self.state_machine.change("start")

    def render(self, surface: pygame.Surface) -> None:
        # Cheerful victory background
        surface.fill((34, 139, 34))

        render_text(
            surface,
            "VICTORY!",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            12,
            (255, 223, 0),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "All Levels Cleared!",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH // 2,
            30,
            (255, 255, 255),
            center=True,
            shadowed=True,
        )

        # Martian animated in center
        surface.blit(
            self.martian_texture,
            (settings.VIRTUAL_WIDTH // 2 - 8, 48),
            self.martian_animation.get_current_frame(),
        )

        # Coin summary
        y = 74
        for color, amount in self.player.coins_counter.items():
            surface.blit(
                settings.TEXTURES["tiles"],
                (settings.VIRTUAL_WIDTH // 2 - 32, y),
                settings.FRAMES["tiles"][color],
            )
            render_text(
                surface,
                "x",
                settings.FONTS["small"],
                settings.VIRTUAL_WIDTH // 2,
                y + 3,
                (255, 255, 255),
                shadowed=True,
            )
            render_text(
                surface,
                f"{amount}",
                settings.FONTS["small"],
                settings.VIRTUAL_WIDTH // 2 + 16,
                y + 3,
                (255, 255, 255),
                shadowed=True,
            )
            y += 18

        render_text(
            surface,
            f"Final Score: {self.player.score}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH // 2,
            y + 6,
            (255, 255, 0),
            shadowed=True,
            center=True,
        )

        render_text(
            surface,
            "Press Enter to Return to Title",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT - 16,
            (255, 255, 255),
            center=True,
            shadowed=True,
        )
