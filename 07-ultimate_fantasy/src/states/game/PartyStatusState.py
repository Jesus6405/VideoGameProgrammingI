from typing import Any, Dict, List, Optional, Tuple

from gale.timer import Timer
from gale.state import BaseState
from gale.ui.panel import Panel
from gale.ui.label import Label
from gale.ui.progress_bar import ProgressBar
from gale.ui.cursor import Cursor
from src.gui.theme import BAR_THEME
from src.definitions.entity import DEFAULT_CHARACTER_FRAME
import pygame
import settings

class PartyStatusState(BaseState): 
    def enter(self, play_state: Any): 
        self.play_state = play_state
        self.party = play_state.world.party

        self.mode: str = "ACTION_SELECT"

        self.cursor_right = Cursor(settings.TEXTURES["cursor-right"])

        self.card_width = 184
        self.card_height = 80

        self.header_panel = Panel(3, 20, 368, 16)
        self.header_label = Label(
            settings.VIRTUAL_WIDTH / 2, 
            13, 
            "Party Status", 
            font=settings.FONTS["small"],
            color=pygame.Color(255, 255, 255),
            center=True,
            shadowed=True
        )

        self.footer_panel = Panel(6, 194, 368, 24)
        self.footer_label = Label(
            settings.VIRTUAL_WIDTH / 2,
            206,
            "Arrows: Navigate  |  Enter: Select  |  S: Close",
            font=settings.FONTS["small"],
            color=pygame.Color(230, 230, 230),
            center=True,
            shadowed=True,
        )

        self.card_positions = [(6, 26), (194, 26), (6, 110), (194, 110)]

        self.character_panels: Dict[int, Panel] = {}
        self.hp_bars: Dict[int, ProgressBar] = {}
        self.exp_bars: Dict[int, ProgressBar] = {}
        self.stat_labels: Dict[int, Dict[str, Label]] = {}
        self.action_labels: Dict[int, List[Tuple[Label, bool, pygame.Rect, Dict[str, Any]]]] = {}

        self._build_ui()

        self.selected_char_idx = 2 if 2 in self.party.characters else 0
        self.selected_action_idx = 0
        self.target_char_idx = 0

        self.active_heal_action: Optional[Dict[str, Any]] = None
        self.active_healer_char: Optional[Any] = None

        self._clamp_action_selection()

    def _build_ui(self) -> None:
        for idx in range(4):
            if idx not in self.party.characters:
                continue

            character = self.party.characters[idx]
            x, y = self.card_positions[idx]

            panel = Panel(x, y, self.card_width, self.card_height)
            self.character_panels[idx] = panel

            labels: Dict[str, Label] = {}

            name_color = pygame.Color(255, 255, 255) if not character.dead else pygame.Color(180, 80, 80)
            name_str = character.name if not character.dead else f"{character.name} (KO)"
            labels["name"] = Label(
                x + 28,
                y + 6,
                name_str,
                font=settings.FONTS["small"],
                color=name_color,
                shadowed=True,
            )
            labels["class"] = Label(
                x + 28,
                y + 15,
                character.klass.capitalize(),
                font=settings.FONTS["small"],
                color=pygame.Color(160, 160, 160),
            )

            labels["lvl"] = Label(
                x + 8,
                y + 26,
                f"Lv.{character.level}",
                font=settings.FONTS["small"],
                color=pygame.Color(240, 240, 240),
            )
            labels["mag"] = Label(
                x + 48,
                y + 26,
                f"MAG:{int(character.magic)}",
                font=settings.FONTS["small"],
                color=pygame.Color(140, 200, 255),
            )

            hp_text = f"HP {int(character.current_hp)}/{int(character.hp)}"
            labels["hp"] = Label(
                x + 8,
                y + 36,
                hp_text,
                font=settings.FONTS["small"],
                color=pygame.Color(255, 180, 180),
            )
            self.hp_bars[idx] = ProgressBar(
                x + 8,
                y + 46,
                82,
                4,
                value=character.current_hp,
                max_value=character.hp,
                color=pygame.Color(200, 40, 40),
                theme=BAR_THEME,
            )

            exp_text = f"EXP {int(character.current_exp)}/{int(character.exp_to_level)}"
            labels["exp"] = Label(
                x + 8,
                y + 52,
                exp_text,
                font=settings.FONTS["small"],
                color=pygame.Color(180, 200, 255),
            )
            self.exp_bars[idx] = ProgressBar(
                x + 8,
                y + 62,
                82,
                3,
                value=character.current_exp,
                max_value=character.exp_to_level,
                color=pygame.Color(40, 80, 220),
                theme=BAR_THEME,
            )

            labels["stats"] = Label(
                x + 8,
                y + 68,
                f"ATK:{int(character.attack)}  DEF:{int(character.defense)}",
                font=settings.FONTS["small"],
                color=pygame.Color(180, 180, 180),
            )

            self.stat_labels[idx] = labels

            action_items: List[Tuple[Label, bool, pygame.Rect, Dict[str, Any]]] = []
            labels["act_header"] = Label(
                x + 98,
                y + 6,
                "Actions:",
                font=settings.FONTS["small"],
                color=pygame.Color(200, 200, 160),
                shadowed=True,
            )

            act_y = y + 18
            for act_idx, action in enumerate(character.actions):
                is_healing = action.get("target_type") == "character" or "heal" in action.get("name", "").lower()

                if is_healing:
                    act_color = pygame.Color(120, 255, 150)
                    alpha_val = 255
                else:
                    act_color = pygame.Color(180, 180, 180)
                    alpha_val = 100

                act_label = Label(
                    x + 106,
                    act_y,
                    action["name"],
                    font=settings.FONTS["small"],
                    color=act_color,
                    shadowed=is_healing,
                )

                if not is_healing and hasattr(act_label, "_text_obj"):
                    act_label._text_obj.text.set_alpha(alpha_val)
                    if hasattr(act_label._text_obj, "shadow_text") and act_label._text_obj.shadow_text is not None:
                        act_label._text_obj.shadow_text.set_alpha(alpha_val)

                hit_rect = pygame.Rect(x + 94, act_y - 1, 86, 14)
                action_items.append((act_label, is_healing, hit_rect, action))
                act_y += 16

            self.action_labels[idx] = action_items

    def _clamp_action_selection(self) -> None:
            if self.selected_char_idx not in self.party.characters:
                self.selected_char_idx = min(self.party.characters.keys())

            actions = self.action_labels.get(self.selected_char_idx, [])
            if actions:
                self.selected_action_idx = max(0, min(len(actions) - 1, self.selected_action_idx))
            else:
                self.selected_action_idx = 0

    def _refresh_stats(self, char_idx: Optional[int] = None) -> None:
        indices = [char_idx] if char_idx is not None else list(self.party.characters.keys())
        for idx in indices:
            if idx not in self.party.characters:
                continue
            char = self.party.characters[idx]
            labels = self.stat_labels[idx]
            labels["hp"].set_text(f"HP {int(char.current_hp)}/{int(char.hp)}")

            if char.dead:
                labels["name"].set_text(f"{char.name} (KO)")
            else:
                labels["name"].set_text(char.name)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.mode == "ACTION_SELECT" and input_data.pressed:
            self._handle_action_select_input(input_id)
        elif self.mode == "TARGET_SELECT" and input_data.pressed:
            self._handle_target_select_input(input_id)

    def _handle_action_select_input(self, input_id: str) -> None:
        if input_id in ("quit", "status"):
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            self.state_machine.pop()
            return

        col = self.selected_char_idx % 2
        row = self.selected_char_idx // 2
        actions = self.action_labels.get(self.selected_char_idx, [])

        if input_id == "move_left":
            if col == 1:
                target_idx = row * 2
                if target_idx in self.party.characters:
                    self.selected_char_idx = target_idx
                    self._clamp_action_selection()
                    settings.SOUNDS["blip"].stop()
                    settings.SOUNDS["blip"].play()
        elif input_id == "move_right":
            if col == 0:
                target_idx = row * 2 + 1
                if target_idx in self.party.characters:
                    self.selected_char_idx = target_idx
                    self._clamp_action_selection()
                    settings.SOUNDS["blip"].stop()
                    settings.SOUNDS["blip"].play()
        elif input_id == "move_up":
            if self.selected_action_idx > 0:
                self.selected_action_idx -= 1
                settings.SOUNDS["blip"].stop()
                settings.SOUNDS["blip"].play()
            elif row == 1:
                target_idx = col
                if target_idx in self.party.characters:
                    self.selected_char_idx = target_idx
                    top_actions = self.action_labels.get(target_idx, [])
                    self.selected_action_idx = max(0, len(top_actions) - 1)
                    settings.SOUNDS["blip"].stop()
                    settings.SOUNDS["blip"].play()
        elif input_id == "move_down":
            if self.selected_action_idx < len(actions) - 1:
                self.selected_action_idx += 1
                settings.SOUNDS["blip"].stop()
                settings.SOUNDS["blip"].play()
            elif row == 0:
                target_idx = 2 + col
                if target_idx in self.party.characters:
                    self.selected_char_idx = target_idx
                    self.selected_action_idx = 0
                    settings.SOUNDS["blip"].stop()
                    settings.SOUNDS["blip"].play()
        elif input_id == "enter":
            self._trigger_selected_action()

    def _trigger_selected_action(self) -> None:
        actions = self.action_labels.get(self.selected_char_idx, [])
        if not actions or self.selected_action_idx >= len(actions):
            return

        act_label, is_healing, _, action = actions[self.selected_action_idx]
        character = self.party.characters[self.selected_char_idx]

        if not is_healing:
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            self.footer_label.set_text(f"{action['name']} cannot be used outside of battle!")
            return

        if character.dead:
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            self.footer_label.set_text(f"{character.name} is knocked out and cannot use magic!")
            return

        if action.get("require_target", True):
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            self.mode = "TARGET_SELECT"
            self.active_heal_action = action
            self.active_healer_char = character

            self.target_char_idx = 0
            if self.party.characters[self.target_char_idx].dead:
                self._next_alive_target()

            self.footer_label.set_text("Select target to heal  |  Enter: Confirm  |  S: Cancel")
        else:
            self._execute_global_heal(character, action)

    def _handle_target_select_input(self, input_id: str) -> None:
        if input_id in ("status"):
            # Cancel target selection
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            self.mode = "ACTION_SELECT"
            self.active_heal_action = None
            self.active_healer_char = None
            self.footer_label.set_text("Arrows: Navigate  |  Enter: Select  |  S: Close")
            return

        if input_id in ("move_left", "move_up"):
            self._prev_alive_target()
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
        elif input_id in ("move_right", "move_down"):
            self._next_alive_target()
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
        elif input_id == "enter":
            self._confirm_target_heal()

    def _next_alive_target(self) -> None:
        keys = sorted(self.party.characters.keys())
        n = len(keys)
        current_pos = keys.index(self.target_char_idx) if self.target_char_idx in keys else 0

        for step in range(1, n + 1):
            next_idx = keys[(current_pos + step) % n]
            if not self.party.characters[next_idx].dead:
                self.target_char_idx = next_idx
                return

    def _prev_alive_target(self) -> None:
        keys = sorted(self.party.characters.keys())
        n = len(keys)
        current_pos = keys.index(self.target_char_idx) if self.target_char_idx in keys else 0

        for step in range(1, n + 1):
            prev_idx = keys[(current_pos - step) % n]
            if not self.party.characters[prev_idx].dead:
                self.target_char_idx = prev_idx
                return

    def _confirm_target_heal(self) -> None:
        if self.active_heal_action is None or self.active_healer_char is None:
            self.mode = "ACTION_SELECT"
            return

        target = self.party.characters[self.target_char_idx]
        if target.dead:
            return

        action = self.active_heal_action
        healer = self.active_healer_char

        # Execute healing formula (identical to BattleState)
        amount = action["func"](healer, target, action.get("strength"))

        sound_key = action.get("sound_effect", "powerup")
        if sound_key in settings.SOUNDS:
            settings.SOUNDS[sound_key].stop()
            settings.SOUNDS[sound_key].play()

        target_bar = self.hp_bars[self.target_char_idx]
        Timer.tween(0.5, [(target_bar, {"value": target.current_hp})])

        self._refresh_stats(self.target_char_idx)
        self.play_state.world.dirty = True

        self.footer_label.set_text(f"{action['name']} restored {amount} HP to {target.name}!")

        self.mode = "ACTION_SELECT"
        self.active_heal_action = None
        self.active_healer_char = None

    def _execute_global_heal(self, healer: Any, action: Dict[str, Any]) -> None:
        alive_targets = [c for c in self.party.characters.values() if not c.dead]
        if not alive_targets:
            return

        # Execute global healing formula (identical to BattleState)
        amount = action["func"](healer, alive_targets, action.get("strength"))

        sound_key = action.get("sound_effect", "powerup")
        if sound_key in settings.SOUNDS:
            settings.SOUNDS[sound_key].stop()
            settings.SOUNDS[sound_key].play()

        # Tween all alive targets' HP progress bars
        tween_targets = [
            (self.hp_bars[idx], {"value": self.party.characters[idx].current_hp})
            for idx, c in self.party.characters.items()
            if not c.dead
        ]
        Timer.tween(0.5, tween_targets)

        self._refresh_stats()
        self.play_state.world.dirty = True

        self.footer_label.set_text(f"{action['name']} restored {amount} HP to each member!")

    def update(self, dt: float) -> None:
        for bar in self.hp_bars.values():
            bar.update(dt)
        for bar in self.exp_bars.values():
            bar.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        # Semi-transparent dark backdrop over the paused overworld
        backdrop = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        backdrop.fill((0, 0, 0))
        backdrop.set_alpha(180)
        surface.blit(backdrop, (0, 0))

        # Render Header Panel
        self.header_panel.render(surface)
        self.header_label.render(surface)

        # Render Character Panels
        for idx in range(4):
            if idx not in self.party.characters:
                continue

            character = self.party.characters[idx]
            panel = self.character_panels[idx]
            panel.render(surface)

            # Draw Character Sprite portrait
            char_x, char_y = self.card_positions[idx]
            sprite_x = char_x + 8
            sprite_y = char_y + 6
            surface.blit(
                settings.TEXTURES[character.texture],
                (sprite_x, sprite_y),
                settings.frame(character.texture, DEFAULT_CHARACTER_FRAME),
            )

            # Render stat labels
            labels = self.stat_labels[idx]
            for label in labels.values():
                label.render(surface)

            # Render progress bars
            self.hp_bars[idx].render(surface)
            self.exp_bars[idx].render(surface)

            # Render action labels
            actions = self.action_labels[idx]
            for act_label, _, _, _ in actions:
                act_label.render(surface)

            # If in ACTION_SELECT mode: render cursor next to selected action
            if self.mode == "ACTION_SELECT" and idx == self.selected_char_idx:
                if actions and 0 <= self.selected_action_idx < len(actions):
                    _, _, hit_rect, _ = actions[self.selected_action_idx]
                    self.cursor_right.render(
                        surface, (hit_rect.x + 4, hit_rect.centery)
                    )

            # If in TARGET_SELECT mode: render cursor over target card
            if self.mode == "TARGET_SELECT" and idx == self.target_char_idx:
                self.cursor_right.render(
                    surface, (char_x + 2, char_y + 14)
                )

        # Render Footer Panel
        self.footer_panel.render(surface)
        self.footer_label.render(surface)


