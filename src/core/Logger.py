
class Logger:
    messages = []
    screen = None

    @classmethod
    def log(cls, message: str) -> None:
        cls.messages.append(message)
        if cls.screen:
            cls.screen.app.call_from_thread(setattr, cls.screen, "display_output", "<br>  \n".join(cls.messages))