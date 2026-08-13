import sys
import subprocess

def install_deps():
    try:
        import rich
        import questionary
    except ImportError:
        print("Installing beautiful UI dependencies...")
        cmds = [
            [sys.executable, "-m", "pip", "install", "--user", "rich", "questionary"],
            [sys.executable, "-m", "pip", "install", "--user", "rich", "questionary", "--break-system-packages"]
        ]
        success = False
        for cmd in cmds:
            try:
                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                success = True
                break
            except subprocess.CalledProcessError:
                pass
        if not success:
            print("Failed to install UI dependencies. Please run: pip install rich questionary")
            sys.exit(1)

install_deps()
import rich
from rich.console import Console
from rich.panel import Panel
import questionary

console = Console()
console.print(Panel.fit("[bold magenta]Safe Git Push[/bold magenta]\n[cyan]Welcome to the new UI![/cyan]"))

choices = ["Option A", "Option B", "Option C"]
ans = questionary.select("Select an option:", choices=choices).ask()
console.print(f"You selected: [green]{ans}[/green]")
