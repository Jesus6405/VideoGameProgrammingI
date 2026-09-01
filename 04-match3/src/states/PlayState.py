"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        self.is_dragging = False
        self.dragged_tile = None
        self.drag_start_i = -1
        self.drag_start_j = -1
        
        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        if self.active and self.is_dragging and self.dragged_tile:
            if not pygame.mouse.get_pressed()[0]:
                self._handle_drag_release(pygame.mouse.get_pos())
            else:
                mx, my = pygame.mouse.get_pos()
                vx = mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                vy = my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                self.dragged_tile.x = vx - self.board.x - settings.TILE_SIZE // 2 
                self.dragged_tile.y = vy - self.board.y - settings.TILE_SIZE // 2

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface, ignore_tile = self.dragged_tile if self.is_dragging else None)

        if self.is_dragging and self.dragged_tile:
            # Highlight tile slot under mouse cursor
            mx, my = pygame.mouse.get_pos()
            vx = mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            vy = my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            hover_i = (vy - self.board.y) // settings.TILE_SIZE
            hover_j = (vx - self.board.x) // settings.TILE_SIZE
            if (0 <= hover_i < settings.BOARD_HEIGHT and 0 <= hover_j < settings.BOARD_WIDTH):
                hx = hover_j * settings.TILE_SIZE + self.board.x
                hy = hover_i * settings.TILE_SIZE + self.board.y
                surface.blit(self.tile_alpha_surface, (hx, hy))

            # Draw dragged tile floating on top
            self.dragged_tile.render(surface, self.board.x, self.board.y)

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click":
            if input_data.pressed:
                pos_x, pos_y = input_data.position
                pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE

                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    self.is_dragging = True
                    self.dragged_tile = self.board.tiles[i][j]
                    self.drag_start_i = i
                    self.drag_start_j = j
                    self.dragged_tile.x = pos_x - self.board.x - settings.TILE_SIZE // 2
                    self.dragged_tile.y = pos_y - self.board.y - settings.TILE_SIZE // 2
            elif not input_data.pressed or input_data.released:
                self._handle_drag_release(input_data.position)

    def _handle_drag_release(self, mouse_pos: Any) -> None:
        if not self.is_dragging or not self.dragged_tile:
            return

        mx, my = mouse_pos
        vx = mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
        vy = my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT

        target_i = (vy - self.board.y) // settings.TILE_SIZE
        target_j = (vx - self.board.x) // settings.TILE_SIZE

        start_i = self.drag_start_i
        start_j = self.drag_start_j
        tile1 = self.dragged_tile

        self.is_dragging = False
        self.dragged_tile = None

        di = abs(target_i - start_i)
        dj = abs(target_j - start_j)

        if (
            0 <= target_i < settings.BOARD_HEIGHT
            and 0 <= target_j < settings.BOARD_WIDTH
            and di <= 1
            and dj <= 1
            and di != dj
        ):
            tile2 = self.board.tiles[target_i][target_j]
            self.active = False

            target_x1 = target_j * settings.TILE_SIZE
            target_y1 = target_i * settings.TILE_SIZE
            target_x2 = start_j * settings.TILE_SIZE
            target_y2 = start_i * settings.TILE_SIZE

            def arrive():
                (self.board.tiles[start_i][start_j], self.board.tiles[target_i][target_j]) = (self.board.tiles[target_i][target_j], self.board.tiles[start_i][start_j])
                tile1.i, tile1.j, tile2.i, tile2.j = (target_i, target_j, start_i, start_j)
                tile1.x, tile1.y = target_x1, target_y1
                tile2.x, tile2.y = target_x2, target_y2

                matches = self.board.calculate_matches_for([tile1, tile2])

                if matches is None: 
                    settings.SOUNDS["error"].play() 

                    def arrive_back(): 
                        (self.board.tiles[start_i][start_j], self.board.tiles[target_i][target_j]) = (self.board.tiles[target_i][target_j], self.board.tiles[start_i][start_j])
                        tile1.i, tile1.j, tile2.i, tile2.j = (start_i, start_j, target_i, target_j)
                        tile1.x, tile1.y = target_x2, target_y2
                        tile2.x, tile2.y = target_x1, target_y1
                        self.active = True

                    Timer.tween(
                        0.25,
                        [
                            (tile1, {"x": target_x2, "y": target_y2}),
                            (tile2, {"x": target_x1, "y": target_y1}),
                        ],
                        on_finish=arrive_back,
                    )
                else: 
                    settings.SOUNDS["match"].stop()
                    settings.SOUNDS["match"].play()

                    for match in matches:
                        self.score += len(match) * 50

                    self.board.remove_matches()

                    falling_tiles = self.board.get_falling_tiles()

                    Timer.tween(
                        0.25,
                        falling_tiles,
                        on_finish=lambda: self._calculate_matches(
                            [item[0] for item in falling_tiles]
                        ),
                    )

            Timer.tween(
                0.25,
                [
                    (tile1, {"x": target_x1, "y": target_y1}),
                    (tile2, {"x": target_x2, "y": target_y2}),
                ],
                on_finish=arrive,
            )
        else:
            # Snap back tile to original position
            original_x = start_j * settings.TILE_SIZE
            original_y = start_i * settings.TILE_SIZE
            tile1.x = original_x
            tile1.y = original_y

    def _calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            if not self.board.has_valid_moves():
                self.board.recreate_board()
            self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )
