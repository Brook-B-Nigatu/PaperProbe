from textual.app import App
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
