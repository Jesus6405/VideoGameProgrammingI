from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class FloorShield(PowerUp):
    """
    Power-up that creates a protective floor shield at the bottom of the screen.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.activate_floor_shield(8.0)
        settings.SOUNDS["life"].stop()
        settings.SOUNDS["life"].play()
        self.active = False
