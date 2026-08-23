"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TitleState.
"""

import random

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.rendering import render_table


class TitleState(BaseState):
    def enter(self, pong) -> None:
        self.pong = pong

    def render(self, surface: pygame.Surface) -> None:
        render_table(surface, self.pong)
        render_text(
            surface,
            "Press enter to select a game mode",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True,
        )
        render_text(
            surface, 
            "Player 1 VS Player 2", 
            settings.FONTS["large"], 
            settings.VIRTUAL_WIDTH / 2, 
            settings.VIRTUAL_HEIGHT / 2 + 30, 
            settings.COLOR_YELLOW if self.pong.gamemode == 0 else settings.COLOR_WHITE, 
            center=True
        )
        render_text(
            surface, 
            "Player 1 VS Bot", 
            settings.FONTS["large"], 
            settings.VIRTUAL_WIDTH / 2, 
            settings.VIRTUAL_HEIGHT / 2 + 50, 
            settings.COLOR_YELLOW if self.pong.gamemode == 1 else settings.COLOR_WHITE, 
            center=True
        )
        render_text(
            surface, 
            "Bot VS Bot", 
            settings.FONTS["large"], 
            settings.VIRTUAL_WIDTH / 2, 
            settings.VIRTUAL_HEIGHT / 2 + 70, 
            settings.COLOR_YELLOW if self.pong.gamemode == 2 else settings.COLOR_WHITE, 
            center=True
        )


    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "confirm" and input_data.pressed:
            self.pong.serving_player = random.randint(1, 2)
            self.state_machine.change("serve", pong=self.pong)
        elif input_id == "p2_up" and input_data.pressed:
            if self.pong.gamemode > 0:
                self.pong.gamemode -= 1
        elif input_id == "p2_down" and input_data.pressed:
            if self.pong.gamemode < 2:
                self.pong.gamemode += 1
