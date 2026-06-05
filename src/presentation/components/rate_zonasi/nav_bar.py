"""
Navigasi horizontal tombol bulan.
"""

import customtkinter as ctk

from .constant import COLORS, FONTS


class RateZonasiNavBar(ctk.CTkFrame):
    """Navigasi horizontal tombol bulan."""

    def __init__(self, master, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_navigate = on_navigate
        self.buttons = []
        self.active_index = 0

    def create_buttons(self, months_list, label_formatter):
        # Hapus tombol lama
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()

        if not months_list:
            return

        for i, m in enumerate(months_list):
            label = label_formatter(m)
            btn = ctk.CTkButton(
                self,
                text=label,
                width=120,
                height=28,
                font=FONTS["small"],
                corner_radius=6,
                command=lambda idx=i: self._on_click(idx)
            )
            btn.pack(side="left")
            self.buttons.append(btn)

        self.set_active(0)

    def _on_click(self, index):
        self.set_active(index)
        if self.on_navigate:
            self.on_navigate(index)

    def set_active(self, index):
        self.active_index = index
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="white",
                    hover_color=COLORS["primary"]
                )
            else:
                btn.configure(
                    fg_color=COLORS["bg_card"],
                    text_color=COLORS["text"],
                    hover_color=COLORS["border"]
                )

    def clear(self):
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()