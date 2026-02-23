"""
Core.Styles.compat_manager - Gestor de compatibilidad entre ttkbootstrap y tkinter
"""


class CompatibilityManager:
    """
    Gestor de compatibilidad entre ttkbootstrap y tkinter.
    
    Evita conflictos de opciones de widgets.
    """
    
    # Opciones conflictivas
    CONFLICTING_OPTIONS = {
        'Label': {
            'tkinter': ['width', 'height', 'wraplength', 'justify', 'padx', 'pady'],
            'ttkbootstrap': ['bootstyle', 'background', 'foreground']
        },
        'Frame': {
            'tkinter': ['width', 'height', 'bg', 'background'],
            'ttkbootstrap': ['bootstyle']
        },
        'Entry': {
            'tkinter': ['width', 'font'],
            'ttkbootstrap': ['bootstyle']
        },
        'Button': {
            'tkinter': ['bg', 'fg', 'relief', 'bd', 'padx', 'pady'],
            'ttkbootstrap': ['bootstyle']
        }
    }
    
    @staticmethod
    def sanitize_tkinter_options(**kwargs) -> dict:
        """
        Elimina opciones problemáticas para ttkbootstrap.
        
        Args:
            **kwargs: Opciones del widget
            
        Returns:
            dict: Opciones filtradas
        """
        problematic = ['width', 'height', 'wraplength', 'justify']
        return {k: v for k, v in kwargs.items() if k not in problematic}
    
    @staticmethod
    def sanitize_labelframe_options(**kwargs) -> dict:
        """
        Elimina opciones problemáticas para tk.LabelFrame.
        
        Args:
            **kwargs: Opciones del widget
            
        Returns:
            dict: Opciones filtradas
        """
        problematic = ['padding', 'bootstyle']
        return {k: v for k, v in kwargs.items() if k not in problematic}
    
    @staticmethod
    def check_widget_compatibility(widget_type: str) -> dict:
        """
        Verifica compatibilidad de un widget.
        
        Args:
            widget_type: Tipo de widget
            
        Returns:
            dict: Información de compatibilidad
        """
        return CompatibilityManager.CONFLICTING_OPTIONS.get(widget_type, {})
    
    @staticmethod
    def get_safe_pack_options(**kwargs) -> dict:
        """
        Retorna opciones seguras para pack().
        
        Args:
            **kwargs: Opciones
            
        Returns:
            dict: Opciones seguras
        """
        safe_options = ['side', 'fill', 'expand', 'padx', 'pady', 'anchor', 'in_']
        return {k: v for k, v in kwargs.items() if k in safe_options}
    
    @staticmethod
    def get_safe_grid_options(**kwargs) -> dict:
        """
        Retorna opciones seguras para grid().
        
        Args:
            **kwargs: Opciones
            
        Returns:
            dict: Opciones seguras
        """
        safe_options = ['row', 'column', 'sticky', 'padx', 'pady', 'columnspan', 'rowspan', 'in_']
        return {k: v for k, v in kwargs.items() if k in safe_options}