"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

import random

import pygame

from gale.input_handler import InputData
from gale.state import BaseState

import settings
from src.rendering import render_table


class PlayState(BaseState):
    def enter(self, pong) -> None:
        self.pong = pong
        self.ai_reaction_timer = 0.0

    def update(self, dt: float) -> None:
        pong = self.pong

        if pong.gamemode > 0:
            self._update_ai_paddle(pong.player2, pong.ball, pong.ball.vx > 0, dt)
            if pong.gamemode == 2:
                self._update_ai_paddle(pong.player1, pong.ball, pong.ball.vx < 0, dt)

        pong.player1.update(dt)
        pong.player2.update(dt)
        pong.ball.update(dt)

        ball_rect = pong.ball.get_rect()

        if ball_rect.left > settings.VIRTUAL_WIDTH:
            self._score(scorer=1)
            return

        if ball_rect.right < 0:
            self._score(scorer=2)
            return

        if ball_rect.top <= 0:
            settings.SOUNDS["wall_hit"].play()
            pong.ball.y = 0
            pong.ball.vy *= -1
        elif ball_rect.bottom >= settings.VIRTUAL_HEIGHT:
            settings.SOUNDS["wall_hit"].play()
            pong.ball.y = settings.VIRTUAL_HEIGHT - pong.ball.height
            pong.ball.vy *= -1
             
        # Refreshed since a wall bounce above may have changed ball.y.
        ball_rect = pong.ball.get_rect()
        player1_rect = pong.player1.get_rect()
        player2_rect = pong.player2.get_rect()

        if ball_rect.colliderect(player1_rect):
            settings.SOUNDS["paddle_hit"].play()
            pong.ball.x = player1_rect.right
            pong.ball.vx *= -1.03
            self._randomize_vy()
        elif ball_rect.colliderect(player2_rect):
            settings.SOUNDS["paddle_hit"].play()
            pong.ball.x = player2_rect.left - pong.ball.width
            pong.ball.vx *= -1.03
            self._randomize_vy()

    def _randomize_vy(self) -> None:
        magnitude = random.randint(10, 149)
        self.pong.ball.vy = -magnitude if self.pong.ball.vy < 0 else magnitude

    def _score(self, scorer: int) -> None:
        pong = self.pong
        settings.SOUNDS["score"].play()

        # Neither ServeState, DoneState, nor TitleState handle p1_up/p1_down/
        # p2_up/p2_down, so if a paddle key is still held when a point is
        # scored, its eventual release event is dropped instead of zeroing
        # vy here — leaving the paddle drifting on its own once play resumes.
        pong.player1.vy = 0
        pong.player2.vy = 0

        if scorer == 1:
            pong.player1_score += 1
            pong.serving_player = 2
        else:
            pong.player2_score += 1
            pong.serving_player = 1

        if pong.player1_score == settings.MAX_POINTS or pong.player2_score == settings.MAX_POINTS:
            pong.winning_player = scorer
            self.state_machine.change("done", pong=pong)
            return

        pong.ball.reset(
            settings.VIRTUAL_WIDTH / 2 - settings.BALL_SIZE / 2,
            settings.VIRTUAL_HEIGHT / 2 - settings.BALL_SIZE / 2,
        )
        self.state_machine.change("serve", pong=pong)

    def _predict_ball_y(self, ball, paddle_x):
        if self.pong.ball.vx == 0: 
            return settings.VIRTUAL_HEIGHT / 2

        time_to_reach = (paddle_x - ball.x) / ball.vx

        if time_to_reach < 0: 
            return settings.VIRTUAL_HEIGHT / 2

        predicted_y = ball.y + ball.vy * time_to_reach

        if predicted_y < 0:
            predicted_y = -predicted_y
        elif predicted_y > settings.VIRTUAL_HEIGHT:
            predicted_y = 2 * settings.VIRTUAL_HEIGHT - predicted_y

        return predicted_y

    def _update_ai_paddle(self, paddle, ball, ball_heading_toward, dt):
        self.ai_reaction_timer += dt

        if self.ai_reaction_timer >= settings.AI_REACTION_INTERVAL:
            self.ai_reaction_timer = 0.0

            if ball_heading_toward:
                predicted_y = self._predict_ball_y(ball, paddle.x)
                error = random.uniform(-settings.AI_ERROR_RANGE, settings.AI_ERROR_RANGE)
                paddle.ai_target_y = predicted_y + error
            else:
                paddle.ai_target_y = settings.VIRTUAL_HEIGHT / 2

        if paddle.ai_target_y < paddle.y:
            paddle.vy = -settings.PADDLE_SPEED
        elif paddle.ai_target_y > paddle.y + paddle.height:
            paddle.vy = settings.PADDLE_SPEED
        else:
            paddle.vy = 0


    def render(self, surface: pygame.Surface) -> None:
        render_table(surface, self.pong)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        pong = self.pong

        if pong.gamemode != 2: 
            if input_id in ("p1_up", "p1_down"):
                if input_data.pressed:
                    pong.player1.vy = (
                        -settings.PADDLE_SPEED if input_id == "p1_up" else settings.PADDLE_SPEED
                    )
                elif input_data.released:
                    sign = -1 if input_id == "p1_up" else 1
                    if pong.player1.vy == sign * settings.PADDLE_SPEED:
                        pong.player1.vy = 0
            elif input_id in ("p2_up", "p2_down") and pong.gamemode == 0:
                if input_data.pressed:
                    pong.player2.vy = (
                        -settings.PADDLE_SPEED if input_id == "p2_up" else settings.PADDLE_SPEED
                    )
                elif input_data.released:
                    sign = -1 if input_id == "p2_up" else 1
                    if pong.player2.vy == sign * settings.PADDLE_SPEED:
                        pong.player2.vy = 0
