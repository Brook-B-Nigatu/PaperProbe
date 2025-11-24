import asyncio
import re
import os

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container 
from textual.widgets import Header, Footer, Static, Input, ListView, ListItem
from mock import mock_scan_paper_for_github_links

SAMPLE_URL = "https://github.com/Brook-B-Nigatu/PaperProbe"
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

# ----------------------- Screens -----------------------
class IntroScreen(Screen):
    BINDINGS = [("ctrl+s", "use_sample", "Use sample url"), ("ctrl+q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main"):
            yield Static(ASCII_LOGO, id="logo")
            yield Static("Paste a paper URL or local file path, or a GitHub repo URL.", id="prompt")
            yield Input(placeholder="https://arxiv.org/abs/... or /path/to/paper.pdf or https://github.com/..", id="input")
            yield Static("After scanning, choose a repo from the list.", id="message")
        yield Footer()

    async def action_use_sample(self) -> None:
        inp = self.query_one(Input)
        inp.value = SAMPLE_URL
        self.query_one("#message").update(f"Sample path populated: {SAMPLE_URL}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self.handle_submit()

    async def handle_submit(self) -> None:
        inp = self.query_one(Input)
        value = inp.value.strip()
        if not value:
            self.query_one("#message").update("Please enter a URL or file path.")
            return

        self.query_one("#message").update("Detecting input type...")

        # Detect pdf/paper vs github
        if re.search(r"github\.com", value, re.I):
            # Proceed to analysis screen
            return

        if value.lower().endswith(".pdf") or re.search(r"arxiv|doi|pdf", value, re.I) or value.startswith("/"):
            self.query_one("#message").update("Scanning paper for GitHub links (mock)...")
            
            main = self.query_one("#main")
            if not self.query("#results_list"):
                results_list = ListView(id="results_list")
                results_list.can_focus = True
                await main.mount(results_list)
            
            results_list = self.query_one("#results_list")
            results_list.clear()
            links = await mock_scan_paper_for_github_links(value)
            for idx, L in enumerate(links, start=1):
                label = f"{idx}. {L['url']}"
                if L.get("recommended"):
                    label += " [b][i](RECOMMENDED)[/b][/i]"
                item = ListItem(Static(label), id=f"item-{idx}")
                item.data = L
                await results_list.append(item)

            self.query_one("#message").update("Select a GitHub link (use arrows + Enter).")
            results_list.focus()
            return

        # Unknown input
        self.query_one("#message").update("Input looks unknown; treating as GitHub URL for demo.")
        await asyncio.sleep(0.3)
        fake = value if value.startswith("http") else f"https://github.com/example/{value}"
        # Proceed to analysis screen

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "data") and item.data:
            url = item.data["url"]
            # Proceed to analysis screen

#------------------------ App -----------------------
class PaperProbeApp(App):
    TITLE = "PaperProbe"
    SUB_TITLE = "Find source code for research papers and generate sample scripts"
    BINDINGS = [("ctrl+q", "quit", "Quit"), ("ctrl+d", "toggle_dark", "Toggle Dark Mode")]

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"
        self.push_screen(IntroScreen())

    async def action_toggle_dark(self) -> None:
        self.theme = ("catppuccin-latte" if self.theme == "catppuccin-mocha" else "catppuccin-mocha")


if __name__ == "__main__":
    PaperProbeApp().run()
