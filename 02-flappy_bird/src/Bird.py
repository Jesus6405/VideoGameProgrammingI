"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class Bird.
"""

import pygame

import settings


class Bird:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.vy: float = 0.0
        self.jumping: bool = False
        self.is_invisible: bool = False
        self.invisible_timer: float = 0.0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def jump(self) -> None:
        self.jumping = True

    def activate_invisivility(self, duration: float) -> None:
        self.is_invisible = True
        self.invisible_timer = duration
        pygame.mixer.music.pause()
        settings.SOUNDS["ghost_music"].play()

    def update(self, dt: float) -> None:
        self.vy += settings.GRAVITY * dt

        if self.jumping:
            settings.SOUNDS["jump"].play()
            self.vy = -settings.JUMP_TAKEOFF_SPEED
            self.jumping = False

        self.y += self.vy * dt

        if self.is_invisible:
            self.invisible_timer -= dt
            if self.invisible_timer <= 0:
                self.is_invisible = False
                self.invisible_timer = 0.0
                settings.TEXTURES["bird"].set_alpha(255)
                settings.SOUNDS["ghost_music"].stop()
                pygame.mixer.music.unpause()

    def render(self, surface: pygame.Surface) -> None:
        bird_image = settings.TEXTURES["bird"]

        if self.is_invisible:
            bird_image.set_alpha(128)
    
        surface.blit(bird_image, self.get_rect())
