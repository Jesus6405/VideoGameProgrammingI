import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World

class PauseState(BaseState):

    def enter(self, **params):
        self.world = params["world"]
        self.bird = params["bird"]
        self.score = params["score"]
        self.gamemode = params["gamemode"]

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed = True,
        )
        render_text(
            surface,
            "PAUSED",
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - 20,
            settings.COLOR_WHITE,
            shadowed = True,
            center = True
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "playing", world=self.world, bird=self.bird, score=self.score, gamemode = self.gamemode
            )
