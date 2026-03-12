"""
Core pushblock logic: tracks button presses within the 14-frame window,
determines Dark Force conflicts, and resolves pushblock probability.

Mechanics (accurate to Vampire Savior):
- Every button press counts toward the total, including repeated presses
  of the same button. 6 presses of LP = 6 presses = 100% pushblock.
- Dark Force only triggers if two buttons of the same strength
  (LP+LK, MP+MK, HP+HK) are pressed on the EXACT SAME FRAME.
"""

import random
from config import FRAME_WINDOW, PUSHBLOCK_PROBABILITY, STRENGTH_GROUPS, BUTTON_SHORT


class PushblockResult:
    """Stores the result of a single pushblock attempt."""

    def __init__(self):
        self.buttons_pressed = []       # List of game button indices in press order (with repeats)
        self.total_presses = 0          # Total number of presses (including repeats)
        self.dark_force_triggered = False
        self.dark_force_type = None     # "Light", "Medium", or "Heavy"
        self.pushblock_probability = 0.0
        self.pushblock_success = False
        self.roll_value = None          # The random roll (for display)
        self.frames_used = 0            # How many frames the window lasted
        self.press_timeline = []        # List of (frame_number, button_index)

    def summary(self):
        if self.dark_force_triggered:
            return f"DARK FORCE ({self.dark_force_type})!"
        elif self.pushblock_success:
            return (
                f"PUSHBLOCK! ({int(self.pushblock_probability * 100)}% chance, "
                f"rolled {self.roll_value:.2f})"
            )
        else:
            pct = int(self.pushblock_probability * 100)
            if self.total_presses < 3:
                return f"NOT ENOUGH PRESSES ({self.total_presses}/6, {pct}%)"
            else:
                return (
                    f"PUSHBLOCK FAILED ({pct}% chance, "
                    f"rolled {self.roll_value:.2f})"
                )


class PushblockEngine:
    """Manages the state machine for a single pushblock attempt."""

    # States
    STATE_IDLE = "idle"
    STATE_ACTIVE = "active"
    STATE_RESULT = "result"

    def __init__(self):
        self.state = self.STATE_IDLE
        self.frame_counter = 0
        self.buttons_pressed_order = []   # Every press in order (with repeats)
        self.press_timeline = []          # (frame, button_index) for every press
        self.presses_by_frame = {}        # {frame_number: set of button_indices pressed that frame}
        self.current_result = None
        self.result_display_timer = 0
        self.history = []                 # List of PushblockResult

    def start_attempt(self, first_button_index):
        """Begin a new pushblock attempt when first button is pressed."""
        self.state = self.STATE_ACTIVE
        self.frame_counter = 0
        self.buttons_pressed_order = [first_button_index]
        self.press_timeline = [(0, first_button_index)]
        self.presses_by_frame = {0: {first_button_index}}
        self.current_result = None

    def register_press(self, button_index):
        """Register a button press during an active window."""
        if self.state != self.STATE_ACTIVE:
            return
        self.buttons_pressed_order.append(button_index)
        self.press_timeline.append((self.frame_counter, button_index))

        # Track which buttons were pressed on this specific frame
        if self.frame_counter not in self.presses_by_frame:
            self.presses_by_frame[self.frame_counter] = set()
        self.presses_by_frame[self.frame_counter].add(button_index)

    def tick(self):
        """Advance one frame. Call this every frame (60fps)."""
        if self.state == self.STATE_ACTIVE:
            self.frame_counter += 1
            if self.frame_counter >= FRAME_WINDOW:
                self._resolve()
        elif self.state == self.STATE_RESULT:
            self.result_display_timer += 1

    def _check_dark_force(self):
        """
        Check if Dark Force was triggered.
        Dark Force occurs when two buttons of the same strength group
        are pressed on the EXACT SAME FRAME.
        Returns (triggered: bool, strength_name: str or None).
        """
        for frame_num, buttons_on_frame in self.presses_by_frame.items():
            for strength_name, btn_indices in STRENGTH_GROUPS.items():
                if all(b in buttons_on_frame for b in btn_indices):
                    return True, strength_name
        return False, None

    def _resolve(self):
        """Resolve the pushblock attempt at end of window."""
        result = PushblockResult()
        result.buttons_pressed = list(self.buttons_pressed_order)
        result.total_presses = len(self.buttons_pressed_order)
        result.frames_used = self.frame_counter
        result.press_timeline = list(self.press_timeline)

        # Check for Dark Force: same-strength pair on the same frame
        df_triggered, df_type = self._check_dark_force()
        result.dark_force_triggered = df_triggered
        result.dark_force_type = df_type

        if result.dark_force_triggered:
            result.pushblock_probability = 0.0
            result.pushblock_success = False
        else:
            # Total presses (including repeats) determine probability
            count = min(result.total_presses, 6)
            result.pushblock_probability = PUSHBLOCK_PROBABILITY.get(count, 0.0)

            # Roll
            if result.pushblock_probability >= 1.0:
                result.pushblock_success = True
                result.roll_value = 0.0
            elif result.pushblock_probability <= 0.0:
                result.pushblock_success = False
                result.roll_value = 1.0
            else:
                result.roll_value = random.random()
                result.pushblock_success = (
                    result.roll_value < result.pushblock_probability
                )

        self.current_result = result
        self.history.append(result)
        self.state = self.STATE_RESULT
        self.result_display_timer = 0

    def dismiss_result(self):
        """Go back to idle (user acknowledges result)."""
        self.state = self.STATE_IDLE

    def get_state(self):
        return self.state

    def get_current_frame(self):
        return self.frame_counter

    def get_total_presses(self):
        """Return total number of presses (including repeats)."""
        return len(self.buttons_pressed_order)

    def get_active_buttons(self):
        """Return set of distinct button indices pressed in current attempt."""
        return set(self.buttons_pressed_order)

    def get_presses_by_frame(self):
        """Return the frame->buttons mapping for Dark Force visualization."""
        return self.presses_by_frame

    def has_dark_force_conflict(self):
        """
        Check if a Dark Force conflict currently exists in the active window.
        Used for live UI warning during input.
        """
        if self.state != self.STATE_ACTIVE:
            return False, None
        return self._check_dark_force()

    def get_stats(self):
        """Return summary statistics from history."""
        if not self.history:
            return {
                "total": 0,
                "successes": 0,
                "failures": 0,
                "dark_forces": 0,
                "success_rate": 0.0,
            }
        total = len(self.history)
        successes = sum(1 for r in self.history if r.pushblock_success)
        dark_forces = sum(1 for r in self.history if r.dark_force_triggered)
        failures = total - successes - dark_forces
        rate = successes / total if total > 0 else 0.0
        return {
            "total": total,
            "successes": successes,
            "failures": failures,
            "dark_forces": dark_forces,
            "success_rate": rate,
        }

    def clear_history(self):
        self.history.clear()