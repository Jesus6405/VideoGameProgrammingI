from typing import TypeVar

import settings 
from src.powerups.PowerUp import PowerUp

class BallCatch(PowerUp):
    """
    Power-up that enables the paddle to catch the ball on impact.
    """

    def __init__(self, x:int, y:int):
        super().__init__(x, y, 1)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.paddle.sticky = True
        play_state.paddle.sticky_timer = 12.0
        settings.SOUNDS["grow_up"].stop()
        settings.SOUNDS["grow_up"].play()
        self.active = False
