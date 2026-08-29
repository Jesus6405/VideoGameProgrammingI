from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class Cannons(PowerUp):
    """
    Power-up that adds cannon turrets to the paddle.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 3)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.paddle.cannons = True
        play_state.paddle.cannons_timer = 12.0
        settings.SOUNDS["grow_up"].stop()
        settings.SOUNDS["grow_up"].play()
        self.active = False
