"""
Component: TeamTable
Menangani rendering visual data anggota tim offline (CS / Gudang) secara tabular.
"""

import customtkinter as ctk
import tkinter as tk


class TeamTable(ctk.CTkFrame):
    def __init__(self, master, on_edit_row_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Definisikan font statis untuk efisiensi render
        self.font_normal = ctk.CTkFont(size=13)
        self.font_badge = ctk.CTkFont(size=11, weight="bold")
        self.font_header = ctk.CTkFont(size=12, weight="bold")
        
        # Matriks warna berdasarkan divisi lini tim
        self.team_color_matrix = {
            "gudang": "#F59E0B",  # Amber / Oranye
            "cs": "#10B981"       # Hijau Emerald
        }
        
        self._setup_header()
        self.on_edit_row = on_edit_row_callback
        self._show_actions = False
        
        # Scrollable container (canvas) supporting horizontal + vertical scroll
        self._build_scrollable_area()

    def _build_scrollable_area(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, pady=(5, 0))

        self.canvas = tk.Canvas(container, bg="#0B1220", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        def _on_config(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.inner_frame.bind("<Configure>", _on_config)
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.inner_id, width=e.width))

    def _setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="#1F2937", height=40, corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Layout kolom: Nama, No HP, Alamat, Divisi Lini
        headers = [("Nama (Panggilan)", 0.03), ("No. HP", 0.30), ("Alamat", 0.55), ("Divisi Tim", 0.82)]
        for text, rel_x in headers:
            lbl = ctk.CTkLabel(
                header_frame, text=text, font=self.font_header,
                text_color="#9CA3AF", anchor="w"
            )
            lbl.place(relx=rel_x, rely=0.5, anchor="w")

    def render_rows(self, team_members: list):
        """Merender ulang baris data tim offline di dalam scroll container."""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        if not team_members:
            no_data = ctk.CTkLabel(self.inner_frame, text="Tidak ada data anggota tim ditemukan.", text_color="#6B7280")
            no_data.pack(pady=40)
            return

        for index, member in enumerate(team_members):
            row = ctk.CTkFrame(
                self.inner_frame, 
                fg_color="#111827" if index % 2 == 0 else "#1F2937", 
                height=50, 
                corner_radius=6
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # 1. Nama / Panggilan
            nama = str(member.get('nama', '')).strip()
            panggilan = str(member.get('panggilan', '')).strip()
            nama_text = f"{nama} ({panggilan})" if nama and panggilan else (nama or "-")
            
            lbl_name = ctk.CTkLabel(row, text=nama_text, text_color="#FFFFFF", font=self.font_normal)
            lbl_name.place(relx=0.03, rely=0.5, anchor="w")

            # 2. No HP
            lbl_phone = ctk.CTkLabel(row, text=member.get("nohp", "-"), text_color="#9CA3AF", font=self.font_normal)
            lbl_phone.place(relx=0.30, rely=0.5, anchor="w")

            # 3. Alamat
            lbl_address = ctk.CTkLabel(row, text=member.get("alamat", "-"), text_color="#9CA3AF", font=self.font_normal)
            lbl_address.place(relx=0.55, rely=0.5, anchor="w")

            # 4. Divisi Lini Badge
            role_tim = str(member.get("role_tim", "gudang")).strip().lower()
            badge_color = self.team_color_matrix.get(role_tim, "#9CA3AF")
            
            lbl_badge = ctk.CTkLabel(
                row, text=role_tim.upper(),
                text_color=badge_color,
                font=self.font_badge
            )
            lbl_badge.place(relx=0.82, rely=0.5, anchor="w")

            # Action column for edit (only when edit mode active)
            if self._show_actions:
                action_frame = ctk.CTkFrame(row, fg_color="transparent")
                action_frame.place(relx=0.94, rely=0.5, anchor="w")

                btn_edit = ctk.CTkButton(
                    action_frame, text="Edit", width=80,
                    fg_color="#3B82F6", hover_color="#2563EB",
                    command=(lambda m=member: self.on_edit_row(m)) if self.on_edit_row else (lambda: None)
                )
                btn_edit.pack()

    def set_show_actions(self, enabled: bool):
        self._show_actions = enabled
        