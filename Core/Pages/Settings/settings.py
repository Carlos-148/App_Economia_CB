"""
Core.Pages.Settings.settings - Página de Configuración Completa
Todo integrado en un archivo con comentarios para separar secciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

from Core.Styles.base_components import BaseFrame, StyledLabel, CardFrame
from Core.Backends.settings_backend import SettingsBackend
from Core.Common.logger import setup_logger
from ttkbootstrap.constants import LEFT, RIGHT, X, Y, BOTH

logger = setup_logger()


class SettingsFrame(BaseFrame):
    """Página completa de configuración con todas las secciones integradas"""
    
    def __init__(self, parent):
        from Core.Common.config import load_config
        config = load_config()
        theme = config.get("theme", "solar")
        
        super().__init__(parent, theme_name=theme)
        self.logger = setup_logger()
        self.backend = SettingsBackend()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la UI completa"""
        
        # ============================================
        # HEADER - TÍTULO Y SUBTÍTULO
        # ============================================
        header = BaseFrame(self, theme_name=self.theme_name)
        header.pack(fill=X, padx=20, pady=(20, 15))
        
        title = StyledLabel(
            header,
            text="⚙️ CONFIGURACIÓN AVANZADA",
            label_type="title",
            theme_name=self.theme_name
        )
        title.set_accent()
        title.pack(anchor="w", pady=(0, 5))
        
        subtitle = StyledLabel(
            header,
            text="Gestiona la configuración de tu aplicación",
            label_type="small",
            theme_name=self.theme_name
        )
        subtitle.pack(anchor="w")
        
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=X, padx=20, pady=(0, 15))
        
        # ============================================
        # CONTENEDOR PRINCIPAL - 2 COLUMNAS
        # ============================================
        content = BaseFrame(self, theme_name=self.theme_name)
        content.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # ============================================
        # COLUMNA IZQUIERDA - GESTIÓN DE DATOS
        # ============================================
        left_column = BaseFrame(content, theme_name=self.theme_name)
        left_column.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        left_title = StyledLabel(
            left_column,
            text="📋 GESTIÓN DE DATOS",
            label_type="heading",
            theme_name=self.theme_name
        )
        left_title.pack(anchor="w", pady=(0, 15))
        
        # ============================================
        # SECCIÓN 1: BASE DE DATOS
        # ============================================
        self._create_database_section(left_column)
        
        # ============================================
        # SECCIÓN 2: USUARIO
        # ============================================
        self._create_user_section(left_column)
        
        # ============================================
        # SECCIÓN 3: EXPORTES
        # ============================================
        self._create_export_section(left_column)
        
        # ============================================
        # COLUMNA DERECHA - APARIENCIA Y SISTEMA
        # ============================================
        right_column = BaseFrame(content, theme_name=self.theme_name)
        right_column.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))
        
        right_title = StyledLabel(
            right_column,
            text="🎨 APARIENCIA Y SISTEMA",
            label_type="heading",
            theme_name=self.theme_name
        )
        right_title.pack(anchor="w", pady=(0, 15))
        
        # ============================================
        # SECCIÓN 4: TEMAS
        # ============================================
        self._create_theme_section(right_column)
        
        # ============================================
        # SECCIÓN 5: ESTADÍSTICAS
        # ============================================
        self._create_stats_section(right_column)
        
        # ============================================
        # SECCIÓN 6: UTILIDADES
        # ============================================
        self._create_utilities_section(right_column)
        
        self.logger.info("✅ SettingsFrame inicializado completamente")
    
    # ============================================
    # SECCIÓN 1: BASE DE DATOS
    # ============================================
    def _create_database_section(self, parent):
        """Crea la sección de base de datos"""
        card = CardFrame(parent, title="🗄️ BASE DE DATOS", theme_name=self.theme_name)
        card.pack(fill=X, pady=(0, 10))
        
        # Estado
        state_frame = BaseFrame(card, theme_name=self.theme_name)
        state_frame.pack(fill=X, padx=10, pady=(10, 8))
        
        tk.Label(state_frame, text="Estado:", font=("Segoe UI", 9), bg=self.bg_color).pack(side=tk.LEFT, padx=(0, 10))
        
        self.db_state_label = StyledLabel(
            state_frame,
            text="Cargando...",
            label_type="small",
            theme_name=self.theme_name
        )
        self.db_state_label.pack(side=tk.LEFT)
        
        # Información
        info_label = StyledLabel(card, text="Información:", label_type="small", theme_name=self.theme_name)
        info_label.pack(anchor="w", padx=10, pady=(8, 3))
        
        self.db_info_text = tk.Text(
            card, height=3, wrap=tk.WORD, bg="white", relief="solid", bd=1,
            font=("Segoe UI", 8), state=tk.DISABLED
        )
        self.db_info_text.pack(fill=X, padx=10, pady=(0, 8))
        
        # Botones
        button_frame = BaseFrame(card, theme_name=self.theme_name)
        button_frame.pack(fill=X, padx=10, pady=(0, 8))
        
        buttons = [
            ("🔌 Probar", self.test_db_connection, "#0dcaf0", 0),
            ("📊 Stats", self.show_db_stats, "#17a2b8", 1),
            ("📥 Backups", self.show_db_backups, "#6c757d", 2),
            ("🔄 Reset", self.reset_db_data, "#ffc107", 0),
            ("🔨 Nueva BD", self.create_new_db, "#dc3545", 1),
            ("📂 Abrir", self.open_db_folder, "#007bff", 2),
        ]
        
        for text, cmd, color, col in buttons:
            row = 0 if col < 3 else 1
            tk.Button(
                button_frame, text=text, command=cmd, bg=color,
                fg="black" if color == "#ffc107" else "white",
                relief="flat", cursor="hand2", bd=0, font=("Segoe UI", 8, "bold"),
                padx=8, pady=4
            ).grid(row=row, column=col if col < 3 else col-3, sticky=tk.EW, padx=2, pady=2)
        
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
        
        # Cargar estado inicial
        self.update_db_status()
    
    # ============================================
    # SECCIÓN 2: USUARIO
    # ============================================
    def _create_user_section(self, parent):
        """Crea la sección de usuario"""
        card = CardFrame(parent, title="👤 USUARIO", theme_name=self.theme_name)
        card.pack(fill=X, pady=(0, 10))
        
        # Nombre
        name_frame = BaseFrame(card, theme_name=self.theme_name)
        name_frame.pack(fill=X, padx=10, pady=(10, 6))
        
        tk.Label(name_frame, text="Nombre:", font=("Segoe UI", 9), bg=self.bg_color).pack(side=tk.LEFT, anchor="w")
        
        self.user_entry_name = tk.Entry(name_frame, font=("Segoe UI", 9))
        self.user_entry_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Capital (solo lectura)
        capital_frame = BaseFrame(card, theme_name=self.theme_name)
        capital_frame.pack(fill=X, padx=10, pady=(0, 6))
        
        tk.Label(capital_frame, text="Capital:", font=("Segoe UI", 9), bg=self.bg_color).pack(side=tk.LEFT, anchor="w")
        
        self.user_entry_capital = tk.Entry(capital_frame, font=("Segoe UI", 9), state=tk.DISABLED)
        self.user_entry_capital.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Info
        info_label = StyledLabel(
            card, text="💡 Se gestiona en: Caja → Efectivo",
            label_type="small", theme_name=self.theme_name
        )
        info_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Botón guardar
        tk.Button(
            card, text="💾 Guardar", command=self.save_user,
            bg="#198754", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        ).pack(fill=X, padx=10, pady=(0, 10))
        
        # Cargar valores
        self.load_user_values()
    
    # ============================================
    # SECCIÓN 3: EXPORTES
    # ============================================
    def _create_export_section(self, parent):
        """Crea la sección de exportes"""
        card = CardFrame(parent, title="📊 EXPORTES", theme_name=self.theme_name)
        card.pack(fill=X, pady=(0, 10))
        
        button_frame = BaseFrame(card, theme_name=self.theme_name)
        button_frame.pack(fill=X, padx=10, pady=(10, 10))
        
        tk.Button(
            button_frame, text="📤 Exportar", command=self.export_summary,
            bg="#0dcaf0", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        ).pack(fill=X, pady=(0, 5))
        
        tk.Button(
            button_frame, text="📁 Abrir Carpeta", command=self.open_exports_folder,
            bg="#0d6efd", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        ).pack(fill=X)
    
    # ============================================
    # SECCIÓN 4: TEMAS
    # ============================================
    def _create_theme_section(self, parent):
        """Crea la sección de temas"""
        card = CardFrame(parent, title="🎨 TEMAS", theme_name=self.theme_name)
        card.pack(fill=X, pady=(0, 10))
        
        # Tema oficial
        label1 = StyledLabel(card, text="Tema Oficial:", label_type="small", theme_name=self.theme_name)
        label1.pack(anchor="w", padx=10, pady=(10, 4))
        
        theme_frame = BaseFrame(card, theme_name=self.theme_name)
        theme_frame.pack(fill=X, padx=10, pady=(0, 8))
        
        self.theme_combo = ttk.Combobox(
            theme_frame, values=self.backend.get_valid_themes(),
            state="readonly", width=20
        )
        self.theme_combo.set(self.backend.get_current_theme())
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            theme_frame, text="✅", command=self.apply_theme,
            bg="#198754", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), width=3, padx=5, pady=2
        ).pack(side=tk.LEFT)
        
        # Presets
        label2 = StyledLabel(card, text="Preset:", label_type="small", theme_name=self.theme_name)
        label2.pack(anchor="w", padx=10, pady=(8, 4))
        
        preset_frame = BaseFrame(card, theme_name=self.theme_name)
        preset_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.preset_combo = ttk.Combobox(
            preset_frame, values=self.backend.get_theme_presets(),
            state="readonly", width=20
        )
        self.preset_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            preset_frame, text="✅", command=self.apply_preset,
            bg="#198754", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), width=3, padx=5, pady=2
        ).pack(side=tk.LEFT)
    
    # ============================================
    # SECCIÓN 5: ESTADÍSTICAS
    # ============================================
    def _create_stats_section(self, parent):
        """Crea la sección de estadísticas"""
        card = CardFrame(parent, title="📈 ESTADÍSTICAS", theme_name=self.theme_name)
        card.pack(fill=X, pady=(0, 10))
        
        self.stats_text = tk.Text(
            card, height=4, wrap=tk.WORD, bg="white", relief="solid", bd=1,
            font=("Segoe UI", 8), state=tk.DISABLED
        )
        self.stats_text.pack(fill=X, padx=10, pady=(10, 8))
        
        tk.Button(
            card, text="🔄 Actualizar", command=self.load_stats,
            bg="#0dcaf0", fg="white", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        ).pack(fill=X, padx=10, pady=(0, 10))
        
        # Cargar datos iniciales
        self.load_stats()
    
    # ============================================
    # SECCIÓN 6: UTILIDADES
    # ============================================
    def _create_utilities_section(self, parent):
        """Crea la sección de utilidades"""
        card = CardFrame(parent, title="🛠️ UTILIDADES", theme_name=self.theme_name)
        card.pack(fill=X, pady=(0, 10))
        
        tk.Button(
            card, text="🔄 Recargar App", command=self.reload_app,
            bg="#ffc107", fg="black", relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4
        ).pack(fill=X, padx=10, pady=(10, 10))
    
    # ============================================
    # MÉTODOS: DATABASE
    # ============================================
    def test_db_connection(self):
        success, msg = self.backend.test_db_connection()
        messagebox.showinfo("Conexión BD", msg)
        self.update_db_status()
    
    def show_db_stats(self):
        stats = self.backend.get_db_stats()
        msg = f"📊 BD: {stats.get('database', 'N/A')}\nTablas: {stats.get('tables', 0)}\nRegistros: {stats.get('rows', 0):,}"
        messagebox.showinfo("📊 Estadísticas", msg)
    
    def show_db_backups(self):
        backups = self.backend.list_backups()
        if not backups:
            messagebox.showinfo("💾 Backups", "No hay backups")
            return
        msg = "💾 BACKUPS:\n\n"
        for idx, backup in enumerate(backups[:5], 1):
            msg += f"{idx}. {backup.get('filename', 'N/A')}\n"
        messagebox.showinfo("💾 Backups", msg)
    
    def reset_db_data(self):
        if messagebox.askyesno("⚠️ RESET", "¿Eliminar todos los datos?"):
            success, msg = self.backend.reset_database()
            messagebox.showinfo("✅" if success else "❌", msg)
            self.update_db_status()
    
    def create_new_db(self):
        if messagebox.askyesno("⚠️ BD NUEVA", "¿Crear BD nueva? (Irreversible)"):
            success, msg = self.backend.create_new_database()
            if success:
                messagebox.showinfo("✅", msg)
                import sys
                sys.exit(0)
            else:
                messagebox.showerror("❌", msg)
    
    def open_db_folder(self):
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
    
    def update_db_status(self):
        success, msg = self.backend.test_db_connection()
        if success:
            self.db_state_label.config(text="✅ Activa", foreground="#28a745")
            stats = self.backend.get_db_stats()
            info = f"🗄️ {stats.get('database', 'N/A')}\n📊 Tablas: {stats.get('tables', 0)}\n📦 Registros: {stats.get('rows', 0):,}"
        else:
            self.db_state_label.config(text="❌ Error", foreground="#dc3545")
            info = msg
        
        self.db_info_text.config(state=tk.NORMAL)
        self.db_info_text.delete(1.0, tk.END)
        self.db_info_text.insert(1.0, info.strip())
        self.db_info_text.config(state=tk.DISABLED)
    
    # ============================================
    # MÉTODOS: USUARIO
    # ============================================
    def load_user_values(self):
        user_config = self.backend.get_user_config()
        self.user_entry_name.delete(0, tk.END)
        self.user_entry_name.insert(0, user_config.get("name", ""))
        
        self.user_entry_capital.config(state=tk.NORMAL)
        self.user_entry_capital.delete(0, tk.END)
        self.user_entry_capital.insert(0, str(user_config.get("capital", 0.0)))
        self.user_entry_capital.config(state=tk.DISABLED)
    
    def save_user(self):
        name = self.user_entry_name.get().strip()
        if not name:
            messagebox.showwarning("Validación", "Ingresa un nombre")
            return
        
        success, msg = self.backend.save_user_config(name, 0.0)
        messagebox.showinfo("✅" if success else "❌", msg)
    
    # ============================================
    # MÉTODOS: EXPORTES
    # ============================================
    def export_summary(self):
        success, msg = self.backend.export_summary()
        messagebox.showinfo("✅" if success else "���", msg)
    
    def open_exports_folder(self):
        success, msg = self.backend.open_exports_folder()
        if success:
            self.logger.info(msg)
        else:
            messagebox.showerror("❌", msg)
    
    # ============================================
    # MÉTODOS: TEMAS
    # ============================================
    def apply_theme(self):
        theme = self.theme_combo.get().strip()
        if not theme:
            messagebox.showwarning("Aviso", "Selecciona un tema")
            return
        
        success, msg = self.backend.save_theme(theme)
        messagebox.showinfo("✅" if success else "❌", msg)
    
    def apply_preset(self):
        preset = self.preset_combo.get().strip()
        if not preset:
            messagebox.showwarning("Aviso", "Selecciona un preset")
            return
        
        success, msg = self.backend.apply_preset(preset)
        messagebox.showinfo("✅" if success else "❌", msg)
    
    # ============================================
    # MÉTODOS: ESTADÍSTICAS
    # ============================================
    def load_stats(self):
        try:
            stats = self.backend.get_system_stats()
            
            app_version = stats.get('app_version', 'N/A')
            current_user = stats.get('current_user', 'N/A')
            current_theme = stats.get('current_theme', 'N/A')
            
            db_info = stats.get('database', {})
            database = db_info.get('database', 'N/A') if isinstance(db_info, dict) else 'N/A'
            rows = db_info.get('rows', 0) if isinstance(db_info, dict) else 0
            
            msg = f"""📱 v{app_version}
👤 {current_user}
🎨 {current_theme}

🗄️ {database}
📦 Registros: {rows:,}"""
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, msg.strip())
            self.stats_text.config(state=tk.DISABLED)
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    # ============================================
    # MÉTODOS: UTILIDADES
    # ============================================
    def reload_app(self):
        if messagebox.askyesno("🔄 Recargar", "¿Reiniciar la aplicación?"):
            self.backend.reload_application()