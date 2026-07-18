"""
Compatibilite API - Delegue vers le nouveau moteur ecu_engine.

Ce fichier maintient les memes signatures que l'ancien moteur
pour que projects.py n'ait pas besoin d'etre modifie.
"""

from app.ecu_engine.engine import analyze_ecu_file, generate_modified_file

__all__ = ["analyze_ecu_file", "generate_modified_file"]
