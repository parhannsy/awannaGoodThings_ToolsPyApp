"""
Component: TeamTable
Menangani rendering visual data anggota tim offline (CS / Gudang) secara tabular.
"""

import customtkinter as ctk


class TeamTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
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
        
        # Container scrollable untuk data tim
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_container.pack(fill="both", expand=True, pady=(5, 0))

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
        for widget in self.scroll_container.winfo_children():
            widget.destroy()
            
        if not team_members:
            no_data = ctk.CTkLabel(self.scroll_container, text="Tidak ada data anggota tim ditemukan.", text_color="#6B7280")
            no_data.pack(pady=40)
            return

        for index, member in enumerate(team_members):
            row = ctk.CTkFrame(
                self.scroll_container, 
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