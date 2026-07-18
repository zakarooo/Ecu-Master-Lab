"""
ECU Engine - Moteur d'analyse ECU professionnel modulaire.

Pipeline 10 couches :
 1. format_detector      - Detection du format fichier
 2. processor_identifier  - Identification du processeur
 3. memory_identifier     - Identification de la memoire
 4. info_extractor        - Extraction informations techniques
 5. signature_scanner     - Recherche signatures internes
 6. segment_analyzer      - Analyse segments memoire
 7. map_detector          - Detection cartographies
 8. checksum_engine       - Verification checksums
 9. cross_validator       - Validation croisee base PostgreSQL
10. report_generator      - Rapport explicable
"""

__version__ = "2.0.0"
__all__ = ["ECUEngine"]
