"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

from typing import Optional

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from src.strategies import NormalStrategy, HardStrategy


class PlayingState(BaseState):
    def enter(self, **params):
        self.gamemode = params.get("gamemode", 0)
        self.strategy = HardStrategy() if self.gamemode == 1 else NormalStrategy()
        self.world = params.get("world") if params.get("world") is not None else World()
        self.world.reset(True)
        self.bird = params.get("bird") if params.get("bird") is not None else Bird(
            settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
            settings.BIRD_WIDTH,
            settings.BIRD_HEIGHT,
        )
        self.score = params.get("score") if params.get("score") is not None else 0

    def update(self, dt: float) -> None:
        self.strategy.update_bird(self.bird, dt)
        self.strategy.update_world(self.world, dt)
        self.world.update(dt)

        if self.gamemode == 1: 
            if self.world.check_powerup_collision(self.bird.get_rect()):
                self.bird.activate_invisivility(5.0)

        if self.world.collides(self.bird.get_rect(), self.bird.is_invisible):
            settings.SOUNDS["explosion"].play()
            settings.SOUNDS["hurt"].play()
            settings.SOUNDS["ghost_music"].stop()
            settings.TEXTURES["bird"].set_alpha(255)
            pygame.mixer.music.unpause()
            self.state_machine.change("count_down", gamemode = self.gamemode)
            return

        if self.world.update_scored(self.bird.get_rect()):
            self.score += 1
            settings.SOUNDS["score"].play()

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
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "pause", world=self.world, bird=self.bird, score=self.score, gamemode = self.gamemode
            )
        else:
            self.strategy.handle_bird_input(self.bird, input_id, input_data)
