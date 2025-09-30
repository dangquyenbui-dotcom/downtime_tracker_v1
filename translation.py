"""
Simple translation system for Downtime Tracker
Handles English and Spanish translations without complex babel setup
"""

import json
import os
from flask import session

class TranslationManager:
    """Manages translations for the application"""
    
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation files"""
        # Create translations directory if it doesn't exist
        os.makedirs('translations', exist_ok=True)
        
        # Load or create English translations
        en_file = 'translations/en.json'
        if os.path.exists(en_file):
            with open(en_file, 'r', encoding='utf-8') as f:
                self.translations['en'] = json.load(f)
        else:
            self.translations['en'] = self.get_default_en_translations()
            self.save_translations('en')
        
        # Load or create Spanish translations
        es_file = 'translations/es.json'
        if os.path.exists(es_file):
            with open(es_file, 'r', encoding='utf-8') as f:
                self.translations['es'] = json.load(f)
        else:
            self.translations['es'] = self.get_default_es_translations()
            self.save_translations('es')
    
    def save_translations(self, lang):
        """Save translations to file"""
        filename = f'translations/{lang}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.translations[lang], f, ensure_ascii=False, indent=2)
    
    def get(self, key, lang=None):
        """Get translated string"""
        if lang is None:
            lang = session.get('language', 'en')
        
        # Return from translations or fallback to key
        return self.translations.get(lang, {}).get(key, 
               self.translations.get('en', {}).get(key, key))
    
    def get_default_en_translations(self):
        """Default English translations"""
        return {
            # Common
            "Downtime Tracker": "Downtime Tracker",
            "Dashboard": "Dashboard",
            "Admin Panel": "Admin Panel",
            "Logout": "Logout",
            "Login": "Login",
            "Sign In": "Sign In",
            "Welcome": "Welcome",
            "Language": "Language",
            
            # Login page
            "Username": "Username",
            "Password": "Password",
            "Enter your AD username": "Enter your AD username",
            "Enter your password": "Enter your password",
            "Active Directory Authentication": "Active Directory Authentication",
            "Access Requirements": "Access Requirements",
            "You must be a member of": "You must be a member of",
            "Submit downtime": "Submit downtime",
            "Full access": "Full access",
            "Invalid credentials": "Invalid credentials or access denied",
            "Please enter both username and password": "Please enter both username and password",
            "Active Session Detected": "Active Session Detected",
            "You have an active session from another location": "You have an active session from another location",
            "Last Activity": "Last Activity",
            "IP Address": "IP Address",
            "Continue and Sign In": "Continue and Sign In",
            "Cancel": "Cancel",
            
            # Dashboard
            "Welcome, {name}!": "Welcome, {name}!",
            "Administrator": "Administrator",
            "User": "User",
            "Email": "Email",
            "Access Level": "Access Level",
            "Full Administrative Access": "Full Administrative Access",
            "Downtime Entry Only": "Downtime Entry Only",
            "AD Groups": "AD Groups",
            "None": "None",
            "Active Facilities": "Active Facilities",
            "Production Lines": "Production Lines",
            "Downtime Events (7 days)": "Downtime Events (7 days)",
            "Downtime Categories": "Downtime Categories",
            "Report Downtime": "Report Downtime",
            "Record production downtime events": "Record production downtime events",
            "View Reports": "View Reports",
            "View downtime reports and analytics": "View downtime reports and analytics",
            "Manage facilities, lines, and settings": "Manage facilities, lines, and settings",
            "Sign out of your account": "Sign out of your account",
            
            # Downtime Entry
            "Report Production Downtime": "Report Production Downtime",
            "Edit Downtime Entry": "Edit Downtime Entry",
            "Date/Time": "Date/Time",
            "Shift": "Shift",
            "No Active Shift": "No Active Shift",
            "Facility": "Facility",
            "Select Facility": "Select Facility",
            "Production Line": "Production Line",
            "Select Facility First": "Select Facility First",
            "Select Line": "Select Line",
            "Main Category": "Main Category",
            "Select Main": "Select Main",
            "Sub Category": "Sub Category",
            "Select Main First": "Select Main First",
            "Time Range": "Time Range",
            "Associates (Crew)": "Associates (Crew)",
            "Duration": "Duration",
            "minutes": "minutes",
            "Comments / Additional Information": "Comments / Additional Information",
            "Enter any additional details about the downtime...": "Enter any additional details about the downtime...",
            "Quick Notes": "Quick Notes",
            "Parts": "Parts",
            "Maintenance": "Maintenance",
            "Quality": "Quality",
            "Changeover": "Changeover",
            "Clear": "Clear",
            "Submit Downtime": "Submit Downtime",
            "Update Entry": "Update Entry",
            "Downtime Reported!": "Downtime Reported!",
            "Entry Updated!": "Entry Updated!",
            "Report Another": "Report Another",
            "All Today's Entries for This Line": "All Today's Entries for This Line",
            "entries": "entries",
            "Edit": "Edit",
            "Delete": "Delete",
            
            # Admin Panel
            "System Administration": "System Administration",
            "Manage facilities, production lines, and view system audit logs": "Manage facilities, production lines, and view system audit logs",
            "Facilities": "Facilities",
            "Manage manufacturing facilities and locations": "Manage manufacturing facilities and locations",
            "Configure production lines for each facility": "Configure production lines for each facility",
            "Audit Log": "Audit Log",
            "View complete history of all system changes": "View complete history of all system changes",
            "Define and manage downtime categories": "Define and manage downtime categories",
            "Shift Management": "Shift Management",
            "Configure shift schedules and timing": "Configure shift schedules and timing",
            "User Management": "User Management",
            "View user activity and permissions": "View user activity and permissions",
            
            # Status messages
            "Language changed successfully": "Language changed successfully",
            "Invalid language selection": "Invalid language selection",
            "Session expired": "Your session has expired or you logged in from another location.",
            "You have been successfully logged out": "You have been successfully logged out",
            
            # Time
            "Today": "Today",
            "Yesterday": "Yesterday",
            "days ago": "days ago",
            "hour ago": "hour ago",
            "hours ago": "hours ago",
            "minute ago": "minute ago",
            "minutes ago": "minutes ago",
            "just now": "just now"
        }
    
    def get_default_es_translations(self):
        """Default Spanish translations"""
        return {
            # Common
            "Downtime Tracker": "Rastreador de Tiempo Muerto",
            "Dashboard": "Panel de Control",
            "Admin Panel": "Panel de Administración",
            "Logout": "Cerrar Sesión",
            "Login": "Iniciar Sesión",
            "Sign In": "Iniciar Sesión",
            "Welcome": "Bienvenido",
            "Language": "Idioma",
            
            # Login page
            "Username": "Usuario",
            "Password": "Contraseña",
            "Enter your AD username": "Ingrese su usuario de AD",
            "Enter your password": "Ingrese su contraseña",
            "Active Directory Authentication": "Autenticación de Active Directory",
            "Access Requirements": "Requisitos de Acceso",
            "You must be a member of": "Debe ser miembro de",
            "Submit downtime": "Registrar tiempo muerto",
            "Full access": "Acceso completo",
            "Invalid credentials": "Credenciales inválidas o acceso denegado",
            "Please enter both username and password": "Por favor ingrese usuario y contraseña",
            "Active Session Detected": "Sesión Activa Detectada",
            "You have an active session from another location": "Tiene una sesión activa desde otra ubicación",
            "Last Activity": "Última Actividad",
            "IP Address": "Dirección IP",
            "Continue and Sign In": "Continuar e Iniciar Sesión",
            "Cancel": "Cancelar",
            
            # Dashboard
            "Welcome, {name}!": "¡Bienvenido, {name}!",
            "Administrator": "Administrador",
            "User": "Usuario",
            "Email": "Correo Electrónico",
            "Access Level": "Nivel de Acceso",
            "Full Administrative Access": "Acceso Administrativo Completo",
            "Downtime Entry Only": "Solo Registro de Tiempo Muerto",
            "AD Groups": "Grupos de AD",
            "None": "Ninguno",
            "Active Facilities": "Instalaciones Activas",
            "Production Lines": "Líneas de Producción",
            "Downtime Events (7 days)": "Eventos de Tiempo Muerto (7 días)",
            "Downtime Categories": "Categorías de Tiempo Muerto",
            "Report Downtime": "Reportar Tiempo Muerto",
            "Record production downtime events": "Registrar eventos de tiempo muerto de producción",
            "View Reports": "Ver Reportes",
            "View downtime reports and analytics": "Ver reportes y análisis de tiempo muerto",
            "Manage facilities, lines, and settings": "Administrar instalaciones, líneas y configuraciones",
            "Sign out of your account": "Cerrar sesión de su cuenta",
            
            # Downtime Entry
            "Report Production Downtime": "Reportar Tiempo Muerto de Producción",
            "Edit Downtime Entry": "Editar Entrada de Tiempo Muerto",
            "Date/Time": "Fecha/Hora",
            "Shift": "Turno",
            "No Active Shift": "Sin Turno Activo",
            "Facility": "Instalación",
            "Select Facility": "Seleccionar Instalación",
            "Production Line": "Línea de Producción",
            "Select Facility First": "Seleccione Instalación Primero",
            "Select Line": "Seleccionar Línea",
            "Main Category": "Categoría Principal",
            "Select Main": "Seleccionar Principal",
            "Sub Category": "Subcategoría",
            "Select Main First": "Seleccione Principal Primero",
            "Time Range": "Rango de Tiempo",
            "Associates (Crew)": "Asociados (Equipo)",
            "Duration": "Duración",
            "minutes": "minutos",
            "Comments / Additional Information": "Comentarios / Información Adicional",
            "Enter any additional details about the downtime...": "Ingrese detalles adicionales sobre el tiempo muerto...",
            "Quick Notes": "Notas Rápidas",
            "Parts": "Partes",
            "Maintenance": "Mantenimiento",
            "Quality": "Calidad",
            "Changeover": "Cambio",
            "Clear": "Limpiar",
            "Submit Downtime": "Enviar Tiempo Muerto",
            "Update Entry": "Actualizar Entrada",
            "Downtime Reported!": "¡Tiempo Muerto Reportado!",
            "Entry Updated!": "¡Entrada Actualizada!",
            "Report Another": "Reportar Otro",
            "All Today's Entries for This Line": "Todas las Entradas de Hoy para Esta Línea",
            "entries": "entradas",
            "Edit": "Editar",
            "Delete": "Eliminar",
            
            # Admin Panel
            "System Administration": "Administración del Sistema",
            "Manage facilities, production lines, and view system audit logs": "Administrar instalaciones, líneas de producción y ver registros de auditoría",
            "Facilities": "Instalaciones",
            "Manage manufacturing facilities and locations": "Administrar instalaciones y ubicaciones de manufactura",
            "Configure production lines for each facility": "Configurar líneas de producción para cada instalación",
            "Audit Log": "Registro de Auditoría",
            "View complete history of all system changes": "Ver historial completo de todos los cambios del sistema",
            "Define and manage downtime categories": "Definir y administrar categorías de tiempo muerto",
            "Shift Management": "Gestión de Turnos",
            "Configure shift schedules and timing": "Configurar horarios y tiempos de turnos",
            "User Management": "Gestión de Usuarios",
            "View user activity and permissions": "Ver actividad y permisos de usuarios",
            
            # Status messages
            "Language changed successfully": "Idioma cambiado exitosamente",
            "Invalid language selection": "Selección de idioma inválida",
            "Session expired": "Su sesión ha expirado o inició sesión desde otra ubicación.",
            "You have been successfully logged out": "Ha cerrado sesión exitosamente",
            
            # Time
            "Today": "Hoy",
            "Yesterday": "Ayer",
            "days ago": "días atrás",
            "hour ago": "hora atrás",
            "hours ago": "horas atrás",
            "minute ago": "minuto atrás",
            "minutes ago": "minutos atrás",
            "just now": "ahora mismo"
        }

# Global instance
_translator = TranslationManager()

def _(text, **kwargs):
    """Translation function for templates and Python code"""
    translated = _translator.get(text)
    if kwargs:
        translated = translated.format(**kwargs)
    return translated

def set_language(lang):
    """Set the current language"""
    if lang in ['en', 'es']:
        session['language'] = lang
        return True
    return False

def get_current_language():
    """Get the current language"""
    return session.get('language', 'en')