"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

import math
from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        self.target_score = settings.TARGET_SCORES.get(self.level, 50)
        self.key_block_pos = settings.KEY_BLOCK_POSITIONS.get(self.level, (320, 80))
        self.key_block_spawned = enter_params.get("key_block_spawned", False)
        self.level_completed = enter_params.get("level_completed", False)
        self.from_pause_state = enter_params.get("from_pause_state", False)

        # Max radius for circular cartoon transition
        self.max_circle_radius = float(math.hypot(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        self.circle_radius = 0.0

        self.game_level = enter_params.get("game_level")
        if self.game_level is None:
            self.game_level = GameLevel(self.level)
            pygame.mixer.music.load(
                settings.BASE_DIR / "assets" / "sounds" / "music_grassland.ogg"
            )
            pygame.mixer.music.play(loops=-1)

        self.game_level.on_key_collected = self.on_level_complete
        self.tilemap = self.game_level.tilemap
        self.player = enter_params.get("player")
        if self.player is None:
            # Resting exactly on the ground tile's surface (row 9, one tile
            # below the platform's top edge) rather than a few pixels into
            # it, so gale.tilemap's one-way platform collision (which
            # requires the entity to already be at/above the surface) picks
            # it up on the very first frame instead of falling through.
            spawn_y = 9 * self.tilemap.tile_height - 20
            self.player = Player(0, spawn_y, self.game_level)
            self.player.change_state("idle")
        elif not self.from_pause_state:
            # Transfer existing player to this level
            self.player.game_level = self.game_level
            self.player.tilemap = self.game_level.tilemap
            spawn_y = 9 * self.tilemap.tile_height - 20
            self.player.x = 0
            self.player.y = spawn_y
            self.player.vx = 0
            self.player.vy = 0
            self.player.is_dead = False
            self.player.change_state("idle")

        self.camera = enter_params.get("camera")

        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)
        else: 
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)

        self.clock = enter_params.get("clock")

        if self.clock is None:
            self.clock = Clock(30)

            def countdown_timer():
                current_state = self.state_machine.current

                if not isinstance(current_state, PlayState):
                    return

                if current_state.level_completed or current_state.key_block_spawned:
                    return 
                
                current_state.clock.count_down()

                if 0 < current_state.clock.time <= 5:
                    settings.SOUNDS["timer"].play()

                if current_state.clock.time == 0:
                    current_state.player.change_state("dead")

            Timer.every(1, countdown_timer)
        else:
            self.clock.pause = False
            Timer.resume()

        if not self.from_pause_state:
            # Opening cartoon iris-in transition
            Timer.tween(
                0.6,
                [(self, {"circle_radius": self.max_circle_radius})],
                ease_function_name="out_quad",
            )
        else:
            self.circle_radius = self.max_circle_radius

    def on_level_complete(self) -> None:
        if self.level_completed:
            return

        self.level_completed = True

        pygame.mixer.music.stop()
        settings.SOUNDS["win"].stop()
        settings.SOUNDS["win"].play()

        self.player.vx = 0
        self.player.change_state("idle")

        Timer.tween(
            1.2,
            [(self, {"circle_radius": 0.0})],
            ease_function_name="in_quad",
            on_finish=self.finish_level_transition,
        )

    def finish_level_transition(self) -> None:
        Timer.clear()
        if self.level < settings.NUM_LEVELS:
            self.state_machine.change(
                "play",
                level=self.level + 1,
                player=self.player,
            )
        else:
            self.state_machine.change("victory", self.player)

    def update(self, dt: float) -> None:
        if self.player.is_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            Timer.clear()
            self.state_machine.change("game_over", self.player)

        if not self.key_block_spawned and self.player.score >= self.target_score:
            self.key_block_spawned = True
            self.game_level.spawn_key_block(*self.key_block_pos)

        if not self.level_completed:
            self.player.update(dt)

        if self.player.y >= self.tilemap.pixel_height:
            self.player.change_state("dead")

        self.camera.update(dt)
        self.game_level.update(dt)

        if self.game_level.key_block is not None: 
            self.game_level.key_block.resolve_player_collision(self.player)

        if not self.level_completed:
            for creature in self.game_level.creatures:
                if self.player.collides(creature):
                    self.player.change_state("dead")

        if not self.key_block_spawned:
            for item in self.game_level.items:
                if not item.active or not item.collidable:
                    continue
            
                if self.player.collides(item):
                    item.on_collide(self.player)
                    item.on_consume(self.player)

        if (
            self.game_level.key is not None
            and self.game_level.key.active
            and self.game_level.key.collidable
            and not self.level_completed
        ):
            if self.player.collides(self.game_level.key):
                self.game_level.key.on_consume(self.player)

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        render_text(
            surface,
            f"Score: {self.player.score}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        if self.key_block_spawned:
            render_text(
                surface,
                "Goal: KEY READY!",
                settings.FONTS["small"],
                5,
                16,
                (255, 223, 0),
                shadowed=True,
            )
            render_text(
                surface,
                "★ KEY BLOCK UNLOCKED! ★",
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH // 2,
                settings.VIRTUAL_HEIGHT // 3,
                (255, 223, 0),
                center=True,
                shadowed=True,
            )
        else:
            render_text(
                surface,
                f"Goal: {self.target_score} pts",
                settings.FONTS["small"],
                5,
                16,
                (200, 200, 200),
                shadowed=True,
            )

        render_text(
            surface,
            f"Level {self.level}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH // 2,
            5,
            (255, 255, 255),
            shadowed=True,
            center=True,
        )

        render_text(
            surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        # Cartoon Iris Transition (Circle Wipe)
        if self.circle_radius < self.max_circle_radius:
            mask = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            mask.fill((0, 0, 0, 255))

            # Screen position of the player
            player_screen_x = self.player.x - self.camera.x
            player_screen_y = self.player.y - self.camera.y + (self.player.height // 2)

            if self.circle_radius > 0:
                pygame.draw.circle(
                    mask,
                    (0, 0, 0, 0),
                    (int(player_screen_x), int(player_screen_y)),
                    int(self.circle_radius),
                )
            surface.blit(mask, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            Timer.pause()
            self.clock.pause = True
            self.state_machine.change(
                "pause",
                level=self.level,
                camera=self.camera,
                game_level=self.game_level,
                player=self.player,
                clock=self.clock,
                key_block_spawned = self.key_block_spawned,
                level_completed = self.level_completed
            )
        else:
            self.player.on_input(input_id, input_data)
