import shutil
DISPLAY_WIDTH = shutil.get_terminal_size().columns
if DISPLAY_WIDTH > 50:
    DISPLAY_WIDTH = 50


def print_title(title):
    print()
    print(f"{f'[{title}]':=^{DISPLAY_WIDTH}}")
