from typing import Any

import pygame

import settings
from src.GameObject import GameObject
from src.Projectile import Projectile
from gale.factory import Factory


# Arrow game-object definition used by the Factory each time fire() is called.
_ARROW_DEF = {
    "type": "arrow",
    "texture": "arrow",
    "frame": 1,
    "width": 16,
    "height": 8,
    "solid": False,
    "default_state": "default",
    "states": {
        "default": {"frame": 1},
    },
}


class Bow:
    """
    Factory that creates arrow Projectiles.  Each call to fire()
    instantiates a new GameObject (the visible arrow sprite) and wraps
    it in a Projectile that handles movement, wall-collision, and
    enemy-collision.
    """

    def __init__(self) -> None:
        self.arrow_factory: Factory = Factory(GameObject)

    def fire(self, player: Any) -> Projectile:
        """
        Factory method: creates and returns an arrow Projectile flying
        in the direction the player is currently facing.
        """
        direction = player.direction

        # Position the arrow just in front of the player.
        if direction == "left":
            x = player.x - _ARROW_DEF["width"]
            y = player.y + player.height / 2 - _ARROW_DEF["height"] / 2
        elif direction == "right":
            x = player.x + player.width
            y = player.y + player.height / 2 - _ARROW_DEF["height"] / 2
        elif direction == "up":
            x = player.x + player.width / 2 - _ARROW_DEF["height"] / 2
            y = player.y - _ARROW_DEF["width"]
        else:  # down
            x = player.x + player.width / 2 - _ARROW_DEF["height"] / 2
            y = player.y + player.height

        arrow_obj = self.arrow_factory.create(x, y, {"definition" : _ARROW_DEF})

        if direction in ("up", "down"):
            arrow_obj.width = _ARROW_DEF["height"]
            arrow_obj.height = _ARROW_DEF["width"]

        arrow_obj.arrow_direction = direction

        return Projectile(arrow_obj, direction)
