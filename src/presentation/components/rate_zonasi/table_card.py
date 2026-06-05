"""
Kartu tabel 6 kolom: Provinsi | Total | Delive | %Delive | RTS | %RTS.

Implementasi menggunakan Grid Layout langsung pada container utama
dengan frame wrapper per baris untuk rounded corner terkontrol.
"""

import customtkinter as ctk

from .constant import COLORS, FONTS


class RateZonasiTableCard(ctk.CTkFrame):
    """Kartu tabel 6 kolom: Provinsi | Total | Delive | %Delive | RTS | %RTS."""

    def __init__(self, master, title, data_rows, is_active=False, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"], corner_radius=12, **kwargs)
        self.title = title
        self.data_rows = data_rows
        self.is_active = is_active
        self._build()

    def _build(self):
    # =====================================================
    # HEADER
    # =====================================================
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(fill="x")

        self.title_label = ctk.CTkLabel(
            header,
            text=self.title,
            font=FONTS["header"],
            text_color=(
                COLORS["primary"]
                if self.is_active
                else COLORS["text"]
            )
        )
        self.title_label.pack(anchor="w")

        total_all = sum(
            r["total_raw"]
            for r in self.data_rows
        )

        total_delive = sum(
            r["delive"]
            for r in self.data_rows
        )

        total_rts = sum(
            r["rts"]
            for r in self.data_rows
        )

        delive_pct = (
            total_delive / total_all * 100
            if total_all > 0
            else 0
        )

        rts_pct = (
            total_rts / total_all * 100
            if total_all > 0
            else 0
        )

        summary_text = (
            f"Total: {total_all:,}  |  "
            f"Delive: {total_delive:,} ({delive_pct:.1f}%)  |  "
            f"RTS: {total_rts:,} ({rts_pct:.1f}%)"
        )

        ctk.CTkLabel(
            header,
            text=summary_text,
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w")

        # =====================================================
        # TABLE CONTAINER
        # =====================================================
        table_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_table"],
            corner_radius=12
        )
        table_container.pack(
            fill="both",
            expand=True,
            pady=(8, 0)
        )

        # =====================================================
        # COLUMN CONFIG
        # =====================================================
        table_container.grid_columnconfigure(
            0,
            weight=4,
            minsize=220
        )

        table_container.grid_columnconfigure(
            1,
            weight=1,
            minsize=110
        )

        table_container.grid_columnconfigure(
            2,
            weight=1,
            minsize=110
        )

        table_container.grid_columnconfigure(
            3,
            weight=1,
            minsize=110
        )

        table_container.grid_columnconfigure(
            4,
            weight=1,
            minsize=110
        )

        table_container.grid_columnconfigure(
            5,
            weight=1,
            minsize=110
        )

        headers = [
            "PROVINSI",
            "TOTAL",
            "DELIVE",
            "%DELIVE",
            "RTS",
            "%RTS"
        ]

        # =====================================================
        # HEADER ROW
        # =====================================================
        for col, title in enumerate(headers):

            anchor_pos = (
                "w"
                if col == 0
                else "e"
            )

            padx_val = (
                (16, 8)
                if col == 0
                else (8, 16)
            )

            ctk.CTkLabel(
                table_container,
                text=title,
                fg_color=COLORS["primary"],
                text_color="white",
                height=42,
                corner_radius=0,
                font=FONTS["header"],
                anchor=anchor_pos
            ).grid(
                row=0,
                column=col,
                sticky="nsew",
                padx=0,
                pady=0
            )

        # =====================================================
        # DATA ROWS
        # =====================================================
        for idx, row in enumerate(self.data_rows):

            bg_color = (
                COLORS["bg_table"]
                if idx % 2 == 0
                else COLORS["bg_card"]
            )

            values = [
                (
                    row["provinsi"],
                    COLORS["text"]
                ),
                (
                    f"{row['total_raw']:,}",
                    COLORS["text"]
                ),
                (
                    f"{row['delive']:,}",
                    COLORS["success"]
                ),
                (
                    row["ratio_delive"],
                    COLORS["success"]
                ),
                (
                    f"{row['rts']:,}",
                    COLORS["danger"]
                ),
                (
                    row["ratio_rts_delive"],
                    COLORS["danger"]
                ),
            ]

            row_index = idx + 1

            for col, (value, color) in enumerate(values):

                anchor_pos = (
                    "w"
                    if col == 0
                    else "e"
                )

                padx_val = (
                    (16, 8)
                    if col == 0
                    else (8, 16)
                )

                ctk.CTkLabel(
                    table_container,
                    text=value,
                    text_color=color,
                    fg_color=bg_color,
                    height=40,
                    anchor=anchor_pos,
                    font=(
                        FONTS["small"]
                        if col == 0
                        else FONTS["mono"]
                    )
                ).grid(
                    row=row_index,
                    column=col,
                    sticky="nsew",
                    padx=0,
                    pady=0
                )

    def set_active(self, active):
        self.is_active = active
        self.title_label.configure(
            text_color=COLORS["primary"] if active else COLORS["text"]
        )