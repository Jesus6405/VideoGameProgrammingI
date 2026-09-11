from typing import Any

import pygame

import settings
from src.Entity import Entity


class Boss(Entity):
    def __init__(self, flipped: bool,*args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.hitpoints = settings.BOSS_HITPOINTS
        self.health = self.hitpoints
        self.sword_immune = True
        self.vulnerable_timer = 0.0
        self.flipped = flipped

    def on_arrow_hit(self) -> None:
        self.hitpoints -= 1
        self.health = self.hitpoints
        self.sword_immune = False
        self.vulnerable_timer = settings.BOSS_VULNERABILITY_DURATION
        self.go_invulnerable(0.2)

        if self.hitpoints <= 0:
            self.dead = True

    def damage(self, dmg: int) -> None:
        if not self.sword_immune:
            self.hitpoints -= dmg
            self.health = self.hitpoints
            self.go_invulnerable(0.2)
            if self.hitpoints <= 0:
                self.dead = True

    def update(self, dt: float) -> None:
        super().update(dt)

        if not self.sword_immune:
            self.vulnerable_timer -= dt
            if self.vulnerable_timer <= 0:
                self.vulnerable_timer = 0.0
                self.sword_immune = True

    def render_sprite(self, surface: pygame.Surface, texture_id: str, frame_index: int) -> None:
        texture = settings.TEXTURES[texture_id]
        frame = settings.frame(texture_id, frame_index)
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.blit(texture, (0, 0), frame)

        if self.invulnerable and self.flash_timer > 0.06:
            self.flash_timer = 0
            image.set_alpha(64)
        elif not self.sword_immune and (int(self.vulnerable_timer * 10) % 2 == 0):
            image.set_alpha(150)

        if self.flipped:
            image = pygame.transform.flip(image, True, False)

        sprite_x = round(self.x - self.offset_x)
        sprite_y = round(self.y - self.offset_y)

        surface.blit(image, (sprite_x, sprite_y))
