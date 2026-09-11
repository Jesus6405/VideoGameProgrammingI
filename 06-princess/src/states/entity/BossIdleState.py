from typing import TypeVar

import pygame

import settings
from src.states.entity.BaseEntityState import BaseEntityState


class BossIdleState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("idle")
        self.fire_timer = 0.0

    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        self.fire_timer += dt

        if self.fire_timer >= settings.BOSS_FIREBALL_INTERVAL:
            self.fire_timer = 0.0
            self.entity.change_state("boss-attack")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
