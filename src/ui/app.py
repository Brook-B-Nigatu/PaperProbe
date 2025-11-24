import os
from textual.app import App

ASCII_LOGO = """
██████╗  █████╗ ██████╗ ███████╗██████╗ 
██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██████╔╝███████║██████╔╝█████╗  ██████╔╝
██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
██║     ██║  ██║██║     ███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
██████╗ ██████╗  ██████╗ ██████╗ ███████╗
██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝
██████╔╝██████╔╝██║   ██║██████╔╝█████╗  
██╔═══╝ ██╔══██╗██║   ██║██╔══██╗██╔══╝  
██║     ██║  ██║╚██████╔╝██████╔╝███████╗
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
"""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(SCRIPT_DIR, "style.tcss")

class PaperProbeApp(App):
    TITLE = "PaperProbe"
    SUB_TITLE = "Find source code for research papers and generate sample scripts"
    BINDINGS = [("ctrl+q", "quit", "Quit"), ("ctrl+d", "toggle_dark", "Toggle Dark Mode")]

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

    async def action_toggle_dark(self) -> None:
        self.theme = ("catppuccin-latte" if self.theme == "catppuccin-mocha" else "catppuccin-mocha")


if __name__ == "__main__":
    PaperProbeApp().run()
