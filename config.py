"""
Configuration constants for the Vampire Savior Pushblock Trainer.
"""

# Timing
FPS = 60
FRAME_WINDOW = 14  # Pushblock input window in frames

# Button names matching Vampire Savior layout
BUTTON_NAMES = [
    "Light Punch (LP)",
    "Medium Punch (MP)",
    "Heavy Punch (HP)",
    "Light Kick (LK)",
    "Medium Kick (MK)",
    "Heavy Kick (HK)",
]

# Short labels for display
BUTTON_SHORT = ["LP", "MP", "HP", "LK", "MK", "HK"]

# Strength groups — pressing two buttons in the same group triggers Dark Force
# LP+LK = Light Dark Force, MP+MK = Medium Dark Force, HP+HK = Heavy Dark Force
STRENGTH_GROUPS = {
    "Light":  [0, 3],  # LP, LK
    "Medium": [1, 4],  # MP, MK
    "Heavy":  [2, 5],  # HP, HK
}

# Pushblock probability table (index = number of distinct presses)
# 0-indexed: index 0 = 0 presses, index 1 = 1 press, etc.
PUSHBLOCK_PROBABILITY = {
    0: 0.0,
    1: 0.0,
    2: 0.0,
    3: 0.25,
    4: 0.50,
    5: 0.75,
    6: 1.0,
}

# Window dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700

# Colors
COLOR_BG = (18, 18, 30)
COLOR_BG_LIGHT = (30, 30, 50)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_DIM = (120, 120, 140)
COLOR_ACCENT = (100, 140, 255)
COLOR_SUCCESS = (50, 220, 100)
COLOR_FAILURE = (220, 60, 60)
COLOR_WARNING = (255, 200, 50)
COLOR_DARKFORCE = (180, 50, 200)
COLOR_BUTTON_INACTIVE = (50, 50, 70)
COLOR_BUTTON_ACTIVE = (80, 100, 200)
COLOR_BUTTON_PRESSED = (100, 200, 130)
COLOR_TIMER_BAR_BG = (40, 40, 60)
COLOR_TIMER_BAR_FG = (100, 160, 255)
COLOR_TIMER_BAR_URGENT = (255, 100, 80)

# Config file for saved mappings
MAPPING_FILE = "button_mapping.json"