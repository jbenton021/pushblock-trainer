"""
Handles joystick detection, button mapping persistence, and raw input reading.
"""

import json
import os
import pygame
from config import BUTTON_NAMES, BUTTON_SHORT, MAPPING_FILE


class InputManager:
    def __init__(self):
        pygame.joystick.init()
        self.joystick = None
        self.button_mapping = {}  # {game_button_index: joystick_button_id}
        self.detect_joystick()
        self.load_mapping()

    def detect_joystick(self):
        """Detect and initialize the first available joystick."""
        count = pygame.joystick.get_count()
        if count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Joystick detected: {self.joystick.get_name()}")
            print(f"  Buttons: {self.joystick.get_numbuttons()}")
            print(f"  Axes: {self.joystick.get_numaxes()}")
            print(f"  Hats: {self.joystick.get_numhats()}")
        else:
            print("No joystick detected.")
            self.joystick = None

    def refresh_joystick(self):
        """Re-scan for joysticks."""
        pygame.joystick.quit()
        pygame.joystick.init()
        self.detect_joystick()

    def is_connected(self):
        return self.joystick is not None

    def get_joystick_name(self):
        if self.joystick:
            return self.joystick.get_name()
        return "No controller detected"

    def get_num_buttons(self):
        if self.joystick:
            return self.joystick.get_numbuttons()
        return 0

    def save_mapping(self):
        """Save button mapping to JSON file."""
        data = {
            "joystick_name": self.get_joystick_name(),
            "mapping": {str(k): v for k, v in self.button_mapping.items()},
        }
        try:
            with open(MAPPING_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Mapping saved to {MAPPING_FILE}")
        except IOError as e:
            print(f"Error saving mapping: {e}")

    def load_mapping(self):
        """Load button mapping from JSON file if it exists."""
        if not os.path.exists(MAPPING_FILE):
            return False
        try:
            with open(MAPPING_FILE, "r") as f:
                data = json.load(f)
            self.button_mapping = {int(k): v for k, v in data["mapping"].items()}
            print(f"Loaded mapping from {MAPPING_FILE}")
            # Validate mapping has all 6 buttons
            if len(self.button_mapping) == 6 and all(
                i in self.button_mapping for i in range(6)
            ):
                return True
            else:
                print("Incomplete mapping found, will need re-mapping.")
                self.button_mapping = {}
                return False
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading mapping: {e}")
            return False

    def is_fully_mapped(self):
        """Check if all 6 game buttons are mapped."""
        return len(self.button_mapping) == 6 and all(
            i in self.button_mapping for i in range(6)
        )

    def get_mapping_display(self):
        """Return a list of strings showing current mappings."""
        lines = []
        for i in range(6):
            if i in self.button_mapping:
                lines.append(f"{BUTTON_NAMES[i]}: Joy Button {self.button_mapping[i]}")
            else:
                lines.append(f"{BUTTON_NAMES[i]}: [NOT MAPPED]")
        return lines

    def get_pressed_game_buttons(self, joystick_button_id):
        """
        Given a raw joystick button ID, return the game button index (0-5)
        or -1 if not mapped.
        """
        for game_btn, joy_btn in self.button_mapping.items():
            if joy_btn == joystick_button_id:
                return game_btn
        return -1

    def get_all_currently_pressed(self):
        """
        Return a set of game button indices currently held down.
        """
        pressed = set()
        if not self.joystick:
            return pressed
        for game_btn, joy_btn in self.button_mapping.items():
            try:
                if self.joystick.get_button(joy_btn):
                    pressed.add(game_btn)
            except pygame.error:
                pass
        return pressed

    def get_reverse_mapping(self, game_button_index):
        """Get the joystick button mapped to a game button."""
        return self.button_mapping.get(game_button_index, None)