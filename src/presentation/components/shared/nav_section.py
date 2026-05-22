"""
Komponen: NavSection
Tombol-tombol navigasi cepat ke tabel dengan mode horizontal carousel.
Jika tombol melebihi lebar container, user bisa scroll geser ke samping.
"""

import customtkinter as ctk
import tkinter as tk


class NavSection:
    """Section untuk tombol navigasi cepat dengan horizontal carousel."""

    ACTIVE_BG = "#2ecc71"
    ACTIVE_HOVER = "#27ae60"

    def __init__(self, parent_frame, on_navigate=None):
        self.parent = parent_frame
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active_index = 0

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI carousel horizontal."""
        self.container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.container.pack(fill="x", padx=15, pady=(3, 6))

        self.label = ctk.CTkLabel(
            self.container,
            text="Lompat ke tabel:",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self.label.pack(anchor="w", pady=(0, 4))

        self.carousel_container = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.carousel_container.pack(fill="x", expand=True)

        self.canvas = tk.Canvas(
            self.carousel_container,
            height=42,
            highlightthickness=0,
            bd=0,
            bg=self._get_bg_color()
        )
        self.canvas.pack(side="top", fill="x", expand=True)

        self.h_scroll = ctk.CTkScrollbar(
            self.carousel_container,
            orientation="horizontal",
            command=self.canvas.xview
        )
        self.h_scroll.pack(side="bottom", fill="x")

        self.canvas.configure(xscrollcommand=self.h_scroll.set)

        self.buttons_frame = ctk.CTkFrame(
            self.canvas,
            fg_color="transparent"
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.buttons_frame,
            anchor="nw"
        )

        self.buttons_frame.bind(
            "<Configure>",
            self._update_scrollregion
        )

        self.canvas.bind(
            "<Configure>",
            self._resize_canvas
        )

        self._bind_mousewheel()

    def _get_bg_color(self):
        """Ambil warna background sesuai appearance mode."""
        mode = ctk.get_appearance_mode()
        return "#2b2b2b" if mode == "Dark" else "#ebebeb"

    def _update_scrollregion(self, event=None):
        """Update area scroll canvas."""
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def _resize_canvas(self, event):
        """Resize tinggi canvas mengikuti frame."""
        self.canvas.itemconfig(
            self.canvas_window,
            height=event.height
        )

    def _bind_mousewheel(self):
        """Support scroll horizontal dengan shift + wheel."""

        def _on_mousewheel(event):
            self.canvas.xview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        self.canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel)

    def create_buttons(self, dates_list, extract_day_fn, columns_mode=2):
        """
        Buat tombol navigasi horizontal carousel.
        """

        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        self.buttons = {}

        button_data = []

        for i, date_str in enumerate(dates_list):
            day_str = extract_day_fn(date_str)

            try:
                day_num = int(day_str) if day_str != "?" else 999
            except ValueError:
                day_num = 999

            button_data.append((day_num, i, date_str, day_str))

        button_data.sort(key=lambda x: x[0])

        for position, (day_num, original_idx, date_str, day_str) in enumerate(button_data):

            btn = ctk.CTkButton(
                self.buttons_frame,
                text=f"tgl {day_str}",
                width=58,
                height=30,
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda idx=original_idx: self._on_click(idx)
            )

            btn.pack(
                side="left",
                padx=(0 if position == 0 else 4, 0),
                pady=2
            )

            self.buttons[original_idx] = btn

        self.buttons_frame.update_idletasks()
        self._update_scrollregion()

    def _on_click(self, index):
        """Handle click tombol."""
        if self.on_navigate:
            self.on_navigate(index)

    def set_active(self, index):
        """Highlight tombol aktif."""
        self.active_index = index

        for idx, btn in self.buttons.items():

            if idx == index:
                btn.configure(
                    fg_color=self.ACTIVE_BG,
                    text_color="white",
                    hover_color=self.ACTIVE_HOVER
                )

                self._scroll_to_button(btn)

            else:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    text_color=("gray10", "gray90"),
                    hover_color=("gray65", "gray35")
                )

    def _scroll_to_button(self, button):
        """Auto scroll agar tombol aktif terlihat."""

        self.canvas.update_idletasks()

        canvas_width = self.canvas.winfo_width()

        button_x = button.winfo_x()
        button_width = button.winfo_width()

        total_width = max(
            self.buttons_frame.winfo_width(),
            1
        )

        target_x = button_x - (canvas_width // 2) + (button_width // 2)

        target_x = max(0, target_x)

        self.canvas.xview_moveto(target_x / total_width)

    def clear(self):
        """Hapus semua tombol."""
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        self.buttons = {}
        self.active_index = 0

        self._update_scrollregion()