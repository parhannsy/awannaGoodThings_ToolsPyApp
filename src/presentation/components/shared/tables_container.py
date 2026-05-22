"""
Komponen: TablesContainer
Container responsive untuk grid tabel dengan smart adaptive layout.
"""

import customtkinter as ctk
from .table_card import TableCard


class TablesContainer:
    """Container tabel dengan responsive smart layout."""

    TWO_COL_THRESHOLD = 700

    def __init__(self, parent_scroll_frame, on_table_click=None):
        self.parent_scroll = parent_scroll_frame
        self.on_table_click = on_table_click
        self.table_cards = {}
        self.table_wrappers = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup container utama."""

        self.container = ctk.CTkFrame(
            self.parent_scroll,
            fg_color="transparent"
        )
        self.container.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.parent_scroll.grid_columnconfigure(0, weight=1)
        self.parent_scroll.grid_rowconfigure(0, weight=1)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

        self.container.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None):
        """Responsive smart layout."""

        if not self.table_wrappers:
            return

        width = self.container.winfo_width()

        total_tables = len(self.table_wrappers)

        # Mobile → selalu 1 kolom
        if width < self.TWO_COL_THRESHOLD:
            cols = 1
        else:
            cols = 2

        # Reset semua konfigurasi kolom
        for i in range(4):
            self.container.grid_columnconfigure(i, weight=0)

        # Aktifkan kolom yang dipakai
        for i in range(cols):
            self.container.grid_columnconfigure(i, weight=1)

        # Hapus grid lama
        for wrapper in self.table_wrappers:
            wrapper.grid_forget()

        # ==========================================
        # MODE 1 KOLOM
        # ==========================================
        if cols == 1:

            for i, wrapper in enumerate(self.table_wrappers):

                wrapper.grid(
                    row=i,
                    column=0,
                    sticky="ew",
                    padx=0,
                    pady=4
                )

        # ==========================================
        # MODE 2 KOLOM SMART
        # ==========================================
        else:

            row = 0
            i = 0

            while i < total_tables:

                remaining = total_tables - i

                # ==================================================
                # Jika sisa tinggal 1 → full width
                # ==================================================
                if remaining == 1:

                    wrapper = self.table_wrappers[i]

                    wrapper.grid(
                        row=row,
                        column=0,
                        columnspan=2,
                        sticky="ew",
                        padx=0,
                        pady=4
                    )

                    i += 1
                    row += 1

                # ==================================================
                # Selain itu → tampilkan berpasangan
                # ==================================================
                else:

                    left_wrapper = self.table_wrappers[i]
                    right_wrapper = self.table_wrappers[i + 1]

                    left_wrapper.grid(
                        row=row,
                        column=0,
                        sticky="nsew",
                        padx=(0, 4),
                        pady=4
                    )

                    right_wrapper.grid(
                        row=row,
                        column=1,
                        sticky="nsew",
                        padx=(4, 0),
                        pady=4
                    )

                    i += 2
                    row += 1

        self.container.update_idletasks()

    def create_tables(self, dates_list, current_results):
        """Create seluruh table card."""

        for widget in self.container.winfo_children():
            widget.destroy()

        self.table_cards = {}
        self.table_wrappers = []

        total_tables = len(dates_list)

        for i, date_str in enumerate(dates_list):

            wrapper = ctk.CTkFrame(
                self.container,
                fg_color="transparent"
            )

            wrapper.grid_columnconfigure(0, weight=1)
            wrapper.grid_rowconfigure(0, weight=1)

            self.table_wrappers.append(wrapper)

            card = TableCard(
                wrapper,
                index=i,
                date_str=date_str,
                result=current_results[date_str],
                on_click=self.on_table_click
            )

            # Jika cuma 1 tabel → paksa expand penuh
            if total_tables == 1:

                try:
                    card.container.pack(
                        fill="both",
                        expand=True,
                        padx=0,
                        pady=0
                    )
                except Exception:
                    pass

            self.table_cards[i] = card

        self.container.update_idletasks()
        self._on_resize()

    def get_header_label(self, index):
        """Return header label."""

        if index in self.table_cards:
            return self.table_cards[index].get_header_label()

        return None

    def set_active_table(self, index):
        """Highlight active table."""

        for idx, card in self.table_cards.items():
            card.set_active(idx == index)

    def clear(self):
        """Hapus semua tabel."""

        for widget in self.container.winfo_children():
            widget.destroy()

        self.table_cards = {}
        self.table_wrappers = []

    def get_canvas(self):
        """Return parent canvas."""

        return self.parent_scroll._parent_canvas