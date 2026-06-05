"""
Bar informasi global: total leads, total delive, global rate.
"""

import customtkinter as ctk

from .constant import COLORS, FONTS


class RateZonasiInfoBar(ctk.CTkFrame):
    """Bar informasi global: total leads, total delive, global rate."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"], corner_radius=8, **kwargs)
        self._build()

    def _build(self):
        # Grid 3 kolom
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Total Leads
        self._create_metric(0, "Total Leads", "0", COLORS["primary"])
        # Total Delive
        self._create_metric(1, "Total Delive", "0", COLORS["success"])
        # Global Rate
        self._create_metric(2, "Global Rate", "0.0%", COLORS["warning"])

        # Warning label
        self.warning_label = ctk.CTkLabel(
            self,
            text="",
            font=FONTS["small"],
            text_color=COLORS["danger"]
        )
        self.warning_label.grid(row=1, column=0, columnspan=3, sticky="w")

    def _create_metric(self, col, title, value, color):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="nsew")

        ctk.CTkLabel(
            frame,
            text=title,
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack()

        label = ctk.CTkLabel(
            frame,
            text=value,
            font=("Segoe UI", 20, "bold"),
            text_color=color
        )
        label.pack()
        setattr(self, f"metric_{col}", label)

    def update_info(self, total_leads, total_delive, global_rate):
        self.metric_0.configure(text=f"{total_leads:,}")
        self.metric_1.configure(text=f"{total_delive:,}")
        self.metric_2.configure(text=f"{global_rate:.1f}%")

    def update_warning(self, total_raw, total_valid, dropped_details=None):
        self.warning_label.configure(text="")

    def clear(self):
        self.metric_0.configure(text="0")
        self.metric_1.configure(text="0")
        self.metric_2.configure(text="0.0%")
        self.warning_label.configure(text="")