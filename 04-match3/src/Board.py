"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()

    def render(self, surface: pygame.Surface, ignore_tile: Optional[Tile] = None) -> None:
        for row in self.tiles:
            for tile in row:
                if tile is not None and tile != ignore_tile:
                    tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        while True: 
            self.tiles = [
                [None for _ in range(settings.BOARD_WIDTH)]
                for _ in range(settings.BOARD_HEIGHT)
            ]
            for i in range(settings.BOARD_HEIGHT):
                for j in range(settings.BOARD_WIDTH):
                    color = random.randint(0, settings.NUM_COLORS - 1)
                    while self._is_match_generated(i, j, color):
                        color = random.randint(0, settings.NUM_COLORS - 1)

                    self.tiles[i][j] = Tile(
                        i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                    )

            if self.has_valid_moves():
                break

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        # If any matched tile is a power-up, expand match with its explosion effect
        if len(self.matches) > 0:
            for match in self.matches:
                extra_tiles = set()
                for tile in match:
                    if tile.power_up is not None:
                        extra_tiles.update(self.get_power_up_explosion(tile))
                for extra in extra_tiles:
                    if extra not in match:
                        match.append(extra)

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self, moved_tiles: Optional[List[Tile]] = None) -> None:
        for match in self.matches:
            if not match:
                continue

            match_color = match[0].color
            same_color_count = sum(1 for t in match if t.color == match_color)

            power_up_type = None
            if same_color_count >= 5:
                power_up_type = "color_bomb"
            elif same_color_count == 4:
                power_up_type = "cross"

            spawn_i, spawn_j = match[0].i, match[0].j
            if power_up_type is not None:
                if moved_tiles:
                    found_moved = False
                    for moved_tile in moved_tiles:
                        if any(t.i == moved_tile.i and t.j == moved_tile.j for t in match):
                            spawn_i, spawn_j = moved_tile.i, moved_tile.j
                            found_moved = True
                            break
                    if not found_moved:
                        spawn_i, spawn_j = match[0].i, match[0].j
                else:
                    spawn_i, spawn_j = match[0].i, match[0].j

                power_up_tile = Tile(
                    spawn_i,
                    spawn_j,
                    match_color,
                    random.randint(0, settings.NUM_VARIETIES - 1),
                    power_up=power_up_type,
                )

                for tile in match:
                    self.tiles[tile.i][tile.j] = None

                self.tiles[spawn_i][spawn_j] = power_up_tile
            else:
                for tile in match:
                    self.tiles[tile.i][tile.j] = None

        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def _check_match_at(self, i: int, j: int) -> bool:
        tile = self.tiles[i][j]
        if tile is None:
            return False
        color = tile.color

        # Check horizontal match
        h_count = 1
        c = j - 1
        while (c >= 0 and self.tiles[i][c] is not None and self.tiles[i][c].color == color):
            h_count += 1
            c -= 1
        c = j + 1
        while (c < settings.BOARD_WIDTH and self.tiles[i][c] is not None and self.tiles[i][c].color == color):
            h_count += 1
            c += 1

        if h_count >= 3:
            return True

        # Check vertical match
        v_count = 1
        r = i - 1
        while (r >= 0 and self.tiles[r][j] is not None and self.tiles[r][j].color == color):
            v_count += 1
            r -= 1
        r = i + 1
        while (r < settings.BOARD_HEIGHT and self.tiles[r][j] is not None and self.tiles[r][j].color == color):
            v_count += 1
            r += 1

        if v_count >= 3:
            return True

        return False

    def _swap_creates_match(self, i1: int, j1: int, i2: int, j2: int) -> bool:
        self.tiles[i1][j1], self.tiles[i2][j2] = self.tiles[i2][j2], self.tiles[i1][j1]
        has_match = self._check_match_at(i1, j1) or self._check_match_at(i2, j2)
        self.tiles[i1][j1], self.tiles[i2][j2] = self.tiles[i2][j2], self.tiles[i1][j1]
        return has_match

    def has_valid_moves(self) -> bool:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.tiles[i][j]
                if tile is not None and tile.power_up is not None:
                    return True

        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                if j + 1 < settings.BOARD_WIDTH:
                    if self._swap_creates_match(i, j, i, j + 1):
                        return True
                if i + 1 < settings.BOARD_HEIGHT:
                    if self._swap_creates_match(i, j, i + 1, j):
                        return True
        return False

    def recreate_board(self) -> None:
        self._initialize_tiles()

    def get_power_up_explosion(self, tile: Tile, processed = None):
        if processed is None:
            processed = set()
        if tile in processed or tile.power_up is None:
            return set()

        processed.add(tile)
        exploded: Set[Tile] = {tile}

        if tile.power_up == "cross":
            # 4-Tile Power-up: explodes horizontal and vertical neighbor tiles
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = tile.i + di, tile.j + dj
                if 0 <= ni < settings.BOARD_HEIGHT and 0 <= nj < settings.BOARD_WIDTH:
                    neighbor = self.tiles[ni][nj]
                    if neighbor is not None:
                        exploded.add(neighbor)
                        if neighbor.power_up is not None and neighbor not in processed:
                            exploded.update(self.get_power_up_explosion(neighbor, processed))

        elif tile.power_up == "color_bomb":
            # 5+ Tile Power-up: explodes all tiles of the same color on the entire board
            for row in self.tiles:
                for other in row:
                    if other is not None and other.color == tile.color:
                        exploded.add(other)
                        if other.power_up is not None and other not in processed:
                            exploded.update(self.get_power_up_explosion(other, processed))

        return exploded
