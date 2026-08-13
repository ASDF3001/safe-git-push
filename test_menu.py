import sys, os
from typing import Optional

def menu_select_interactive(options: list, default_idx: int = 0, title: str = "", allow_quit: bool = False) -> Optional[int]:
    if os.name == 'nt':
        import msvcrt
        def getch():
            return msvcrt.getch()
    else:
        import tty, termios
        def getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch += sys.stdin.read(2)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    selected = default_idx
    opts = list(options)
    if allow_quit:
        opts.append("q. Quit / 終了")
        
    def draw():
        sys.stdout.write(f"\r\033[K\033[1;35m✨ {title}\033[0m\n")
        for i, opt in enumerate(opts):
            if i == selected:
                sys.stdout.write(f"\r\033[K\033[1;36m  ▶ {opt}\033[0m\n")
            else:
                sys.stdout.write(f"\r\033[K    {opt}\n")
        sys.stdout.flush()

    def clear():
        sys.stdout.write(f"\033[{len(opts)+1}A")
        sys.stdout.flush()

    draw()
    while True:
        ch = getch()
        if ch in (b'\xe0H', '\x1b[A', 'k'): # UP
            clear()
            selected = (selected - 1) % len(opts)
            draw()
        elif ch in (b'\xe0P', '\x1b[B', 'j'): # DOWN
            clear()
            selected = (selected + 1) % len(opts)
            draw()
        elif ch in (b'\r', '\r', '\n'): # ENTER
            break
        elif ch in (b'q', 'q', '\x03'): # Q or Ctrl+C
            if allow_quit:
                selected = len(opts) - 1
                break
            else:
                sys.exit(0)
    
    sys.stdout.write("\n")
    if allow_quit and selected == len(opts) - 1:
        return None
    return selected + 1

# Non-interactive fallback logic if stdin is not a tty
if not sys.stdin.isatty():
    print("Not a tty, exiting test.")
    sys.exit(0)
