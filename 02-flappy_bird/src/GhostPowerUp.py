import pygame
import settings


class GhostPowerUp:
    def __init__(self, x: float, y: float, width: int = 16, height: int = 16) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
        self.consumed: bool = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_out_of_game(self) -> bool:
        return self.x < -self.width or self.consumed

    def update(self, dt: float) -> None:
        self.x -= settings.MAIN_SCROLL_SPEED * dt

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["ghost"], self.get_rect())