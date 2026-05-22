"""
Main App: SalesDataApp
"""

import customtkinter as ctk
from pathlib import Path

from infrastructure.config.app_config import AppConfig
from presentation.components.side_bar import Sidebar
from presentation.views.dashboard_view import DashboardView
from presentation.views.rate_zonasi_view import RateZonasiView
from presentation.views.regional_summary_view import RegionalSummaryView
from presentation.views.transformer_view import TransformerView
from presentation.views.performance_view import PerformanceView
from presentation.views.history_view import HistoryView


class SalesDataApp:
    """Main application window."""
    
    def __init__(self):
        self.config = AppConfig()
        self.config.ensure_directories()
        
        ctk.set_appearance_mode(self.config.THEME)
        ctk.set_default_color_theme(self.config.COLOR_THEME)
        
        self.root = ctk.CTk()
        self.root.title(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        self.root.geometry(f"{self.config.APP_WIDTH}x{self.config.APP_HEIGHT}")
        self.root.minsize(900, 600)
        
        self._setup_layout()
        self._setup_sidebar()
        self._setup_views()
        self.show_view("dashboard")
    
    def _setup_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def _setup_sidebar(self):
        self.sidebar = Sidebar(
            master=self.root,
            on_navigate=self.show_view,
            app_name=self.config.APP_NAME
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def _setup_views(self):
        self.views = {}
        
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        self.views["dashboard"] = DashboardView(self.content_frame)
        self.views["regional_summary"] = RegionalSummaryView(self.content_frame)
        self.views["rate_zonasi"] = RateZonasiView(self.content_frame)
        self.views["transformer"] = TransformerView(self.content_frame)
        self.views["performance"] = PerformanceView(self.content_frame)
        self.views["history"] = HistoryView(self.content_frame)
        
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")
            view.grid_remove()
    
    def show_view(self, view_name: str):
        for view in self.views.values():
            view.grid_remove()
        
        if view_name in self.views:
            self.views[view_name].grid()
            self.views[view_name].on_show()
            self.sidebar.set_active(view_name)
    
    def run(self):
        self.root.mainloop()