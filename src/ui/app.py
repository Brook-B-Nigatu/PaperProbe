import asyncio
import re
import os

from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container 
from textual.widgets import Header, Footer, Static, Input, ListView, ListItem, RadioSet, RadioButton, Markdown
from .mock import mock_scan_paper_for_github_links, mock_analyze_github

from src.core.task_manager import get_github_links, basic_analysis

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
        self.query_one("#message").update(f"Sample url populated: {SAMPLE_URL}")

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
            self.app.push_screen(AnalysisScreen(url=value))
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
            results_list.loading = True
            self.load_github_links(value, results_list)
            return

        # Unknown input
        self.query_one("#message").update("Input looks unknown; treating as GitHub URL for demo.")
        await asyncio.sleep(0.3)
        fake = value if value.startswith("http") else f"https://github.com/example/{value}"
        self.app.push_screen(AnalysisScreen(url=fake))

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "data") and item.data:
            url = item.data["url"]
            self.app.push_screen(AnalysisScreen(url=url))

    @work
    async def load_github_links(self, value: str, results_list: ListView) -> None:
        # links = await mock_scan_paper_for_github_links(value)
        links = get_github_links(value)
        for idx, L in enumerate(links, start=1):
            label = f"{idx}. {L}"
            if idx == 1:
                label += " [b][i](RECOMMENDED)[/b][/i]"
            item = ListItem(Static(label), id=f"item-{idx}")
            item.data = {"url": L}
            await results_list.append(item)
        
        results_list.loading = False
        self.query_one("#message").update("Select a GitHub link (use arrows + Enter).")
        results_list.focus()

class AnalysisScreen(Screen):
    BINDINGS = [("ctrl+b", "go_back", "Back"), ("ctrl+f", "fullscreen", "View Fullscreen")]

    def __init__(self, url: str, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.current_markdown = None
        self.current_filename = None
        self.current_mode = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main"):
            yield Static(f"Preparing analysis for: {self.url}", id="prompt")
            yield Static("What kind of analysis do you want?", id="analysis_prompt")
            with RadioSet(id="analysis_mode"):
                yield RadioButton("Basic", id="basic")
                yield RadioButton("Detailed", id="detailed")
            yield Markdown("... waiting for project analysis ...", id="result_view")
        yield Footer()

    async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        mode = event.pressed.id
        self.query_one("#analysis_prompt").update(f"Loading {mode} analysis...")
        result_view = self.query_one("#result_view", Markdown)
        result_view.loading = True
        self.load_analysis(mode)

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_fullscreen(self) -> None:
        if self.current_markdown is not None:
            self.app.push_screen(ResultScreen(
                markdown=self.current_markdown,
                filename=self.current_filename,
                mode=self.current_mode
            ))
        else:
            self.query_one("#analysis_prompt").update("Please select an analysis mode first.")

    @work
    async def load_analysis(self, mode: str) -> None:
        result = await mock_analyze_github(self.url, mode)
        
        filename = f"paperprobe_analysis_{mode}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result['markdown'])
        
        result_view = self.query_one("#result_view", Markdown)
        await result_view.update(result['markdown'])
        result_view.loading = False
        self.query_one("#prompt").update(f"{mode.capitalize()} Analysis Results (saved to {filename})")
        self.query_one("#analysis_prompt").update("Analysis complete! Press Ctrl+F for fullscreen view.")
        
        self.current_markdown = result['markdown']
        self.current_filename = filename
        self.current_mode = mode


class ResultScreen(Screen):
    BINDINGS = [("ctrl+b", "go_back", "Back")]

    def __init__(self, markdown: str, filename: str, mode: str, **kwargs):
        super().__init__(**kwargs)
        self.markdown = markdown
        self.filename = filename
        self.mode = mode

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main"):
            yield Static(f"{self.mode.capitalize()} Analysis Results (saved to {self.filename})", id="prompt")
            yield Markdown(self.markdown, id="result_view")
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

#------------------------ App -----------------------
class PaperProbeApp(App):
    CSS_PATH = CSS_PATH
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
