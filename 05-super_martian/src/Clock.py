"""
ISPPV1 2024
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Clock.
"""


class Clock:
    def __init__(self, time: int) -> None:
        self.time = time
        self.pause = False

    def count_up(self) -> None:
        if self.pause: 
            return 
        self.time += 1

    def count_down(self) -> None:
        if self.pause:
            return 
        self.time = max(0, self.time - 1)

    def __str__(self) -> str:
        return str(self.time)
