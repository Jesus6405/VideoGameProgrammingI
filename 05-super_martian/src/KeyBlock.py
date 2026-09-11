from typing import Any, Callable, Optional

from gale.timer import Timer

import settings
from src import mixins


class KeyBlock(mixins.DrawableMixin, mixins.CollidableMixin):
    def __init__(self, x: float, y: float, on_spawn_key: Optional[Callable[[float, float], None]] = None) -> None:
        self.x = float(x)
        self.y = float(y)
        self.base_y = float(y)
        self.width = 16
        self.height = 16
        self.texture_id = "key_block"
        self.frame_index = 0
        self.flipped = False
        self.active = True
        self.collidable = True
        self.is_hit = False
        self.is_bumping = False
        self.on_spawn_key = on_spawn_key

    def hit(self) -> None:
        if self.is_hit:
            return

        self.is_hit = True
        self.is_bumping = True

        settings.SOUNDS["block_hit"].stop()
        settings.SOUNDS["block_hit"].play()

        # Spawn key at this block's coordinates
        if self.on_spawn_key is not None:
            self.on_spawn_key(self.x, self.base_y)

        # Bump tween: up 6px then back down
        bump_y = self.base_y - 6.0

        def return_to_base() -> None:
            Timer.tween(
                0.08,
                [(self, {"y": self.base_y})],
                ease_function_name="in_quad",
                on_finish=lambda: setattr(self, "is_bumping", False),
            )

        Timer.tween(
            0.08,
            [(self, {"y": bump_y})],
            ease_function_name="out_quad",
            on_finish=return_to_base,
        )

    def resolve_player_collision(self, player: Any) -> None:
        if not self.active or not self.collidable:
            return

        # Check collision rectangle overlap
        player_rect = player.get_collision_rect()
        block_rect = self.get_collision_rect()

        if not player_rect.colliderect(block_rect):
            return

        # Calculate overlaps
        overlap_left = player_rect.right - block_rect.left
        overlap_right = block_rect.right - player_rect.left
        overlap_top = player_rect.bottom - block_rect.top
        overlap_bottom = block_rect.bottom - player_rect.top

        min_overlap_x = min(overlap_left, overlap_right)
        min_overlap_y = min(overlap_top, overlap_bottom)

        if min_overlap_y < min_overlap_x:
            # Vertical collision
            if player.vy < 0 and player.y > self.y:
                # Player jumped into the underside of the block
                player.y = self.base_y + self.height
                player.vy = 0
                self.hit()
            elif player.vy >= 0 and player.y < self.y:
                # Player landed on top of the block
                player.y = self.base_y - player.height
                player.vy = 0
                player.on_ground = True
        else:
            # Horizontal collision
            if player.x < self.x:
                player.x = self.x - player.width
                player.vx = 0
            else:
                player.x = self.x + self.width
                player.vx = 0
