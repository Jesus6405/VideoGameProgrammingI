"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class World: the scrolling
background/ground, and the log pairs the bird must fly through.
"""

import random
from typing import List

import pygame

from gale.factory import Factory

import settings
import random
from src.LogPair import LogPair
from src.GhostPowerUp import GhostPowerUp


class World:
    def __init__(self, generate_logs: bool = False) -> None:
        self.generate_logs: bool = generate_logs
        self.background_x: float = 0.0
        self.ground_x: float = 0.0
        self.logs: List[LogPair] = []
        self.power_ups: List[GhostPowerUp] = []

        self.logs_spawn_timer: float = 0.0
        self.power_up_spawn_timer: float = 0.0
        self.next_powerup_spawn: float = random.uniform(8.0, 15.0)

        self.last_log_y: float = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.log_pair_factory: Factory = Factory(LogPair)
        self.ghost_power_up_factory: Factory = Factory(GhostPowerUp)

    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs

    def collides(self, rect: pygame.Rect, is_invisible:bool = False) -> bool:
        if rect.bottom >= settings.VIRTUAL_HEIGHT:
            return True

        if is_invisible:
            return False

        return any(log_pair.collides(rect) for log_pair in self.logs)

    def check_powerup_collision(self, bird_rect:pygame.Rect) -> bool:
        for power_up in self.power_ups:
            if not power_up.consumed and power_up.get_rect().colliderect(bird_rect):
                power_up.consumed = True
                return True

        return False

    def update_scored(self, rect: pygame.Rect) -> bool:
        return any(log_pair.update_scored(rect) for log_pair in self.logs)

    def update(self, dt: float) -> None:
        self.background_x += -settings.BACK_SCROLL_SPEED * dt

        if self.background_x <= -settings.BACKGROUND_LOOPING_POINT:
            self.background_x = 0

        self.ground_x += -settings.MAIN_SCROLL_SPEED * dt

        if self.ground_x <= -settings.VIRTUAL_WIDTH:
            self.ground_x = 0

        for log_pair in self.logs:
            log_pair.update(dt)

        for power_up in self.power_ups:
            power_up.update(dt)

        self.logs = [log_pair for log_pair in self.logs if not log_pair.is_out_of_game()]
        self.power_ups = [p for p in self.power_ups if not p.is_out_of_game()]

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["background"], (round(self.background_x), 0))

        for log_pair in self.logs:
            log_pair.render(surface)

        for power_up in self.power_ups:
            power_up.render(surface)

        surface.blit(
            settings.TEXTURES["ground"],
            (round(self.ground_x), settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT),
        )
