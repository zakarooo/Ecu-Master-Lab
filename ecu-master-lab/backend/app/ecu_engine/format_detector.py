"""
Couche 1 : Detection automatique du format fichier.

Detecte BIN, Intel HEX, Motorola S19, S-Record, compresses, etc.
Calcule entropie, ratios de bytes, et estime le format reel.
"""

import logging
from typing import Tuple
from .models import FormatResult, FileFormat
from .utils import compute_entropy, find_ascii_strings

logger = logging.getLogger("ecu_engine.format")


def detect_format(data: bytes, file_name: str = "") -> FormatResult:
    result = FormatResult(file_size=len(data))

    if not data:
        result.format_type = FileFormat.EMPTY
        result.explanation = "Fichier vide (0 octet)"
        result.confidence = 100.0
        return result

    size = len(data)
    first_256 = data[:min(256, size)]

    # Ratios de base
    null_count = first_256.count(b'\x00')
    ff_count = first_256.count(b'\xFF')
    ascii_count = sum(1 for b in first_256 if 32 <= b < 127)

    result.null_ratio = null_count / len(first_256)
    result.ff_ratio = ff_count / len(first_256)
    result.ascii_ratio = ascii_count / len(first_256)
    result.entropy = compute_entropy(data[:min(65536, size)])

    # --- Test Intel HEX ---
    if data[0:1] == b':':
        lines = data.split(b'\n')
        valid_hex = 0
        for line in lines[:30]:
            line = line.strip()
            if line.startswith(b':') and len(line) >= 11:
                try:
                    byte_count = int(line[1:3], 16)
                    if byte_count >= 0 and byte_count < 256:
                        valid_hex += 1
                except ValueError:
                    pass
        if valid_hex >= 3:
            result.format_type = FileFormat.INTEL_HEX
            result.encoding = "ascii"
            result.confidence = min(95.0, 60.0 + valid_hex * 2)
            result.explanation = f"Intel HEX detecte ({valid_hex} lignes valides)"
            return result

    # --- Test Motorola S19/S-Record ---
    if data[0:2] in (b'S0', b'S1', b'S2', b'S3', b'S7', b'S8', b'S9'):
        lines = data.split(b'\n')
        valid_s = sum(1 for l in lines[:30]
                      if l.strip()[:1] in (b'S',) and len(l.strip()) >= 4)
        if valid_s >= 3:
            result.format_type = FileFormat.MOTOROLA_S19
            result.encoding = "ascii"
            result.confidence = min(95.0, 60.0 + valid_s * 2)
            result.explanation = f"Motorola S-Record detecte ({valid_s} lignes)"
            return result

    # --- Test GZIP ---
    if data[:2] == b'\x1F\x8B':
        result.format_type = FileFormat.COMPRESSED
        result.encoding = "gzip"
        result.confidence = 99.0
        result.explanation = "Fichier GZIP compresse"
        return result

    # --- Test ZIP ---
    if data[:2] == b'PK':
        result.format_type = FileFormat.COMPRESSED
        result.encoding = "zip"
        result.confidence = 99.0
        result.explanation = "Fichier ZIP detecte"
        return result

    # --- Test texte ASCII ---
    if result.ascii_ratio > 0.85:
        result.format_type = FileFormat.UNKNOWN
        result.encoding = "text_ascii"
        result.confidence = 70.0
        result.explanation = f"Fichier texte ASCII (ratio: {result.ascii_ratio:.0%})"
        result.warnings.append("Fichier texte non reconnu comme format ECU standard")
        return result

    # --- Binaire brut (le plus courant pour les dumps ECU) ---
    result.format_type = FileFormat.BINARY
    result.encoding = "binary"
    result.confidence = 85.0
    details = []
    if result.ff_ratio > 0.5:
        details.append(f"Remplissage 0xFF dominant ({result.ff_ratio:.0%})")
    if result.null_ratio > 0.5:
        details.append(f"Remplissage 0x00 dominant ({result.null_ratio:.0%})")
    if result.entropy > 0.7:
        details.append(f"Entropie elevee ({result.entropy:.2f})")
    elif result.entropy < 0.1:
        details.append(f"Entropie tres basse ({result.entropy:.2f}) - possible fichier vide ou chiffre")

    result.explanation = f"Binaire brut detecte ({size} octets)"
    if details:
        result.explanation += " - " + ", ".join(details)

    # Verifier extension
    if file_name:
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        ext_map = {
            "bin": "binary", "ori": "binary", "dat": "binary",
            "hex": "intel_hex", "s19": "motorola_s19", "srec": "motorola_s19",
            "frf": "binary", "mpc": "binary", "bdm": "binary",
            "ihex": "intel_hex", "mot": "motorola_s19",
        }
        if ext in ext_map:
            expected = ext_map[ext]
            if expected == result.encoding or expected == result.format_type.value:
                result.confidence = min(95.0, result.confidence + 10.0)
                result.explanation += f" (extension .{ext} confirme)"

    return result
