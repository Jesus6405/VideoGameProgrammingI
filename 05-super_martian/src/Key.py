from typing import Any, Callable, Optional

from gale.timer import Timer

import settings
from src import mixins


class Key(mixins.DrawableMixin, mixins.AnimatedMixin, mixins.CollidableMixin):
    def __init__(self, x: float, y: float, on_collect_callback: Optional[Callable[[], None]] = None) -> None:
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.texture_id = "key"
        self.frame_index = 0
        self.flipped = False
        self.active = True
        self.collidable = False  
        self.consumable = False  
        self.is_emerging = False
        self.on_collect_callback = on_collect_callback

        self.animations = {}
        self.current_animation = None
        self.generate_animations(
            {
                "spin": {"frames": [0, 1], "interval": 0.15},
            }
        )
        self.change_animation("spin")

    def spawn_from_block(self, block_x: float, block_y: float) -> None:
        self.x = block_x
        self.y = block_y
        self.active = True
        self.collidable = False
        self.consumable = False
        self.is_emerging = True

        settings.SOUNDS["key_spawn"].stop()
        settings.SOUNDS["key_spawn"].play()

        target_y = block_y - 20.0

        def on_emerge_complete() -> None:
            self.is_emerging = False
            self.collidable = True
            self.consumable = True

        Timer.tween(
            0.6,
            [(self, {"y": target_y})],
            ease_function_name="out_quad",
            on_finish=on_emerge_complete,
        )

    def update(self, dt: float) -> None:
        mixins.AnimatedMixin.update(self, dt)

    def on_consume(self, consumer: Any) -> None:
        if not self.consumable or not self.active:
            return
        self.active = False
        self.collidable = False
        self.consumable = False
        if self.on_collect_callback is not None:
            self.on_collect_callback()
