class LocalProvider:
    """Simple local provider stub for tests."""

    def generate(self, prompt: str) -> str:
        """Return a canned response echoing the prompt."""
        return f"pong:{prompt}"
