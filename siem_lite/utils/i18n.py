"""
Internationalization (i18n) module for SIEM Lite.

This module provides multi-language support for the SIEM Lite system,
including translations for user interfaces, reports, and messages.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Default language
DEFAULT_LANGUAGE = "en"

# Available languages
AVAILABLE_LANGUAGES = ["en", "es", "fr", "de", "pt"]

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # Dashboard
        "dashboard_title": "SIEM Lite - Security Dashboard",
        "dashboard_subtitle": "Security Information and Event Management System",
        "system_status": "System Status",
        "statistics": "Statistics",
        "alerts": "Security Alerts",
        "recent_alerts": "Recent Alerts",
        "alert_id": "ID",
        "timestamp": "Timestamp",
        "alert_type": "Alert Type",
        "source_ip": "Source IP",
        "details": "Details",
        "status_operational": "✅ System Operational",
        "status_warning": "⚠️ System Issues",
        "status_error": "❌ System Error",
        "total_alerts": "Total alerts",
        "alert_types": "Alert types",
        "unique_ips": "Unique IPs",
        "not_available": "❌ Not available",
        # API Messages
        "api_connection_error": "Error connecting to API",
        "api_stats_error": "Error getting statistics",
        "api_health_error": "Error checking API health",
        # Processing Messages
        "processing_start": "🚀 Starting log processing...",
        "loading_logs": "📖 Loading {count} log entries...",
        "parsing_progress": "📝 Parsed {current}/{total} entries",
        "parsing_complete": "✅ Successfully parsed {count} log entries",
        "log_file_not_found": "❌ Log file not found",
        "parsing_error": "❌ Error parsing logs",
        "no_valid_logs": "❌ No valid log entries could be parsed",
        # Alert Messages
        "ssh_bruteforce_detected": "🚨 SSH Brute-Force detected from {ip}",
        "web_attack_detected": "🚨 Web attack detected from {ip}",
        "alert_sent": "📤 Alert sent to API",
        "alert_send_error": "❌ Error sending alert to API",
        "alerts_sent": "📤 {sent}/{total} alerts sent to API",
        # Report Messages
        "report_generated": "📄 Report generated",
        "report_error": "❌ Error generating report",
        "latex_report_generated": "📄 LaTeX report generated",
        "json_report_generated": "📄 JSON report generated",
        # Chart Messages
        "generating_plots": "📊 Generating plots...",
        "plot_saved": "📈 Plot saved",
        "plot_error": "❌ Error generating plot",
        # Database Messages
        "db_connected": "✅ Database connected",
        "db_connection_error": "❌ Database connection error",
        "db_query_error": "❌ Database query error",
        # Log Messages
        "log_generation_start": "📝 Starting log generation...",
        "log_generation_complete": "✅ Log generation complete",
        "log_generation_error": "❌ Error generating logs",
        # CLI Messages
        "cli_welcome": "Welcome to SIEM Lite CLI Dashboard",
        "cli_exit": "Press Ctrl+C to exit",
        "cli_refresh": "Refreshing dashboard...",
        "cli_error": "An error occurred",
        # Feature Messages
        "feature_enabled": "✅ Feature enabled",
        "feature_disabled": "❌ Feature disabled",
        "feature_not_available": "⚠️ Feature not available",
        # Time Formats
        "time_format": "%Y-%m-%d %H:%M:%S",
        "date_format": "%Y-%m-%d",
        # Alert Types
        "alert_ssh_bruteforce": "SSH Brute-Force Attempt",
        "alert_web_attack": "Web Attack",
        "alert_suspicious_activity": "Suspicious Activity",
        "alert_failed_login": "Failed Login",
        "alert_unauthorized_access": "Unauthorized Access",
        # Status Messages
        "status_healthy": "healthy",
        "status_unhealthy": "unhealthy",
        "status_unknown": "unknown",
        "status_connected": "connected",
        "status_disconnected": "disconnected",
        # Error Messages
        "error_generic": "An error occurred",
        "error_timeout": "Request timeout",
        "error_network": "Network error",
        "error_permission": "Permission denied",
        "error_not_found": "Resource not found",
        # Success Messages
        "success_operation": "Operation completed successfully",
        "success_saved": "Data saved successfully",
        "success_updated": "Data updated successfully",
        "success_deleted": "Data deleted successfully",
    },
    "es": {
        # Dashboard
        "dashboard_title": "SIEM Lite - Panel de Seguridad",
        "dashboard_subtitle": "Sistema de Gestión de Información y Eventos de Seguridad",
        "system_status": "Estado del Sistema",
        "statistics": "Estadísticas",
        "alerts": "Alertas de Seguridad",
        "recent_alerts": "Alertas Recientes",
        "alert_id": "ID",
        "timestamp": "Marca de Tiempo",
        "alert_type": "Tipo de Alerta",
        "source_ip": "IP de Origen",
        "details": "Detalles",
        "status_operational": "✅ Sistema Operativo",
        "status_warning": "⚠️ Problemas del Sistema",
        "status_error": "❌ Error del Sistema",
        "total_alerts": "Total de alertas",
        "alert_types": "Tipos de alerta",
        "unique_ips": "IPs únicas",
        "not_available": "❌ No disponible",
        # API Messages
        "api_connection_error": "Error conectando a la API",
        "api_stats_error": "Error obteniendo estadísticas",
        "api_health_error": "Error verificando salud de la API",
        # Processing Messages
        "processing_start": "🚀 Iniciando procesamiento de logs...",
        "loading_logs": "📖 Cargando {count} entradas de log...",
        "parsing_progress": "📝 Analizadas {current}/{total} entradas",
        "parsing_complete": "✅ Analizadas exitosamente {count} entradas de log",
        "log_file_not_found": "❌ Archivo de log no encontrado",
        "parsing_error": "❌ Error analizando logs",
        "no_valid_logs": "❌ No se pudieron analizar entradas de log válidas",
        # Alert Messages
        "ssh_bruteforce_detected": "🚨 Ataque de fuerza bruta SSH detectado desde {ip}",
        "web_attack_detected": "🚨 Ataque web detectado desde {ip}",
        "alert_sent": "📤 Alerta enviada a la API",
        "alert_send_error": "❌ Error enviando alerta a la API",
        "alerts_sent": "📤 {sent}/{total} alertas enviadas a la API",
        # Report Messages
        "report_generated": "📄 Reporte generado",
        "report_error": "❌ Error generando reporte",
        "latex_report_generated": "📄 Reporte LaTeX generado",
        "json_report_generated": "📄 Reporte JSON generado",
        # Chart Messages
        "generating_plots": "📊 Generando gráficos...",
        "plot_saved": "📈 Gráfico guardado",
        "plot_error": "❌ Error generando gráfico",
        # Database Messages
        "db_connected": "✅ Base de datos conectada",
        "db_connection_error": "❌ Error de conexión a la base de datos",
        "db_query_error": "❌ Error en consulta de base de datos",
        # Log Messages
        "log_generation_start": "📝 Iniciando generación de logs...",
        "log_generation_complete": "✅ Generación de logs completa",
        "log_generation_error": "❌ Error generando logs",
        # CLI Messages
        "cli_welcome": "Bienvenido al Panel CLI de SIEM Lite",
        "cli_exit": "Presiona Ctrl+C para salir",
        "cli_refresh": "Actualizando panel...",
        "cli_error": "Ocurrió un error",
        # Feature Messages
        "feature_enabled": "✅ Función habilitada",
        "feature_disabled": "❌ Función deshabilitada",
        "feature_not_available": "⚠️ Función no disponible",
        # Time Formats
        "time_format": "%Y-%m-%d %H:%M:%S",
        "date_format": "%Y-%m-%d",
        # Alert Types
        "alert_ssh_bruteforce": "Intento de Fuerza Bruta SSH",
        "alert_web_attack": "Ataque Web",
        "alert_suspicious_activity": "Actividad Sospechosa",
        "alert_failed_login": "Inicio de Sesión Fallido",
        "alert_unauthorized_access": "Acceso No Autorizado",
        # Status Messages
        "status_healthy": "saludable",
        "status_unhealthy": "no saludable",
        "status_unknown": "desconocido",
        "status_connected": "conectado",
        "status_disconnected": "desconectado",
        # Error Messages
        "error_generic": "Ocurrió un error",
        "error_timeout": "Tiempo de espera agotado",
        "error_network": "Error de red",
        "error_permission": "Permiso denegado",
        "error_not_found": "Recurso no encontrado",
        # Success Messages
        "success_operation": "Operación completada exitosamente",
        "success_saved": "Datos guardados exitosamente",
        "success_updated": "Datos actualizados exitosamente",
        "success_deleted": "Datos eliminados exitosamente",
    },
    "fr": {
        # Tableau de bord
        "dashboard_title": "SIEM Lite - Tableau de bord de sécurité",
        "dashboard_subtitle": "Système de gestion des informations et des événements de sécurité",
        "system_status": "État du système",
        "statistics": "Statistiques",
        "alerts": "Alertes de sécurité",
        "recent_alerts": "Alertes récentes",
        "alert_id": "ID",
        "timestamp": "Horodatage",
        "alert_type": "Type d'alerte",
        "source_ip": "IP source",
        "details": "Détails",
        "status_operational": "✅ Système opérationnel",
        "status_warning": "⚠️ Problèmes système",
        "status_error": "❌ Erreur système",
        "total_alerts": "Nombre total d'alertes",
        "alert_types": "Types d'alerte",
        "unique_ips": "IPs uniques",
        "not_available": "❌ Non disponible",
        # Messages API
        "api_connection_error": "Erreur de connexion à l'API",
        "api_stats_error": "Erreur lors de l'obtention des statistiques",
        "api_health_error": "Erreur lors de la vérification de la santé de l'API",
        # Traitement
        "processing_start": "🚀 Démarrage du traitement des journaux...",
        "loading_logs": "📖 Chargement de {count} entrées de journal...",
        "parsing_progress": "📝 {current}/{total} entrées analysées",
        "parsing_complete": "✅ {count} entrées de journal analysées avec succès",
        "log_file_not_found": "❌ Fichier journal introuvable",
        "parsing_error": "❌ Erreur lors de l'analyse des journaux",
        "no_valid_logs": "❌ Aucune entrée de journal valide n'a pu être analysée",
        # Alertes
        "ssh_bruteforce_detected": "🚨 Attaque par force brute SSH détectée depuis {ip}",
        "web_attack_detected": "🚨 Attaque web détectée depuis {ip}",
        "alert_sent": "📤 Alerte envoyée à l'API",
        "alert_send_error": "❌ Erreur lors de l'envoi de l'alerte à l'API",
        "alerts_sent": "📤 {sent}/{total} alertes envoyées à l'API",
        # Rapports
        "report_generated": "📄 Rapport généré",
        "report_error": "❌ Erreur lors de la génération du rapport",
        "latex_report_generated": "📄 Rapport LaTeX généré",
        "json_report_generated": "📄 Rapport JSON généré",
        # Graphiques
        "generating_plots": "📊 Génération des graphiques...",
        "plot_saved": "📈 Graphique enregistré",
        "plot_error": "❌ Erreur lors de la génération du graphique",
        # Base de données
        "db_connected": "✅ Base de données connectée",
        "db_connection_error": "❌ Erreur de connexion à la base de données",
        "db_query_error": "❌ Erreur de requête à la base de données",
        # Journaux
        "log_generation_start": "📝 Démarrage de la génération des journaux...",
        "log_generation_complete": "✅ Génération des journaux terminée",
        "log_generation_error": "❌ Erreur lors de la génération des journaux",
        # CLI
        "cli_welcome": "Bienvenue sur le tableau de bord CLI de SIEM Lite",
        "cli_exit": "Appuyez sur Ctrl+C pour quitter",
        "cli_refresh": "Actualisation du tableau de bord...",
        "cli_error": "Une erreur est survenue",
        # Fonctionnalités
        "feature_enabled": "✅ Fonction activée",
        "feature_disabled": "❌ Fonction désactivée",
        "feature_not_available": "⚠️ Fonction non disponible",
        # Formats de temps
        "time_format": "%Y-%m-%d %H:%M:%S",
        "date_format": "%Y-%m-%d",
        # Types d'alerte
        "alert_ssh_bruteforce": "Tentative de force brute SSH",
        "alert_web_attack": "Attaque Web",
        "alert_suspicious_activity": "Activité suspecte",
        "alert_failed_login": "Échec de connexion",
        "alert_unauthorized_access": "Accès non autorisé",
        # Statuts
        "status_healthy": "opérationnel",
        "status_unhealthy": "non opérationnel",
        "status_unknown": "inconnu",
        "status_connected": "connecté",
        "status_disconnected": "déconnecté",
        # Erreurs
        "error_generic": "Une erreur est survenue",
        "error_timeout": "Délai d'attente dépassé",
        "error_network": "Erreur réseau",
        "error_permission": "Permission refusée",
        "error_not_found": "Ressource non trouvée",
        # Succès
        "success_operation": "Opération réussie",
        "success_saved": "Données enregistrées avec succès",
        "success_updated": "Données mises à jour avec succès",
        "success_deleted": "Données supprimées avec succès",
        # Menu
        "setup": "Configurer l'environnement",
        "monitor": "Surveillance (temps réel)",
        "analyze_threats": "Analyser les menaces",
        "export": "Exporter les données",
        "change_language": "Changer de langue",
        "exit": "Quitter",
    },
    "de": {
        # Dashboard
        "dashboard_title": "SIEM Lite - Sicherheits-Dashboard",
        "dashboard_subtitle": "System zur Verwaltung von Sicherheitsinformationen und -ereignissen",
        "system_status": "Systemstatus",
        "statistics": "Statistiken",
        "alerts": "Sicherheitswarnungen",
        "recent_alerts": "Aktuelle Warnungen",
        "alert_id": "ID",
        "timestamp": "Zeitstempel",
        "alert_type": "Alarmtyp",
        "source_ip": "Quell-IP",
        "details": "Details",
        "status_operational": "✅ System betriebsbereit",
        "status_warning": "⚠️ Systemprobleme",
        "status_error": "❌ Systemfehler",
        "total_alerts": "Gesamtanzahl Warnungen",
        "alert_types": "Alarmtypen",
        "unique_ips": "Eindeutige IPs",
        "not_available": "❌ Nicht verfügbar",
        # API
        "api_connection_error": "Fehler bei der Verbindung zur API",
        "api_stats_error": "Fehler beim Abrufen der Statistiken",
        "api_health_error": "Fehler bei der Überprüfung des API-Status",
        # Verarbeitung
        "processing_start": "🚀 Log-Verarbeitung wird gestartet...",
        "loading_logs": "📖 Lade {count} Log-Einträge...",
        "parsing_progress": "📝 {current}/{total} Einträge analysiert",
        "parsing_complete": "✅ {count} Log-Einträge erfolgreich analysiert",
        "log_file_not_found": "❌ Logdatei nicht gefunden",
        "parsing_error": "❌ Fehler beim Analysieren der Logs",
        "no_valid_logs": "❌ Keine gültigen Log-Einträge konnten analysiert werden",
        # Warnungen
        "ssh_bruteforce_detected": "🚨 SSH-Brute-Force-Angriff erkannt von {ip}",
        "web_attack_detected": "🚨 Webangriff erkannt von {ip}",
        "alert_sent": "📤 Warnung an API gesendet",
        "alert_send_error": "❌ Fehler beim Senden der Warnung an die API",
        "alerts_sent": "📤 {sent}/{total} Warnungen an die API gesendet",
        # Berichte
        "report_generated": "📄 Bericht erstellt",
        "report_error": "❌ Fehler beim Erstellen des Berichts",
        "latex_report_generated": "📄 LaTeX-Bericht erstellt",
        "json_report_generated": "📄 JSON-Bericht erstellt",
        # Diagramme
        "generating_plots": "📊 Diagramme werden erstellt...",
        "plot_saved": "📈 Diagramm gespeichert",
        "plot_error": "❌ Fehler beim Erstellen des Diagramms",
        # Datenbank
        "db_connected": "✅ Datenbank verbunden",
        "db_connection_error": "❌ Fehler bei der Datenbankverbindung",
        "db_query_error": "❌ Fehler bei der Datenbankabfrage",
        # Logs
        "log_generation_start": "📝 Log-Erstellung wird gestartet...",
        "log_generation_complete": "✅ Log-Erstellung abgeschlossen",
        "log_generation_error": "❌ Fehler bei der Log-Erstellung",
        # CLI
        "cli_welcome": "Willkommen beim SIEM Lite CLI-Dashboard",
        "cli_exit": "Drücken Sie Strg+C zum Beenden",
        "cli_refresh": "Dashboard wird aktualisiert...",
        "cli_error": "Ein Fehler ist aufgetreten",
        # Features
        "feature_enabled": "✅ Funktion aktiviert",
        "feature_disabled": "❌ Funktion deaktiviert",
        "feature_not_available": "⚠️ Funktion nicht verfügbar",
        # Zeitformate
        "time_format": "%Y-%m-%d %H:%M:%S",
        "date_format": "%Y-%m-%d",
        # Alarmtypen
        "alert_ssh_bruteforce": "SSH-Brute-Force-Versuch",
        "alert_web_attack": "Webangriff",
        "alert_suspicious_activity": "Verdächtige Aktivität",
        "alert_failed_login": "Fehlgeschlagene Anmeldung",
        "alert_unauthorized_access": "Unbefugter Zugriff",
        # Status
        "status_healthy": "betriebsbereit",
        "status_unhealthy": "nicht betriebsbereit",
        "status_unknown": "unbekannt",
        "status_connected": "verbunden",
        "status_disconnected": "getrennt",
        # Fehler
        "error_generic": "Ein Fehler ist aufgetreten",
        "error_timeout": "Zeitüberschreitung",
        "error_network": "Netzwerkfehler",
        "error_permission": "Zugriff verweigert",
        "error_not_found": "Ressource nicht gefunden",
        # Erfolg
        "success_operation": "Vorgang erfolgreich abgeschlossen",
        "success_saved": "Daten erfolgreich gespeichert",
        "success_updated": "Daten erfolgreich aktualisiert",
        "success_deleted": "Daten erfolgreich gelöscht",
        # Menü
        "setup": "Umgebung einrichten",
        "monitor": "Überwachung (Echtzeit)",
        "analyze_threats": "Bedrohungen analysieren",
        "export": "Daten exportieren",
        "change_language": "Sprache ändern",
        "exit": "Beenden",
    },
    "pt": {
        # Painel
        "dashboard_title": "SIEM Lite - Painel de Segurança",
        "dashboard_subtitle": "Sistema de Gerenciamento de Informações e Eventos de Segurança",
        "system_status": "Status do Sistema",
        "statistics": "Estatísticas",
        "alerts": "Alertas de Segurança",
        "recent_alerts": "Alertas Recentes",
        "alert_id": "ID",
        "timestamp": "Data/Hora",
        "alert_type": "Tipo de Alerta",
        "source_ip": "IP de Origem",
        "details": "Detalhes",
        "status_operational": "✅ Sistema operacional",
        "status_warning": "⚠️ Problemas no sistema",
        "status_error": "❌ Erro no sistema",
        "total_alerts": "Total de alertas",
        "alert_types": "Tipos de alerta",
        "unique_ips": "IPs únicas",
        "not_available": "❌ Não disponível",
        # API
        "api_connection_error": "Erro ao conectar à API",
        "api_stats_error": "Erro ao obter estatísticas",
        "api_health_error": "Erro ao verificar o status da API",
        # Processamento
        "processing_start": "🚀 Iniciando o processamento dos logs...",
        "loading_logs": "📖 Carregando {count} entradas de log...",
        "parsing_progress": "📝 {current}/{total} entradas analisadas",
        "parsing_complete": "✅ {count} entradas de log analisadas com sucesso",
        "log_file_not_found": "❌ Arquivo de log não encontrado",
        "parsing_error": "❌ Erro ao analisar os logs",
        "no_valid_logs": "❌ Nenhuma entrada de log válida pôde ser analisada",
        # Alertas
        "ssh_bruteforce_detected": "🚨 Ataque de força bruta SSH detectado de {ip}",
        "web_attack_detected": "🚨 Ataque web detectado de {ip}",
        "alert_sent": "📤 Alerta enviado para a API",
        "alert_send_error": "❌ Erro ao enviar alerta para a API",
        "alerts_sent": "📤 {sent}/{total} alertas enviados para a API",
        # Relatórios
        "report_generated": "📄 Relatório gerado",
        "report_error": "❌ Erro ao gerar relatório",
        "latex_report_generated": "📄 Relatório LaTeX gerado",
        "json_report_generated": "📄 Relatório JSON gerado",
        # Gráficos
        "generating_plots": "📊 Gerando gráficos...",
        "plot_saved": "📈 Gráfico salvo",
        "plot_error": "❌ Erro ao gerar gráfico",
        # Banco de dados
        "db_connected": "✅ Banco de dados conectado",
        "db_connection_error": "❌ Erro de conexão com o banco de dados",
        "db_query_error": "❌ Erro na consulta ao banco de dados",
        # Logs
        "log_generation_start": "📝 Iniciando a geração de logs...",
        "log_generation_complete": "✅ Geração de logs concluída",
        "log_generation_error": "❌ Erro ao gerar logs",
        # CLI
        "cli_welcome": "Bem-vindo ao Painel CLI do SIEM Lite",
        "cli_exit": "Pressione Ctrl+C para sair",
        "cli_refresh": "Atualizando painel...",
        "cli_error": "Ocorreu um erro",
        # Funcionalidades
        "feature_enabled": "✅ Funcionalidade ativada",
        "feature_disabled": "❌ Funcionalidade desativada",
        "feature_not_available": "⚠️ Funcionalidade não disponível",
        # Formatos de tempo
        "time_format": "%Y-%m-%d %H:%M:%S",
        "date_format": "%Y-%m-%d",
        # Tipos de alerta
        "alert_ssh_bruteforce": "Tentativa de força bruta SSH",
        "alert_web_attack": "Ataque Web",
        "alert_suspicious_activity": "Atividade suspeita",
        "alert_failed_login": "Falha no login",
        "alert_unauthorized_access": "Acesso não autorizado",
        # Status
        "status_healthy": "operacional",
        "status_unhealthy": "não operacional",
        "status_unknown": "desconhecido",
        "status_connected": "conectado",
        "status_disconnected": "desconectado",
        # Erros
        "error_generic": "Ocorreu um erro",
        "error_timeout": "Tempo de solicitação esgotado",
        "error_network": "Erro de rede",
        "error_permission": "Permissão negada",
        "error_not_found": "Recurso não encontrado",
        # Sucesso
        "success_operation": "Operação concluída com sucesso",
        "success_saved": "Dados salvos com sucesso",
        "success_updated": "Dados atualizados com sucesso",
        "success_deleted": "Dados excluídos com sucesso",
        # Menu
        "setup": "Configurar ambiente",
        "monitor": "Monitoramento (tempo real)",
        "analyze_threats": "Analisar ameaças",
        "export": "Exportar dados",
        "change_language": "Mudar idioma",
        "exit": "Sair",
    },
}


class I18nManager:
    """
    Internationalization manager for SIEM Lite.

    This class handles multi-language support for the entire system,
    including user interfaces, reports, and system messages.
    """

    def __init__(self, language: str = DEFAULT_LANGUAGE):
        """
        Initialize the i18n manager.

        Args:
            language (str): Language code (en, es, fr, de, pt)
        """
        self.language = language
        self.translations = TRANSLATIONS.get(language, TRANSLATIONS["en"])

    def get(self, key: str, default: str = None, **kwargs) -> str:
        """
        Get a translated string.

        Args:
            key (str): Translation key
            default (str): Default value if key not found
            **kwargs: Format parameters

        Returns:
            str: Translated string
        """
        translation = self.translations.get(key, default or key)

        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation

        return translation

    def set_language(self, language: str) -> None:
        """
        Change the current language.

        Args:
            language (str): New language code
        """
        if language in AVAILABLE_LANGUAGES:
            self.language = language
            self.translations = TRANSLATIONS.get(language, TRANSLATIONS["en"])
        else:
            raise ValueError(f"Unsupported language: {language}")

    def get_available_languages(self) -> list:
        """
        Get list of available languages.

        Returns:
            list: List of available language codes
        """
        return AVAILABLE_LANGUAGES.copy()

    def get_language_name(self, language_code: str) -> str:
        """
        Get the display name for a language code.

        Args:
            language_code (str): Language code

        Returns:
            str: Language display name
        """
        language_names = {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "pt": "Português",
        }
        return language_names.get(language_code, language_code)

    def format_time(self, timestamp: Any) -> str:
        """
        Format timestamp according to current language.

        Args:
            timestamp: Timestamp to format

        Returns:
            str: Formatted timestamp
        """
        time_format = self.get("time_format", "%Y-%m-%d %H:%M:%S")

        if isinstance(timestamp, str):
            return timestamp
        elif hasattr(timestamp, "strftime"):
            return timestamp.strftime(time_format)
        else:
            return str(timestamp)

    def format_number(self, number: int) -> str:
        """
        Format number with thousands separator.

        Args:
            number (int): Number to format

        Returns:
            str: Formatted number
        """
        return f"{number:,}"

    def get_alert_type_name(self, alert_type: str) -> str:
        """
        Get translated alert type name.

        Args:
            alert_type (str): Alert type key

        Returns:
            str: Translated alert type name
        """
        return self.get(f"alert_{alert_type.lower().replace(' ', '_')}", alert_type)

    def get_status_message(self, status: str) -> str:
        """
        Get translated status message.

        Args:
            status (str): Status key

        Returns:
            str: Translated status message
        """
        return self.get(f"status_{status.lower()}", status)


# Global i18n instance
i18n = I18nManager()


def t(key: str, default: str = None, **kwargs) -> str:
    """
    Convenience function to get translated string.

    Args:
        key (str): Translation key
        default (str): Default value if key not found
        **kwargs: Format parameters

    Returns:
        str: Translated string
    """
    return i18n.get(key, default, **kwargs)


def set_language(language: str) -> None:
    """
    Set the global language.

    Args:
        language (str): Language code
    """
    i18n.set_language(language)


def get_available_languages() -> list:
    """
    Get available languages.

    Returns:
        list: List of available language codes
    """
    return i18n.get_available_languages()


def main() -> None:
    """Test function for the i18n module."""
    # Test different languages
    test_keys = ["dashboard_title", "system_status", "total_alerts"]

    for lang in ["en", "es"]:
        print(f"\n=== Language: {lang} ===")
        i18n.set_language(lang)
        for key in test_keys:
            print(f"{key}: {i18n.get(key)}")


if __name__ == "__main__":
    main()
