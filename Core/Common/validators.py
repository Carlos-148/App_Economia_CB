"""
Core.Common.validators - Validadores centralizados para formularios
"""

import re
from typing import Tuple, Dict, Any


class FormValidator:
    """Validador centralizado y único para todos los formularios"""
    
    PATTERNS = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "phone": r'^\+?1?\d{9,15}$',
        "number": r'^-?\d+\.?\d*$',
        "positive_number": r'^\d+\.?\d*$',
        "alphanumeric": r'^[a-zA-Z0-9_]+$',
        "url": r'^https?://',
    }
    
    @staticmethod
    def validate_required(value: str, field_name: str = "Campo") -> Tuple[bool, str]:
        """Valida que el campo no esté vacío"""
        if not value or not str(value).strip():
            return False, f"❌ {field_name} es requerido"
        return True, ""
    
    @staticmethod
    def validate_number(
        value: str,
        field_name: str = "Campo",
        positive_only: bool = True,
        min_val: float = None,
        max_val: float = None
    ) -> Tuple[bool, str]:
        """Valida que sea un número válido dentro de rango opcional"""
        try:
            num = float(str(value).strip())
            
            if positive_only and num < 0:
                return False, f"❌ {field_name} debe ser positivo"
            
            if min_val is not None and num < min_val:
                return False, f"❌ {field_name} debe ser >= {min_val}"
            
            if max_val is not None and num > max_val:
                return False, f"❌ {field_name} debe ser <= {max_val}"
            
            return True, ""
            
        except (ValueError, TypeError):
            return False, f"❌ {field_name} debe ser un número válido"
    
    @staticmethod
    def validate_range(
        value: str,
        min_val: float = None,
        max_val: float = None,
        field_name: str = "Campo"
    ) -> Tuple[bool, str]:
        """Valida rango numérico"""
        try:
            num = float(str(value).strip())
            
            if min_val is not None and num < min_val:
                return False, f"❌ {field_name} debe ser >= {min_val}"
            
            if max_val is not None and num > max_val:
                return False, f"❌ {field_name} debe ser <= {max_val}"
            
            return True, ""
            
        except (ValueError, TypeError):
            return False, f"❌ {field_name} debe ser un número"
    
    @staticmethod
    def validate_length(
        value: str,
        min_len: int = None,
        max_len: int = None,
        field_name: str = "Campo"
    ) -> Tuple[bool, str]:
        """Valida longitud de texto"""
        value_str = str(value).strip()
        
        if min_len and len(value_str) < min_len:
            return False, f"❌ {field_name} debe tener >= {min_len} caracteres"
        
        if max_len and len(value_str) > max_len:
            return False, f"❌ {field_name} no puede exceder {max_len} caracteres"
        
        return True, ""
    
    @staticmethod
    def validate_email(value: str) -> Tuple[bool, str]:
        """Valida formato de email"""
        if not re.match(FormValidator.PATTERNS["email"], str(value).strip()):
            return False, "❌ Email inválido"
        return True, ""
    
    @staticmethod
    def validate_phone(value: str) -> Tuple[bool, str]:
        """Valida formato de teléfono"""
        if not re.match(FormValidator.PATTERNS["phone"], str(value).strip()):
            return False, "❌ Teléfono inválido"
        return True, ""
    
    @staticmethod
    def validate_pattern(
        value: str,
        pattern_key: str,
        field_name: str = "Campo"
    ) -> Tuple[bool, str]:
        """Valida usando patrones predefinidos"""
        if pattern_key not in FormValidator.PATTERNS:
            return False, "❌ Patrón desconocido"
        
        if not re.match(FormValidator.PATTERNS[pattern_key], str(value).strip()):
            return False, f"❌ {field_name} tiene formato inválido"
        
        return True, ""
    
    @staticmethod
    def validate_form(form_data: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Valida un formulario completo.
        
        Args:
            form_data: {
                'field_name': {
                    'value': '...',
                    'validators': [
                        ('required', {}),
                        ('number', {'positive_only': True}),
                    ]
                }
            }
        
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        for field_name, field_config in form_data.items():
            value = field_config.get('value', '')
            validators = field_config.get('validators', [])
            
            for validator_name, validator_kwargs in validators:
                is_valid = False
                msg = ""
                
                if validator_name == 'required':
                    is_valid, msg = FormValidator.validate_required(value, field_name)
                elif validator_name == 'number':
                    is_valid, msg = FormValidator.validate_number(value, field_name, **validator_kwargs)
                elif validator_name == 'range':
                    is_valid, msg = FormValidator.validate_range(value, field_name=field_name, **validator_kwargs)
                elif validator_name == 'length':
                    is_valid, msg = FormValidator.validate_length(value, field_name=field_name, **validator_kwargs)
                elif validator_name == 'email':
                    is_valid, msg = FormValidator.validate_email(value)
                elif validator_name == 'phone':
                    is_valid, msg = FormValidator.validate_phone(value)
                elif validator_name == 'pattern':
                    is_valid, msg = FormValidator.validate_pattern(value, field_name=field_name, **validator_kwargs)
                
                if not is_valid:
                    return False, msg
        
        return True, ""