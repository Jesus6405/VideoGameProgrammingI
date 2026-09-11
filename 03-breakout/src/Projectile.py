from typing import Any
import pygame


class Projectile:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.vy = -300
        self.active = True

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides(self, another: Any) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y < -self.height:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_collision_rect()
        pygame.draw.rect(surface, (255, 100, 0), rect.inflate(2, 2))
        pygame.draw.rect(surface, (255, 240, 150), rect)