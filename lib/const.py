import shutil
DISPLAY_WIDTH = shutil.get_terminal_size().columns
if DISPLAY_WIDTH > 128:
    DISPLAY_WIDTH //= 2
