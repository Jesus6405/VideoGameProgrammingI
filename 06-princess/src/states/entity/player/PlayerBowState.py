from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.states.entity.BaseEntityState import BaseEntityState


class PlayerBowState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

        # Render offset for spaced character sprite.
        self.entity.offset_y = 5
        self.entity.offset_x = 0

        self.fired = False

        self.entity.change_animation(f"bow-{self.entity.direction}")

    def enter(self) -> None:
        settings.SOUNDS["sword"].stop()
        settings.SOUNDS["sword"].play()

        # Restart bow animation.
        self.entity.current_animation.reset()

    def update(self, dt: float) -> None:
        self.entity.sword_requested = False
        self.entity.interact_requested = False
        self.entity.fire_requested = False

        # Fire the arrow once the animation finishes.
        if self.entity.current_animation.times_played > 0 and not self.fired:
            self.fired = True
            projectile = self.entity.bow.fire(self.entity)
            self.dungeon.current_room.projectiles.append(projectile)
            self.entity.current_animation.times_played = 0
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
