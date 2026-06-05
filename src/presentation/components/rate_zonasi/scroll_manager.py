"""
Helper untuk mengelola scroll ke card tertentu.
"""


class RateZonasiScrollManager:
    """Helper untuk mengelola scroll ke card tertentu."""

    def __init__(self, container):
        self.container = container

    def scroll_to_table(self, index):
        if 0 <= index < len(self.container.cards):
            card = self.container.cards[index]
            # Trigger scroll event
            card.update_idletasks()