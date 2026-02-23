"""
Core.Pages.Settings.database_section - Sección de Base de Datos
Usa configuración centralizada
"""

import tkinter as tk
from tkinter import messagebox

from Core.Styles.base_components import BaseFrame, StyledLabel, CardFrame
from Core.Backends.settings_backend import SettingsBackend
from Core.Common.logger import setup_logger
from Core.Pages.Settings.settings_config import DATABASE_SECTION, LAYOUT

logger = setup_logger()


class DatabaseSection(BaseFrame):
    """Sección de gestión de base de datos"""
    
    def __init__(self, parent, theme_name="solar", backend: SettingsBackend = None):
        super().__init__(parent, theme_name=theme_name)
        self.backend = backend or SettingsBackend()
        self.logger = setup_logger()
        self.config = DATABASE_SECTION
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """Configura la interfaz"""
        card = CardFrame(self, title=self.config['title'], theme_name=self.theme_name)
        card.pack(fill=tk.X, pady=LAYOUT['card_pady'])
        
        # Estado
        state_frame = BaseFrame(card, theme_name=self.theme_name)
        state_frame.pack(fill=tk.X, padx=10, pady=(10, 8))
        
        tk.Label(
            state_frame, 
            text=self.config['state_label'], 
            font=("Segoe UI", 9),
            bg=self.bg_color
        ).pack(side=tk.LEFT, anchor="w", padx=(0, 10))
        
        self.lbl_state = StyledLabel(
            state_frame,
            text="Cargando...",
            label_type="small",
            theme_name=self.theme_name
        )
        self.lbl_state.pack(side=tk.LEFT)
        
        # Información
        info_label = StyledLabel(
            card,
            text=self.config['info_label'],
            label_type="small",
            theme_name=self.theme_name
        )
        info_label.pack(anchor="w", padx=10, pady=(8, 3))
        
        self.info_text = tk.Text(
            card,
            height=3,
            wrap=tk.WORD,
            bg="white",
            relief="solid",
            bd=1,
            font=("Segoe UI", 8),
            state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # Botones
        button_frame = BaseFrame(card, theme_name=self.theme_name)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        for idx, btn_config in enumerate(self.config['buttons']):
            row = idx // 3
            col = idx % 3
            
            tk.Button(
                button_frame,
                text=btn_config['text'],
                command=getattr(self, btn_config['command']),
                bg=btn_config['color'],
                fg="white" if btn_config['color'] != "#ffc107" else "black",
                relief="flat",
                cursor="hand2",
                bd=0,
                font=("Segoe UI", 8, "bold"),
                padx=8,
                pady=4
            ).grid(
                row=row, 
                column=col, 
                sticky=tk.EW, 
                padx=LAYOUT['button_grid_padx'], 
                pady=LAYOUT['button_grid_pady']
            )
        
        # Configurar columnas
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
    
    def test_connection(self):
        success, msg = self.backend.test_db_connection()
        if success:
            messagebox.showinfo("✅ Conexión", msg)
            self.update_status()
        else:
            messagebox.showerror("❌ Error", msg)
    
    def show_stats(self):
        stats = self.backend.get_db_stats()
        msg = f"📊 BD: {stats.get('database', 'N/A')}\n📊 Tablas: {stats.get('tables', 0)}\n📦 Registros: {stats.get('rows', 0):,}"
        messagebox.showinfo("📊 Stats", msg)
    
    def reset_data(self):
        if not messagebox.askyesno("⚠️ RESET", "¿Eliminar todos los datos?"):
            return
        success, msg = self.backend.reset_database()
        if success:
            messagebox.showinfo("✅ OK", msg)
            self.update_status()
        else:
            messagebox.showerror("❌ Error", msg)
    
    def create_new_db(self):
        if not messagebox.askyesno("⚠️ BD NUEVA", "¿Crear BD nueva? (Irreversible)"):
            return
        success, msg = self.backend.create_new_database()
        if success:
            messagebox.showinfo("✅ OK", msg)
            import sys
            sys.exit(0)
        else:
            messagebox.showerror("❌ Error", msg)
    
    def show_backups(self):
        backups = self.backend.list_backups()
        if not backups:
            messagebox.showinfo("💾 Backups", "No hay backups")
            return
        msg = "💾 BACKUPS:\n\n"
        for idx, backup in enumerate(backups[:5], 1):
            msg += f"{idx}. {backup.get('filename', 'N/A')}\n"
        messagebox.showinfo("💾 Backups", msg)
    
    def open_folder(self):
        import os
        folder = self.backend.get_db_folder()
        if not os.path.exists(folder):
            messagebox.showinfo("ℹ️", f"No existe: {folder}")
            return
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif os.name == "posix":
                import subprocess
                subprocess.Popen(["open", folder])
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)[:100]}")
    
    def update_status(self):
        try:
            success, msg = self.backend.test_db_connection()
            if success:
                self.lbl_state.config(text="✅ Activa", foreground="#28a745")
                stats = self.backend.get_db_stats()
                info = f"🗄️ {stats.get('database', 'N/A')}\n📊 Tablas: {stats.get('tables', 0)}\n📦 Registros: {stats.get('rows', 0):,}"
            else:
                self.lbl_state.config(text="❌ Error", foreground="#dc3545")
                info = msg
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info.strip())
            self.info_text.config(state=tk.DISABLED)
        except Exception as e:
            self.logger.error(f"Error: {e}")