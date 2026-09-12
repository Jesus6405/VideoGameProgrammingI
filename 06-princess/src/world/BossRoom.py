from typing import Any, Callable, List, TypeVar

import pygame

import settings
from src.Boss import Boss
from src.definitions.entity import ENTITY_DEFS
from src.Fireball import Fireball
from src.states.entity.BossAttackState import BossAttackState
from src.states.entity.BossIdleState import BossIdleState
from src.world.Doorway import Doorway
from src.world.Room import Room


class BossRoom(Room):
    """
    A special dungeon room containing only the boss. The single entry
    door locks upon arrival and reopens once the boss is defeated.
    """

    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
        entry_direction: str,
    ) -> None:
        self.entry_direction = entry_direction
        self.boss_defeated = False
        self.fireballs: List[Fireball] = []

        super().__init__(player, on_game_over, spawn_chest=False)

        # Only one doorway exists in the room: the entry doorway
        self.doorways = [Doorway(self.entry_direction, False, self)]
        self._doorways_by_direction = {self.entry_direction: self.doorways[0]}

        self.create_boss()

    def _generate_entities(self) -> None:
        """The boss room has no regular enemies."""
        pass

    def _generate_objects(self, spawn_chest: bool = False) -> None:
        """The boss room has no objects."""
        pass

    def create_boss(self) -> None:
        definition = ENTITY_DEFS["boss"]

        boss_width = 64
        boss_height = 68

        # Position the boss on the side opposite to the entry door.
        if self.entry_direction == "bottom":
            bx = settings.VIRTUAL_WIDTH / 2 - boss_width / 2
            by = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE + 4
        elif self.entry_direction == "top":
            bx = settings.VIRTUAL_WIDTH / 2 - boss_width / 2
            by = (settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - settings.TILE_SIZE - boss_height - 4)
        elif self.entry_direction == "left":
            bx = (settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - settings.TILE_SIZE - boss_width - 4)
            by = settings.VIRTUAL_HEIGHT / 2 - boss_height / 2
        else: 
            bx = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE + 4
            by = settings.VIRTUAL_HEIGHT / 2 - boss_height / 2

        self.boss = Boss(
            self.entry_direction == "right",  # flipped if entering from the right
            x=bx,
            y=by,
            width=boss_width,
            height=boss_height,
            walk_speed=definition.get("walk_speed", 0),
            health=settings.BOSS_HITPOINTS,
            animation_defs=definition["animations"],
            states={},
        )

        room_ref = self

        self.boss.state_machine.states = {
            "boss-idle": lambda sm: BossIdleState(self.boss, sm),
            "boss-attack": lambda sm: BossAttackState(self.boss, sm, room_ref),
        }
        self.boss.change_state("boss-idle")

        self.entities.append(self.boss)

    def update(self, dt: float) -> None:
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self.player.update(dt)

        if not self.boss.dead:
            self.boss.process_ai(self, dt)
            self.boss.update(dt)

            if (self.player.collides(self.boss) and not self.player.invulnerable):
                settings.SOUNDS["hit-player"].play()
                self.player.damage(2)
                self.player.go_invulnerable(1.5)

                if self.player.health <= 0:
                    self.on_game_over()

        if self.boss.dead and not self.boss_defeated:
            self.boss_defeated = True
            for doorway in self.doorways:
                doorway.open = True
            settings.SOUNDS["door"].play()

        # Remove dead boss from entity list.
        self.entities = [e for e in self.entities if not e.dead]

        for projectile in list(self.projectiles):
            projectile.update(dt)

            if not projectile.dead and not self.boss.dead and projectile.collides(self.boss):
                self.boss.on_arrow_hit()
                settings.SOUNDS["hit-enemy"].play()
                projectile.dead = True

            if projectile.dead:
                self.projectiles.remove(projectile)

        for fireball in list(self.fireballs):
            fireball.update(dt)

            if not fireball.dead and fireball.collides(self.player):
                fireball.dead = True
                self.player.health = 0
                settings.SOUNDS["hit-player"].play()
                self.on_game_over()

            if fireball.dead:
                self.fireballs.remove(fireball)

        for obj in list(self.objects):
            obj.update(dt)

            if self.player.collides(obj):
                obj.on_collide()

                if obj.solid and not obj.taken:
                    self._push_player_out_of(obj)

                if obj.consumable:
                    obj.on_consume(self.player, obj)
                    self.objects.remove(obj)

    def render(self, surface: pygame.Surface, camera_offset_x: float = 0, camera_offset_y: float = 0) -> None:
        super().render(surface, camera_offset_x, camera_offset_y)

        offset_x = self.adjacent_offset_x + camera_offset_x
        offset_y = self.adjacent_offset_y + camera_offset_y

        for fireball in self.fireballs:
            fireball.render(surface, offset_x, offset_y)
