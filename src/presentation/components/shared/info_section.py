"""
Komponen: InfoSection
Menampilkan info rangkuman dan warning.
"""

import customtkinter as ctk


class InfoSection:
    """Section untuk info dan warning labels."""

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._setup_ui()

    def _setup_ui(self):
        """Setup info dan warning labels."""
        self.info_label = ctk.CTkLabel(
            self.parent,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self.info_label.pack(anchor="w", padx=15, pady=(0, 3))

        self.warning_label = ctk.CTkLabel(
            self.parent,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        )
        self.warning_label.pack(anchor="w", padx=15, pady=(0, 3))

    def update_info(self, date_info, total_leads, total_paid, paid_ratio):
        """Update info label."""
        self.info_label.configure(
            text=f"Rangkuman data paid dan lead {date_info} || "
                 f"Total lead: {total_leads} - "
                 f"Total paid: {total_paid} - "
                 f"Paid ratio: {paid_ratio:.1f}%"
        )

    def update_warning(self, total_raw, total_leads):
        """Update warning label jika ada data yang tidak masuk master."""
        if total_raw != total_leads:
            diff = total_raw - total_leads
            self.warning_label.configure(
                text=f"[!] Warning: Ada {diff} data daerah yang tidak masuk Master List."
            )
        else:
            self.warning_label.configure(text="")

    def clear(self):
        """Clear both labels."""
        self.info_label.configure(text="")
        self.warning_label.configure(text="")