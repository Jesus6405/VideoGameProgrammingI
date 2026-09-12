from typing import TypeVar

import pygame

import settings
from src.Fireball import Fireball
from src.states.entity.BaseEntityState import BaseEntityState


class BossAttackState(BaseEntityState):
    def __init__(self, entity, state_machine, room=None) -> None:
        super().__init__(entity, state_machine)
        self.room = room
        self.fired = False

    def enter(self, room=None) -> None:
        if room is not None:
            self.room = room
        self.entity.change_animation("attack")
        self.entity.current_animation.reset()
        self.fired = False

    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        self.room = room

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.entity.current_animation.times_played > 0 and not self.fired:
            self.fired = True

            if self.room and self.room.player:
                player = self.room.player
                fireball = Fireball(
                    self.entity.x,
                    self.entity.y,
                    self.entity.width,
                    self.entity.height,
                    player.x + player.width / 2,
                    player.y + player.height / 2,
                )
                self.room.fireballs.append(fireball)

            self.entity.current_animation.times_played = 0
            self.entity.change_state("boss-idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
