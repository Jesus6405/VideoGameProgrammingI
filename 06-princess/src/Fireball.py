import math
from typing import Any

import pygame

import settings

from gale.animation import Animation


class Fireball:
    def __init__(
        self,
        boss_x: float,
        boss_y: float,
        boss_width: float,
        boss_height: float,
        target_x: float,
        target_y: float,
    ) -> None:
        self.width = 32
        self.height = 32

        self.x = boss_x + boss_width / 2 - self.width / 2
        self.y = boss_y + boss_height / 2 - self.height / 2

        dx = target_x - (self.x + self.width / 2)
        dy = target_y - (self.y + self.height / 2)
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            dist = 1

        self.vx = (dx / dist) * settings.BOSS_FIREBALL_SPEED
        self.vy = (dy / dist) * settings.BOSS_FIREBALL_SPEED

        self.dead = False

        self.animation = Animation([1, 2, 3, 4], 0.05)

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        if self.dead:
            return

        self.animation.update(dt)

        self.x += self.vx * dt
        self.y += self.vy * dt

        left = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        right = (settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - settings.TILE_SIZE)
        top = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
        bottom = (settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - settings.TILE_SIZE)

        if (self.x < left or self.x + self.width > right or self.y < top or self.y + self.height > bottom):
            self.dead = True

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        texture = settings.TEXTURES["fireball"]
        frame_rect = settings.frame("fireball", self.animation.get_current_frame())
        sub = texture.subsurface(frame_rect).copy()
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        rotated = pygame.transform.rotate(sub, angle)
        rot_rect = rotated.get_rect(
            center=(
                round(self.x + self.width / 2 + offset_x),
                round(self.y + self.height / 2 + offset_y),
            )
        )
        surface.blit(rotated, rot_rect)

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())
