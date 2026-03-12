"""
Interactive button mapping screen.
Walks the user through pressing each of the 6 attack buttons on their controller.
"""

import pygame
from config import (
    BUTTON_NAMES,
    BUTTON_SHORT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_BUTTON_INACTIVE,
    FPS,
)


class ButtonMapper:
    def __init__(self, screen, input_manager):
        self.screen = screen
        self.input_manager = input_manager
        self.font_large = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_medium = pygame.font.SysFont("Consolas", 24)
        self.font_small = pygame.font.SysFont("Consolas", 18)

    def run_mapping(self):
        """
        Interactive mapping flow. Returns True if mapping completed, False if cancelled.
        """
        clock = pygame.time.Clock()
        current_button = 0  # Which of the 6 buttons we're mapping (0-5)
        temp_mapping = {}
        used_joy_buttons = set()
        wait_for_release = False  # Debounce: wait for button release before next

        while current_button < 6:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.key == pygame.K_BACKSPACE and current_button > 0:
                        # Go back one step
                        current_button -= 1
                        removed_joy_btn = temp_mapping.pop(current_button, None)
                        if removed_joy_btn is not None:
                            used_joy_buttons.discard(removed_joy_btn)
                        wait_for_release = False

                if event.type == pygame.JOYBUTTONDOWN and not wait_for_release:
                    joy_btn = event.button
                    if joy_btn not in used_joy_buttons:
                        temp_mapping[current_button] = joy_btn
                        used_joy_buttons.add(joy_btn)
                        current_button += 1
                        wait_for_release = True

                if event.type == pygame.JOYBUTTONUP:
                    wait_for_release = False

            # Draw
            self.screen.fill(COLOR_BG)
            self._draw_mapping_screen(current_button, temp_mapping)
            pygame.display.flip()
            clock.tick(FPS)

        # Mapping complete
        self.input_manager.button_mapping = temp_mapping
        self.input_manager.save_mapping()

        # Show confirmation
        self._show_confirmation(temp_mapping)
        return True

    def _draw_mapping_screen(self, current_button, temp_mapping):
        """Draw the mapping UI."""
        # Title
        title = self.font_large.render("BUTTON MAPPING", True, COLOR_ACCENT)
        self.screen.blit(
            title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30)
        )

        # Controller name
        name = self.font_small.render(
            f"Controller: {self.input_manager.get_joystick_name()}", True, COLOR_TEXT_DIM
        )
        self.screen.blit(name, (SCREEN_WIDTH // 2 - name.get_width() // 2, 75))

        # Instructions
        if current_button < 6:
            inst = self.font_medium.render(
                f"Press the button for: {BUTTON_NAMES[current_button]}",
                True,
                COLOR_WARNING,
            )
        else:
            inst = self.font_medium.render("Mapping complete!", True, COLOR_SUCCESS)
        self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 120))

        # Visual button layout (2 rows of 3, like an arcade layout)
        #   LP  MP  HP
        #   LK  MK  HK
        start_x = SCREEN_WIDTH // 2 - 200
        start_y = 200
        btn_w, btn_h = 120, 80
        gap = 15

        for i in range(6):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_w + gap)
            y = start_y + row * (btn_h + gap)

            if i < current_button:
                # Already mapped
                color = COLOR_SUCCESS
            elif i == current_button:
                # Currently mapping — pulse effect
                pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500.0
                r = int(100 + 155 * pulse)
                color = (r, 160, 60)
            else:
                color = COLOR_BUTTON_INACTIVE

            pygame.draw.rect(self.screen, color, (x, y, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(
                self.screen, COLOR_TEXT, (x, y, btn_w, btn_h), 2, border_radius=8
            )

            label = self.font_medium.render(BUTTON_SHORT[i], True, COLOR_TEXT)
            self.screen.blit(
                label,
                (x + btn_w // 2 - label.get_width() // 2, y + 10),
            )

            if i in temp_mapping:
                sublabel = self.font_small.render(
                    f"Btn {temp_mapping[i]}", True, COLOR_BG
                )
                self.screen.blit(
                    sublabel,
                    (x + btn_w // 2 - sublabel.get_width() // 2, y + 45),
                )

        # Help text
        help1 = self.font_small.render(
            "Backspace = Undo last | Escape = Cancel", True, COLOR_TEXT_DIM
        )
        self.screen.blit(
            help1, (SCREEN_WIDTH // 2 - help1.get_width() // 2, SCREEN_HEIGHT - 60)
        )

    def _show_confirmation(self, mapping):
        """Show mapping confirmation for 2 seconds."""
        clock = pygame.time.Clock()
        frames = 0
        while frames < FPS * 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                    return

            self.screen.fill(COLOR_BG)
            title = self.font_large.render("MAPPING SAVED!", True, COLOR_SUCCESS)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

            y = 130
            for i in range(6):
                txt = self.font_medium.render(
                    f"{BUTTON_NAMES[i]} -> Joy Button {mapping[i]}",
                    True,
                    COLOR_TEXT,
                )
                self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
                y += 40

            hint = self.font_small.render(
                "Press any button to continue...", True, COLOR_TEXT_DIM
            )
            self.screen.blit(
                hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 60)
            )

            pygame.display.flip()
            clock.tick(FPS)
            frames += 1