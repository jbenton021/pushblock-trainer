"""
Renders the main trainer UI: button display, timer bar, results, history, stats.
"""

import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BUTTON_SHORT,
    BUTTON_NAMES,
    FRAME_WINDOW,
    PUSHBLOCK_PROBABILITY,
    STRENGTH_GROUPS,
    COLOR_BG,
    COLOR_BG_LIGHT,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_FAILURE,
    COLOR_WARNING,
    COLOR_DARKFORCE,
    COLOR_BUTTON_INACTIVE,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_PRESSED,
    COLOR_TIMER_BAR_BG,
    COLOR_TIMER_BAR_FG,
    COLOR_TIMER_BAR_URGENT,
)
from pushblock_engine import PushblockEngine


class UIRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Consolas", 32, bold=True)
        self.font_large = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Consolas", 22)
        self.font_small = pygame.font.SysFont("Consolas", 16)
        self.font_tiny = pygame.font.SysFont("Consolas", 13)

    def draw_main(self, engine: PushblockEngine, input_manager):
        """Draw the complete main screen."""
        self.screen.fill(COLOR_BG)

        self._draw_header(input_manager)
        self._draw_button_layout(engine)
        self._draw_timer_bar(engine)
        self._draw_status(engine)
        self._draw_probability_table(engine)
        self._draw_result(engine)
        self._draw_history(engine)
        self._draw_stats(engine)
        self._draw_footer()

    def _draw_header(self, input_manager):
        title = self.font_title.render(
            "VAMPIRE SAVIOR \u2014 PUSHBLOCK TRAINER", True, COLOR_ACCENT
        )
        self.screen.blit(
            title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10)
        )

        ctrl = self.font_tiny.render(
            f"Controller: {input_manager.get_joystick_name()}",
            True,
            COLOR_TEXT_DIM,
        )
        self.screen.blit(
            ctrl, (SCREEN_WIDTH // 2 - ctrl.get_width() // 2, 48)
        )

    def _draw_button_layout(self, engine: PushblockEngine):
        """Draw the 6-button arcade layout showing press state."""
        active_buttons = (
            engine.get_active_buttons()
            if engine.get_state() != PushblockEngine.STATE_IDLE
            else set()
        )

        # Layout: LP MP HP  (row 0)
        #         LK MK HK  (row 1)
        start_x = SCREEN_WIDTH // 2 - 195
        start_y = 80
        btn_w, btn_h = 120, 60
        gap = 10

        # Highlight dark force pairs: only if they occurred on the same frame
        dark_force_pairs = set()
        if engine.get_state() == PushblockEngine.STATE_ACTIVE:
            df_triggered, df_type = engine.has_dark_force_conflict()
            if df_triggered and df_type is not None:
                for btn_idx in STRENGTH_GROUPS[df_type]:
                    dark_force_pairs.add(btn_idx)

        for i in range(6):
            row = i // 3
            col = i % 3
            x = start_x + col * (btn_w + gap)
            y = start_y + row * (btn_h + gap)

            if i in dark_force_pairs:
                color = COLOR_DARKFORCE
            elif i in active_buttons:
                color = COLOR_BUTTON_PRESSED
            else:
                color = COLOR_BUTTON_INACTIVE

            pygame.draw.rect(
                self.screen, color, (x, y, btn_w, btn_h), border_radius=6
            )
            pygame.draw.rect(
                self.screen,
                COLOR_TEXT_DIM,
                (x, y, btn_w, btn_h),
                1,
                border_radius=6,
            )

            label = self.font_medium.render(BUTTON_SHORT[i], True, COLOR_TEXT)
            self.screen.blit(
                label,
                (
                    x + btn_w // 2 - label.get_width() // 2,
                    y + btn_h // 2 - label.get_height() // 2,
                ),
            )

    def _draw_timer_bar(self, engine: PushblockEngine):
        """Draw the 14-frame timer bar."""
        bar_x = 100
        bar_y = 225
        bar_w = SCREEN_WIDTH - 200
        bar_h = 30

        # Background
        pygame.draw.rect(
            self.screen,
            COLOR_TIMER_BAR_BG,
            (bar_x, bar_y, bar_w, bar_h),
            border_radius=4,
        )

        if engine.get_state() == PushblockEngine.STATE_ACTIVE:
            progress = engine.get_current_frame() / FRAME_WINDOW
            fill_w = int(bar_w * progress)

            color = (
                COLOR_TIMER_BAR_FG if progress < 0.7 else COLOR_TIMER_BAR_URGENT
            )
            if fill_w > 0:
                pygame.draw.rect(
                    self.screen,
                    color,
                    (bar_x, bar_y, fill_w, bar_h),
                    border_radius=4,
                )

            # Frame counter text
            frame_txt = self.font_small.render(
                f"Frame {engine.get_current_frame()}/{FRAME_WINDOW}",
                True,
                COLOR_TEXT,
            )
            self.screen.blit(
                frame_txt,
                (bar_x + bar_w // 2 - frame_txt.get_width() // 2, bar_y + 5),
            )

            # Draw tick marks for each frame that has input
            # Group simultaneous presses into one tick per frame
            presses_by_frame = engine.get_presses_by_frame()
            for frame_num in sorted(presses_by_frame.keys()):
                btns_on_frame = presses_by_frame[frame_num]
                tick_x = bar_x + int((frame_num / FRAME_WINDOW) * bar_w)
                pygame.draw.line(
                    self.screen,
                    COLOR_WARNING,
                    (tick_x, bar_y - 5),
                    (tick_x, bar_y),
                    2,
                )
                # Show all buttons pressed on this frame
                frame_label = "+".join(
                    BUTTON_SHORT[b] for b in sorted(btns_on_frame)
                )
                tick_label = self.font_tiny.render(
                    frame_label, True, COLOR_WARNING
                )
                self.screen.blit(
                    tick_label,
                    (tick_x - tick_label.get_width() // 2, bar_y - 18),
                )
        else:
            idle_txt = self.font_small.render(
                "Press an attack button to start", True, COLOR_TEXT_DIM
            )
            self.screen.blit(
                idle_txt,
                (bar_x + bar_w // 2 - idle_txt.get_width() // 2, bar_y + 5),
            )

        # Border
        pygame.draw.rect(
            self.screen,
            COLOR_TEXT_DIM,
            (bar_x, bar_y, bar_w, bar_h),
            1,
            border_radius=4,
        )

        # Label
        label = self.font_tiny.render(
            "INPUT WINDOW (14 frames / 233ms)", True, COLOR_TEXT_DIM
        )
        self.screen.blit(label, (bar_x, bar_y + bar_h + 4))

    def _draw_status(self, engine: PushblockEngine):
        """Draw current press count and probability during active window."""
        y = 280
        if engine.get_state() == PushblockEngine.STATE_ACTIVE:
            frames_with_input = engine.get_frames_with_input()
            capped = min(frames_with_input, 6)
            prob = PUSHBLOCK_PROBABILITY.get(capped, 0.0)

            count_txt = self.font_medium.render(
                f"Input frames: {frames_with_input}  (effective: {capped}/6)",
                True,
                COLOR_TEXT,
            )
            self.screen.blit(
                count_txt,
                (SCREEN_WIDTH // 2 - count_txt.get_width() // 2, y),
            )

            prob_color = (
                COLOR_SUCCESS
                if prob >= 0.75
                else (COLOR_WARNING if prob > 0 else COLOR_FAILURE)
            )
            prob_txt = self.font_medium.render(
                f"Current probability: {int(prob * 100)}%", True, prob_color
            )
            self.screen.blit(
                prob_txt,
                (SCREEN_WIDTH // 2 - prob_txt.get_width() // 2, y + 28),
            )

            # Dark Force warning (same-frame only)
            df_triggered, df_type = engine.has_dark_force_conflict()
            if df_triggered:
                warn = self.font_medium.render(
                    f"\u26a0 DARK FORCE ({df_type}) DETECTED! (same-frame input)",
                    True,
                    COLOR_DARKFORCE,
                )
                self.screen.blit(
                    warn,
                    (SCREEN_WIDTH // 2 - warn.get_width() // 2, y + 56),
                )

    def _draw_probability_table(self, engine: PushblockEngine):
        """Draw the probability reference table on the left side."""
        x = 20
        y = 340
        header = self.font_small.render("PUSHBLOCK TABLE", True, COLOR_ACCENT)
        self.screen.blit(header, (x, y))
        y += 22

        current_count = (
            min(engine.get_frames_with_input(), 6)
            if engine.get_state() == PushblockEngine.STATE_ACTIVE
            else -1
        )

        for presses in range(1, 7):
            prob = PUSHBLOCK_PROBABILITY[presses]
            highlight = presses == current_count

            color = COLOR_TEXT
            if highlight:
                color = COLOR_WARNING
                pygame.draw.rect(
                    self.screen, (50, 50, 30), (x - 2, y - 1, 220, 18)
                )

            txt = self.font_small.render(
                f"{presses} input{'s' if presses != 1 else ' ':2s} = {int(prob * 100):3d}%",
                True,
                color,
            )
            self.screen.blit(txt, (x, y))
            y += 20

        # Explanation
        y += 5
        note = self.font_tiny.render(
            "1 input = 1 frame with any button(s)", True, COLOR_TEXT_DIM
        )
        self.screen.blit(note, (x, y))
        y += 16

        # Dark Force note
        y += 4
        df_note = self.font_tiny.render(
            "DARK FORCE (same-frame only):", True, COLOR_DARKFORCE
        )
        self.screen.blit(df_note, (x, y))
        y += 16
        for name, btns in STRENGTH_GROUPS.items():
            labels = "+".join(BUTTON_SHORT[b] for b in btns)
            txt = self.font_tiny.render(
                f"  {name}: {labels}", True, COLOR_TEXT_DIM
            )
            self.screen.blit(txt, (x, y))
            y += 16

    def _draw_result(self, engine: PushblockEngine):
        """Draw the result of the last attempt prominently."""
        result = engine.current_result
        if result is None:
            return

        y = 340
        cx = SCREEN_WIDTH // 2 + 40

        # Result box
        box_w = 450
        box_h = 195
        box_x = cx - box_w // 2

        if engine.get_state() == PushblockEngine.STATE_RESULT:
            # Prominent display
            if result.dark_force_triggered:
                border_color = COLOR_DARKFORCE
                title_text = "DARK FORCE!"
                title_color = COLOR_DARKFORCE
            elif result.pushblock_success:
                border_color = COLOR_SUCCESS
                title_text = "PUSHBLOCK!"
                title_color = COLOR_SUCCESS
            else:
                border_color = COLOR_FAILURE
                title_text = "FAILED"
                title_color = COLOR_FAILURE

            pygame.draw.rect(
                self.screen,
                COLOR_BG_LIGHT,
                (box_x, y, box_w, box_h),
                border_radius=8,
            )
            pygame.draw.rect(
                self.screen,
                border_color,
                (box_x, y, box_w, box_h),
                3,
                border_radius=8,
            )

            # Title
            title = self.font_large.render(title_text, True, title_color)
            self.screen.blit(
                title, (cx - title.get_width() // 2, y + 10)
            )

            # Details
            detail_y = y + 50

            # Show frame-by-frame breakdown
            frame_strs = []
            for frame_num in sorted(result.presses_by_frame.keys()):
                btns = result.presses_by_frame[frame_num]
                btn_label = "+".join(BUTTON_SHORT[b] for b in sorted(btns))
                frame_strs.append(f"f{frame_num}:{btn_label}")
            timeline_str = "  ".join(frame_strs)

            details = [
                f"Timeline: {timeline_str}",
                f"Input frames: {result.frames_with_input}  (1 frame = 1 input)",
                f"Probability: {int(result.pushblock_probability * 100)}%",
            ]
            if result.dark_force_triggered:
                details.append(
                    f"Dark Force type: {result.dark_force_type}"
                )
                details.append("(same-strength pair on same frame)")
            elif (
                result.roll_value is not None
                and result.pushblock_probability > 0
            ):
                details.append(
                    f"Roll: {result.roll_value:.3f} "
                    f"(needed < {result.pushblock_probability:.2f})"
                )

            for line in details:
                txt = self.font_small.render(line, True, COLOR_TEXT)
                self.screen.blit(txt, (box_x + 15, detail_y))
                detail_y += 20

            # Dismiss hint
            hint = self.font_tiny.render(
                "Press any button or Space to continue",
                True,
                COLOR_TEXT_DIM,
            )
            self.screen.blit(
                hint, (cx - hint.get_width() // 2, y + box_h + 5)
            )
        else:
            # Show last result dimmed
            if result.dark_force_triggered:
                color = COLOR_DARKFORCE
            elif result.pushblock_success:
                color = COLOR_SUCCESS
            else:
                color = COLOR_FAILURE
            summary = self.font_small.render(
                f"Last: {result.summary()}", True, color
            )
            self.screen.blit(
                summary, (cx - summary.get_width() // 2, y)
            )

    def _draw_history(self, engine: PushblockEngine):
        """Draw recent attempt history."""
        x = 20
        y = 555
        header = self.font_small.render("HISTORY (last 8)", True, COLOR_ACCENT)
        self.screen.blit(header, (x, y))
        y += 22

        recent = engine.history[-8:]
        for i, result in enumerate(reversed(recent)):
            if result.dark_force_triggered:
                icon = "DF"
                color = COLOR_DARKFORCE
            elif result.pushblock_success:
                icon = "OK"
                color = COLOR_SUCCESS
            else:
                icon = "XX"
                color = COLOR_FAILURE

            # Show frame-by-frame summary
            frame_strs = []
            for frame_num in sorted(result.presses_by_frame.keys()):
                btns = result.presses_by_frame[frame_num]
                btn_label = "+".join(BUTTON_SHORT[b] for b in sorted(btns))
                frame_strs.append(btn_label)
            inputs_str = ", ".join(frame_strs)

            line = (
                f"[{icon}] {result.frames_with_input}inp "
                f"{int(result.pushblock_probability * 100):3d}% | {inputs_str}"
            )
            txt = self.font_tiny.render(
                line, True, color if i == 0 else COLOR_TEXT_DIM
            )
            self.screen.blit(txt, (x, y))
            y += 16

    def _draw_stats(self, engine: PushblockEngine):
        """Draw session statistics."""
        stats = engine.get_stats()
        x = SCREEN_WIDTH - 250
        y = 555

        header = self.font_small.render("SESSION STATS", True, COLOR_ACCENT)
        self.screen.blit(header, (x, y))
        y += 24

        lines = [
            (f"Attempts: {stats['total']}", COLOR_TEXT),
            (f"Pushblocks: {stats['successes']}", COLOR_SUCCESS),
            (f"Failures: {stats['failures']}", COLOR_FAILURE),
            (f"Dark Forces: {stats['dark_forces']}", COLOR_DARKFORCE),
            (
                f"Success Rate: {stats['success_rate'] * 100:.1f}%",
                COLOR_SUCCESS
                if stats["success_rate"] >= 0.5
                else COLOR_FAILURE,
            ),
        ]

        for text, color in lines:
            txt = self.font_small.render(text, True, color)
            self.screen.blit(txt, (x, y))
            y += 22

    def _draw_footer(self):
        """Draw bottom help text."""
        y = SCREEN_HEIGHT - 25
        help_text = "R = Remap buttons | C = Clear stats | Q/Esc = Quit"
        txt = self.font_tiny.render(help_text, True, COLOR_TEXT_DIM)
        self.screen.blit(
            txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y)
        )

    def draw_no_controller(self):
        """Draw a 'no controller' warning screen."""
        self.screen.fill(COLOR_BG)
        title = self.font_large.render(
            "NO CONTROLLER DETECTED", True, COLOR_FAILURE
        )
        self.screen.blit(
            title,
            (
                SCREEN_WIDTH // 2 - title.get_width() // 2,
                SCREEN_HEIGHT // 2 - 60,
            ),
        )

        hint1 = self.font_medium.render(
            "Please connect a USB controller.", True, COLOR_TEXT
        )
        self.screen.blit(
            hint1,
            (SCREEN_WIDTH // 2 - hint1.get_width() // 2, SCREEN_HEIGHT // 2),
        )

        hint2 = self.font_small.render(
            "Press R to re-scan or Esc to quit.", True, COLOR_TEXT_DIM
        )
        self.screen.blit(
            hint2,
            (
                SCREEN_WIDTH // 2 - hint2.get_width() // 2,
                SCREEN_HEIGHT // 2 + 40,
            ),
        )