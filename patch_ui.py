import re
from pathlib import Path

NEW_MENU_SELECT = """def menu_select(options: List[str], default_idx: int = 0, title: str = "",
                t: Dict[str, str] = None, allow_quit: bool = True) -> Optional[int]:
    \"\"\"番号選択メニュー。q で終了 (None を返す)。\"\"\"
    if not options:
        return None

    import sys, os
    if sys.stdin.isatty():
        try:
            if os.name == 'nt':
                import msvcrt
                def getch(): return msvcrt.getch()
            else:
                import tty, termios
                def getch():
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)
                        ch = sys.stdin.read(1)
                        if ch == '\\x1b': ch += sys.stdin.read(2)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    return ch

            selected = default_idx
            opts = list(options)
            if allow_quit:
                opts.append(t["menu_select_quit"] if t else "q. Quit")
                
            def draw():
                sys.stdout.write(f"\\r\\033[K\\033[1;35m✨ {title}\\033[0m\\n")
                for i, opt in enumerate(opts):
                    if i == selected:
                        sys.stdout.write(f"\\r\\033[K\\033[1;36m  ▶ {opt}\\033[0m\\n")
                    else:
                        sys.stdout.write(f"\\r\\033[K    {opt}\\n")
                sys.stdout.flush()

            def clear():
                sys.stdout.write(f"\\033[{len(opts)+1}A")
                sys.stdout.flush()

            draw()
            while True:
                ch = getch()
                if ch in (b'\\xe0H', '\\x1b[A', 'k'):
                    clear()
                    selected = (selected - 1) % len(opts)
                    draw()
                elif ch in (b'\\xe0P', '\\x1b[B', 'j'):
                    clear()
                    selected = (selected + 1) % len(opts)
                    draw()
                elif ch in (b'\\r', '\\r', '\\n'):
                    break
                elif ch in (b'q', 'q', '\\x03'):
                    if allow_quit:
                        selected = len(opts) - 1
                        break
                    else:
                        sys.exit(0)
            
            sys.stdout.write("\\n")
            if allow_quit and selected == len(opts) - 1:
                return None
            return selected + 1
        except Exception:
            pass # Fallback

    if title:
        print_divider(thin=True)
        print(f"{Neon.PROMPT}{title}{Neon.RESET}")
    for i, opt in enumerate(options, 1):
        marker = Neon.SUCCESS + "▶ " if (default_idx and i == default_idx) else Neon.INFO + "  "
        print(f"  {marker}{i}. {opt}{Neon.RESET}")
    if allow_quit:
        print(f"  {Neon.WARNING}  q. {t['menu_select_quit'] if t else 'quit'}{Neon.RESET}")
    while True:
        choice = prompt_input("Choice / 選択", "", range_hint=f"1-{len(options)}")
        if allow_quit and choice.lower() == "q":
            return None
        if not choice and default_idx:
            return default_idx
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print_warning("Please enter 1-{0}{1}".format(
            len(options), " or q" if allow_quit else ""))

def settings_menu(project_dir: Path, t: Dict[str, str]):
    import sys, os
    if not sys.stdin.isatty():
        print_error("Interactive settings require a TTY.")
        sys.exit(1)
        
    cfg = load_config(project_dir, t)
    keys = [
        "auto_hook", "auto_ci", "self_update", "auto_tag", 
        "scan_secrets", "warn_secret_files", "scan_history", 
        "check_gitignore_gap", "dry_run"
    ]
    
    if os.name == 'nt':
        import msvcrt
        def getch(): return msvcrt.getch()
    else:
        import tty, termios
        def getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\\x1b': ch += sys.stdin.read(2)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    selected = 0
    checked = set([i for i, k in enumerate(keys) if cfg.get(k, CONFIG_SCHEMA[k].get("default", False) if k in CONFIG_SCHEMA else False)])
    opts = keys + ["Done / 完了して保存"]
    
    def draw():
        sys.stdout.write(f"\\r\\033[K\\033[1;35m✨ Interactive Settings\\033[0m (Space to toggle, Enter to save)\\n")
        for i, opt in enumerate(opts):
            cursor = "▶" if i == selected else " "
            if i == len(opts) - 1:
                sys.stdout.write(f"\\r\\033[K {cursor} \\033[1;32m{opt}\\033[0m\\n")
            else:
                box = "[x]" if i in checked else "[ ]"
                color = "\\033[1;36m" if i == selected else ""
                sys.stdout.write(f"\\r\\033[K {color}{cursor} {box} {opt}\\033[0m\\n")
        sys.stdout.flush()

    def clear():
        sys.stdout.write(f"\\033[{len(opts)+1}A")
        sys.stdout.flush()

    os.system("clear" if os.name == "posix" else "cls")
    draw()
    while True:
        ch = getch()
        if ch in (b'\\xe0H', '\\x1b[A', 'k'):
            clear()
            selected = (selected - 1) % len(opts)
            draw()
        elif ch in (b'\\xe0P', '\\x1b[B', 'j'):
            clear()
            selected = (selected + 1) % len(opts)
            draw()
        elif ch in (b' ', ' '):
            if selected < len(opts) - 1:
                clear()
                if selected in checked: checked.remove(selected)
                else: checked.add(selected)
                draw()
        elif ch in (b'\\r', '\\r', '\\n'):
            break
        elif ch in (b'q', 'q', '\\x03'):
            sys.exit(0)
            
    sys.stdout.write("\\n")
    print_step("Saving settings to global config (~/.config/gitpush.toml)...")
    global_cfg_path = Path.home() / ".config" / "gitpush.toml"
    global_cfg_path.parent.mkdir(parents=True, exist_ok=True)
    
    import toml
    try:
        data = toml.loads(global_cfg_path.read_text(encoding="utf-8")) if global_cfg_path.exists() else {}
    except Exception:
        data = {}
        
    for i, k in enumerate(keys):
        data[k] = (i in checked)
        
    global_cfg_path.write_text(toml.dumps(data), encoding="utf-8")
    print_success("Settings saved successfully!")
    sys.exit(0)
"""

for target in ["linux/safe_git_push.py", "windows/safe_git_push.py"]:
    text = Path(target).read_text(encoding="utf-8")
    
    # regex to find the menu_select function
    old_menu = re.search(r"def menu_select\(.*?print_warning\(\"Please enter 1-\{0\}\{1\}\"\.format\(\n            len\(options\), \" or q\" if allow_quit else \"\"\)\)", text, re.DOTALL)
    if old_menu:
        text = text[:old_menu.start()] + NEW_MENU_SELECT + text[old_menu.end():]
        
    # fix print_help
    if "setting     Interactive settings menu" not in text:
        text = text.replace('print("  update      Update to the latest version")',
                            'print("  update      Update to the latest version")\n    print("  setting     Interactive settings menu")')

    # Add command handling
    if 'is_setting_command = args.command == "setting"' not in text:
        text = text.replace('is_update_command = args.command == "update"',
                            'is_update_command = args.command == "update"\n    is_setting_command = args.command == "setting"')
                            
        text = text.replace('elif non_interactive or is_update_command:',
                            'elif non_interactive or is_update_command or is_setting_command:')
                            
    # Call setting menu
    if 'if is_setting_command:\n        settings_menu' not in text:
        text = text.replace('if is_update_command:\n        self_update',
                            'if is_setting_command:\n        settings_menu(project_dir, t)\n\n    if is_update_command:\n        self_update')

    Path(target).write_text(text, encoding="utf-8")
    print(f"Updated {target}")

