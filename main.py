"""
Vampire Savior Pushblock Trainer — Main Application
====================================================
Simulates the pushblock input mechanic from Vampire Savior.
Connects to a USB controller, lets the user map 6 attack buttons,
then tracks button presses within a 14-frame window to determine
pushblock success/failure.

Usage:
    python main.py

Controls:
    R       - Remap controller buttons
    C       - Clear session statistics
    Space   - Dismiss result screen
    Esc / Q - Quit
"""

import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from input_manager import InputManager
from pushblock_engine import PushblockEngine
from button_mapper import ButtonMapper
from ui_renderer import UIRenderer


class PushblockTrainer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vampire Savior — Pushblock Trainer")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.input_manager = InputManager()
        self.engine = PushblockEngine()
        self.ui = UIRenderer(self.screen)
        self.mapper = ButtonMapper(self.screen, self.input_manager)

        self.running = True

    def run(self):
        """Main application loop."""
        # If no controller, show warning
        if not self.input_manager.is_connected():
            self._wait_for_controller()
            if not self.running:
                self._quit()
                return

        # If not mapped, run mapping
        if not self.input_manager.is_fully_mapped():
            success = self.mapper.run_mapping()
            if not success:
                self._quit()
                return

        # Main loop
        while self.running:
            self._handle_events()
            self.engine.tick()
            self.ui.draw_main(self.engine, self.input_manager)
            pygame.display.flip()
            self.clock.tick(FPS)

        self._quit()

    def _handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

            if event.type == pygame.JOYBUTTONDOWN:
                self._handle_joystick_button(event)

            # Handle joystick hotplug
            if event.type == pygame.JOYDEVICEADDED:
                self.input_manager.refresh_joystick()
            if event.type == pygame.JOYDEVICEREMOVED:
                self.input_manager.refresh_joystick()

    def _handle_keydown(self, event):
        """Handle keyboard shortcuts."""
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False

        elif event.key == pygame.K_r:
            # Remap buttons
            if self.input_manager.is_connected():
                success = self.mapper.run_mapping()
                if not success:
                    pass  # User cancelled, keep old mapping
                # Reset engine state
                self.engine = PushblockEngine()

        elif event.key == pygame.K_c:
            # Clear stats
            self.engine.clear_history()

        elif event.key == pygame.K_SPACE:
            # Dismiss result
            if self.engine.get_state() == PushblockEngine.STATE_RESULT:
                self.engine.dismiss_result()

    def _handle_joystick_button(self, event):
        """Handle joystick button press."""
        if not self.input_manager.is_fully_mapped():
            return

        game_btn = self.input_manager.get_pressed_game_buttons(event.button)
        if game_btn < 0:
            # Button not mapped to any game button
            # But if in result state, use it to dismiss
            if self.engine.get_state() == PushblockEngine.STATE_RESULT:
                self.engine.dismiss_result()
            return

        state = self.engine.get_state()

        if state == PushblockEngine.STATE_IDLE:
            # Start new attempt
            self.engine.start_attempt(game_btn)

        elif state == PushblockEngine.STATE_ACTIVE:
            # Add button press to current attempt
            self.engine.register_press(game_btn)

        elif state == PushblockEngine.STATE_RESULT:
            # Dismiss result and immediately start new attempt
            self.engine.dismiss_result()
            self.engine.start_attempt(game_btn)

    def _wait_for_controller(self):
        """Show 'no controller' screen until one is connected."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.running = False
                        return
                    if event.key == pygame.K_r:
                        self.input_manager.refresh_joystick()
                        if self.input_manager.is_connected():
                            return
                if event.type == pygame.JOYDEVICEADDED:
                    self.input_manager.refresh_joystick()
                    if self.input_manager.is_connected():
                        return

            self.ui.draw_no_controller()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = PushblockTrainer()
    app.run()