"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Paddle.
"""

import pygame

import settings


class Paddle:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 64
        self.height = 16

        # By default, the blue paddle
        self.skin = 0

        # By default, the 64-pixels-width paddle.
        self.size = 1

        self.texture = settings.TEXTURES["spritesheet"]
        self.frames = settings.FRAMES["paddles"]

        # The paddle only move horizontally
        self.vx = 0

        #Power-up
        self.sticky = False
        self.sticky_timer = 0.0
        self.cannons = False
        self.cannons_timer = 0.0

    def resize(self, size: int) -> None:
        self.size = size
        self.width = (self.size + 1) * 32

    def dec_size(self):
        self.resize(max(0, self.size - 1))

    def inc_size(self):
        self.resize(min(3, self.size + 1))

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        next_x = self.x + self.vx * dt

        if self.vx < 0:
            self.x = max(0, next_x)
        else:
            self.x = min(settings.VIRTUAL_WIDTH - self.width, next_x)

        if self.sticky_timer > 0:
            self.sticky_timer -= dt
            if self.sticky_timer <= 0:
                self.sticky = False
        else:
            self.sticky = False

        if self.cannons_timer > 0: 
            self.cannons_timer -= dt
            if self.cannons_timer <= 0:
                self.cannons = False
        else: 
            self.cannons = False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.texture, (self.x, self.y), self.frames[self.skin][self.size])

        if self.sticky:
            pygame.draw.line(
                surface, 
                (50, 255, 120),
                (self.x, self.y),
                (self.x + self.width - 1, self.y),
                2
            )

        if self.cannons:
            pygame.draw.rect(surface, (80, 80, 100), (self.x + 1, self.y - 4, 4, 6))
            pygame.draw.rect(surface, (255, 50, 50), (self.x + 2, self.y - 6, 2, 4))
            pygame.draw.rect(
                surface, (80, 80, 100), (self.x + self.width - 5, self.y - 4, 4, 6)
            )
            pygame.draw.rect(
                surface, (255, 50, 50), (self.x + self.width - 4, self.y - 6, 2, 4)
            )
