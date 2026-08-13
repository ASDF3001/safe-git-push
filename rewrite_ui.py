import re
import sys
from pathlib import Path

# The new menu_select code
NEW_MENU_SELECT = """def menu_select(options: list, default_idx: int = 0, title: str = "Select an option:", t: Dict[str, str] = None, allow_quit: bool = False) -> Optional[int]:
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
                        if ch == '\x1b': ch += sys.stdin.read(2)
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

    # --- Standard Fallback ---
    print_divider(thin=True)
    print(f"{Neon.TITLE}{title}{Neon.RESET}")
    for i, opt in enumerate(options):
        prefix = "▶ " if i == default_idx else "  "
        print(f"  {prefix}{i + 1}. {opt}")
    if allow_quit:
        print(f"    {t['menu_select_quit'] if t else 'q. Quit'}")
    
    while True:
        try:
            ans = input(f"Choice / 選択 [1-{len(options)}]: ").strip()
            if allow_quit and ans.lower() == "q":
                return None
            if not ans:
                return default_idx + 1
            idx = int(ans)
            if 1 <= idx <= len(options):
                return idx
        except ValueError:
            pass
"""

SETTINGS_MENU = """
def settings_menu(project_dir: Path, t: Dict[str, str]):
    import sys, os
    if not sys.stdin.isatty():
        print_error("Interactive settings require a TTY.")
        sys.exit(1)
        
    cfg = load_config(project_dir, t)
    
    # Bool settings
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
    checked = set([i for i, k in enumerate(keys) if cfg.get(k, CONFIG_SCHEMA[k].get("default", False))])
    
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
    
    # Create ~/.config/gitpush.toml if needed
    global_cfg_path = Path.home() / ".config" / "gitpush.toml"
    global_cfg_path.parent.mkdir(parents=True, exist_ok=True)
    
    # We'll just write it manually (simple toml append/overwrite for bools)
    import toml
    try:
        if global_cfg_path.exists():
            data = toml.loads(global_cfg_path.read_text(encoding="utf-8"))
        else:
            data = {}
    except Exception:
        data = {}
        
    for i, k in enumerate(keys):
        data[k] = (i in checked)
        
    global_cfg_path.write_text(toml.dumps(data), encoding="utf-8")
    print_success("Settings saved successfully!")
    sys.exit(0)
"""

for target in ["linux/safe_git_push.py", "windows/safe_git_push.py"]:
    content = Path(target).read_text(encoding="utf-8")
    
    # 1. Replace menu_select
    old_menu_select_regex = r"def menu_select\(.*?return\s+idx\s+except\s+ValueError:\s+pass"
    content = re.sub(old_menu_select_regex, NEW_MENU_SELECT, content, flags=re.DOTALL)
    
    # 2. Add settings_menu before main()
    if "def settings_menu(" not in content:
        content = content.replace("def main():", SETTINGS_MENU + "\ndef main():")
        
    # 3. Handle 'setting' in main() commands
    if 'is_setting_command = args.command == "setting"' not in content:
        content = content.replace('is_update_command = args.command == "update"', 
                                  'is_update_command = args.command == "update"\n    is_setting_command = args.command == "setting"')
    if 'elif non_interactive or is_update_command:' in content:
        content = content.replace('elif non_interactive or is_update_command:',
                                  'elif non_interactive or is_update_command or is_setting_command:')
    
    if "if is_update_command:" in content and "elif is_setting_command:" not in content:
        content = content.replace('if is_update_command:\n        self_update',
                                  'if is_update_command:\n        self_update')
        # We need to insert setting command handler just after cfg_pre = load_config
        # Wait, if we use replace it might be fragile. 
        # Let's just find `if is_update_command:` and inject it before.
        content = content.replace('if is_update_command:\n',
                                  'if is_setting_command:\n        settings_menu(project_dir, t)\n\n    if is_update_command:\n')
                                  
    # Add setting to help output
    if "setting     Interactive settings menu" not in content:
        content = content.replace('print("  help        Show this help message")',
                                  'print("  setting     Interactive settings menu")\n    print("  help        Show this help message")')

    Path(target).write_text(content, encoding="utf-8")
    print(f"Updated {target}")

