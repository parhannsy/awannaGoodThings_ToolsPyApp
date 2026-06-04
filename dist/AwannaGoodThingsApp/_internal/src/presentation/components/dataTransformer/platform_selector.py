import customtkinter as ctk


class PlatformSelector(ctk.CTkFrame):
    def __init__(self, master, variable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.variable = variable

        self.label = ctk.CTkLabel(
            self,
            text="Pilih output template",
            anchor="w",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )
        self.label.pack(
            fill="x",
            pady=(0, 10)
        )

        self.radio_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.radio_frame.pack(fill="x")

        self.spx_radio = ctk.CTkRadioButton(
            self.radio_frame,
            text="SPX",
            variable=self.variable,
            value="SPX"
        )
        self.spx_radio.pack(
            side="left",
            padx=(0, 20)
        )

        self.flik_radio = ctk.CTkRadioButton(
            self.radio_frame,
            text="FLIK",
            variable=self.variable,
            value="FLIK"
        )
        self.flik_radio.pack(side="left")