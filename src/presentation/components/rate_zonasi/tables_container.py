"""
Container untuk semua table cards dengan scroll management.
"""

from datetime import datetime

import customtkinter as ctk

from .constant import FONTS
from .table_card import RateZonasiTableCard


class RateZonasiTablesContainer(ctk.CTkFrame):
    """Container untuk semua table cards dengan scroll management."""

    def __init__(self, master, on_table_click=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_table_click = on_table_click
        self.cards = []
        self.active_index = 0

    def create_tables(self, months_list, results_dict):
        self.clear()

        for i, m_str in enumerate(months_list):
            title = self._format_title(m_str)
            data = results_dict.get(m_str, [])

            card = RateZonasiTableCard(
                self,
                title=title,
                data_rows=data,
                is_active=(i == 0)
            )
            card.pack(fill="x")
            card.bind("<Button-1>", lambda e, idx=i: self._on_card_click(idx))
            self.cards.append(card)

    def _format_title(self, month_str):
        if month_str in ["ALL_DATA", "TANPA_BULAN"]:
            return "📁 Rekap Data Zonasi Campuran"

        try:
            # Format: YYYY-MM
            date_obj = datetime.strptime(month_str, "%Y-%m")
            bulan_list = [
                "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            bulan_indo = bulan_list[date_obj.month]
            return f"Rangkuman data Bulan {bulan_indo} {date_obj.year}"
        except Exception:
            return f"Periode: {month_str}"

    def _on_card_click(self, index):
        self.set_active_table(index)
        if self.on_table_click:
            self.on_table_click(index)

    def set_active_table(self, index):
        self.active_index = index
        for i, card in enumerate(self.cards):
            card.set_active(i == index)

    def scroll_to_table(self, index):
        if 0 <= index < len(self.cards):
            self.cards[index].scroll_into_view()

    def clear(self):
        for card in self.cards:
            card.destroy()
        self.cards.clear()