"""
Telegram notification service for ECU Master Lab.

Sends notifications for key events:
- File upload
- Analysis complete
- Modification applied
- Errors
"""

import logging
import os
from typing import Optional

log = logging.getLogger("ecu_engine.telegram")

_API = "https://api.telegram.org/bot{token}/sendMessage"


def _get_config():
    from app.core.config import settings
    token = settings.TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = settings.TELEGRAM_CHAT_ID or os.getenv("TELEGRAM_CHAT_ID", "")
    return token, chat_id


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send a message via Telegram bot."""
    token, chat_id = _get_config()
    if not token or not chat_id:
        log.debug("Telegram not configured, skipping notification")
        return False
    try:
        import urllib.request
        import urllib.parse
        url = _API.format(token=token)
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = resp.read()
            log.info("Telegram message sent successfully")
            return True
    except Exception as exc:
        log.warning("Telegram notification failed: %s", exc)
        return False


def notify_upload(filename: str, file_size: int, user: str = "unknown") -> bool:
    """Notify when a file is uploaded."""
    size_str = _format_size(file_size)
    text = (
        "<b>📁 Nouveau fichier uploadé</b>\n\n"
        "<b>Fichier :</b> <code>{filename}</code>\n"
        "<b>Taille :</b> {size}\n"
        "<b>Utilisateur :</b> {user}"
    ).format(filename=filename, size=size_str, user=user)
    return send_message(text)


def notify_analysis_complete(
    filename: str,
    ecu_model: str,
    confidence: float,
    maps_found: int,
    user: str = "unknown",
) -> bool:
    """Notify when analysis is complete."""
    conf_pct = int(confidence * 100)
    text = (
        "<b>✅ Analyse terminée</b>\n\n"
        "<b>Fichier :</b> <code>{filename}</code>\n"
        "<b>ECU détecté :</b> {ecu}\n"
        "<b>Confiance :</b> {conf}%\n"
        "<b>Cartes trouvées :</b> {maps}\n"
        "<b>Utilisateur :</b> {user}"
    ).format(
        filename=filename,
        ecu=ecu_model,
        conf=conf_pct,
        maps=maps_found,
        user=user,
    )
    return send_message(text)


def notify_modification_applied(
    filename: str,
    mods: list,
    checksum_ok: bool,
    user: str = "unknown",
) -> bool:
    """Notify when modifications are applied."""
    mods_str = ", ".join(mods[:5])
    if len(mods) > 5:
        mods_str += " +%d" % (len(mods) - 5)
    cs_icon = "✅" if checksum_ok else "⚠️"
    text = (
        "<b>🔧 Modifications appliquées</b>\n\n"
        "<b>Fichier :</b> <code>{filename}</code>\n"
        "<b>Modifs :</b> {mods}\n"
        "<b>Checksum :</b> {cs}\n"
        "<b>Utilisateur :</b> {user}"
    ).format(filename=filename, mods=mods_str, cs=cs_icon, user=user)
    return send_message(text)


def notify_error(context: str, error: str, user: str = "unknown") -> bool:
    """Notify on error."""
    text = (
        "<b>❌ Erreur</b>\n\n"
        "<b>Contexte :</b> {ctx}\n"
        "<b>Erreur :</b> <code>{err}</code>\n"
        "<b>Utilisateur :</b> {user}"
    ).format(ctx=context, err=error[:500], user=user)
    return send_message(text)


def notify_startup(app_name: str, version: str) -> bool:
    """Notify when the app starts."""
    text = (
        "<b>🚀 {app} v{ver}</b>\n"
        "Backend démarré avec succès"
    ).format(app=app_name, ver=version)
    return send_message(text)


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return "%d B" % size_bytes
    if size_bytes < 1024 * 1024:
        return "%.1f KB" % (size_bytes / 1024)
    if size_bytes < 1024 * 1024 * 1024:
        return "%.1f MB" % (size_bytes / (1024 * 1024))
    return "%.1f GB" % (size_bytes / (1024 * 1024 * 1024))
