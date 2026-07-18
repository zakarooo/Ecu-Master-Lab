"""
Tests complets du moteur ECU Engine v2.
Tests unitaires par couche + tests d'integration pipeline complet.
"""
import asyncio
import struct
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

passed = 0
failed = 0
total_time = 0.0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name} - {detail}")


# ==============================================================
#  FICHIERS SYNTHETIQUES
# ==============================================================

def create_bosch_edc17c64():
    size = 1048576
    data = bytearray(b'\xFF' * size)
    data[0x200:0x205] = b'Bosch'
    data[0x100:0x108] = b'EDC17C64'
    data[0x110:0x11A] = b'1037356247'
    data[0x120:0x130] = b'0 281 030 647'
    for offset in [0x2A000, 0x2B000, 0x2C000, 0x2D000, 0x2E000]:
        for i in range(0, 0x400, 2):
            val = ((offset + i) * 7 + 13) % 1000
            struct.pack_into("<H", data, offset + i, val)
    data[0x1FFC:0x2000] = b'\xAA\xBB\xCC\xDD'
    return bytes(data)


def create_delphi_dcm37():
    size = 524288
    data = bytearray(b'\xFF' * size)
    data[0:6] = b'Delphi'
    data[0x100:0x106] = b'DCM3.7'
    data[0x110:0x11A] = b'1037347844'
    for offset in [0x10000, 0x11000, 0x12000, 0x13000]:
        for i in range(0, 0x200, 2):
            struct.pack_into("<H", data, offset + i, (offset + i) % 500)
    return bytes(data)


def create_siemens_simos181():
    size = 1048576
    data = bytearray(b'\xFF' * size)
    data[0x200:0x208] = b'Siemens'
    data[0x100:0x10C] = b'Simos 18.1'
    data[0x110:0x11A] = b'5850765000'
    for offset in [0x20000, 0x21000, 0x22000, 0x23000]:
        for i in range(0, 0x400, 2):
            struct.pack_into("<H", data, offset + i, ((offset + i) * 3) % 600)
    return bytes(data)


def create_intel_hex():
    lines = []
    for addr in range(0, 0x1000, 16):
        hex_data = ''.join(f'{(addr + i) & 0xFF:02X}' for i in range(16))
        checksum = (~sum(int(hex_data[i:i+2], 16) for i in range(0, 32, 2)) + 1) & 0xFF
        line = f':10{addr:04X}00{hex_data}{checksum:02X}'
        lines.append(line)
    lines.append(':00000001FF')
    return '\n'.join(lines).encode('ascii')


def create_empty_file():
    return b''


def create_text_file():
    return b'This is just a text file with no ECU data.\n' * 100


# ==============================================================
#  TESTS UNITAIRES - COUCHE 1 : FORMAT
# ==============================================================

def test_format_detector():
    from app.ecu_engine.format_detector import detect_format
    from app.ecu_engine.models import FileFormat

    print("\n--- Test Format Detector ---")

    r = detect_format(create_bosch_edc17c64(), "test.bin")
    test("BIN detecte", r.format_type == FileFormat.BINARY)
    test("Confiance > 70", r.confidence > 70, f"{r.confidence}")
    test("Taille > 0", r.file_size > 0, f"{r.file_size}")

    r2 = detect_format(create_intel_hex(), "test.hex")
    test("Intel HEX detecte", r2.format_type == FileFormat.INTEL_HEX)

    r3 = detect_format(create_empty_file(), "empty.bin")
    test("Fichier vide detecte", r3.format_type == FileFormat.EMPTY)

    r4 = detect_format(create_text_file(), "test.txt")
    test("Texte detecte", r4.format_type == FileFormat.UNKNOWN)

    r5 = detect_format(create_bosch_edc17c64(), "test.bin")
    test("Extension confirme", r5.confidence >= 85)


# ==============================================================
#  TESTS UNITAIRES - COUCHE 2 : PROCESSEUR
# ==============================================================

def test_processor_identifier():
    from app.ecu_engine.processor_identifier import identify_processor

    print("\n--- Test Processor Identifier ---")

    r = identify_processor(create_bosch_edc17c64())
    test("Processeur detecte", r.detected)
    test("Confiance > 0", r.confidence > 0, f"{r.confidence}")
    if r.primary:
        test("Famille detectee", r.primary.family.value != "unknown")
        test("Evidence non vide", len(r.evidence) > 0)

    r2 = identify_processor(create_delphi_dcm37())
    test("Delphi processeur", r2.detected)
    test("Delphi confiance > 0", r2.confidence > 0)


# ==============================================================
#  TESTS UNITAIRES - COUCHE 3 : MEMOIRE
# ==============================================================

def test_memory_identifier():
    from app.ecu_engine.memory_identifier import identify_memory

    print("\n--- Test Memory Identifier ---")

    r = identify_memory(create_bosch_edc17c64())
    test("Layout genere", r is not None)
    test("Taille totale > 0", r.total_size > 0)
    test("Regions detectees", len(r.regions) > 0)
    test("Confiance > 0", r.confidence > 0, f"{r.confidence}")


# ==============================================================
#  TESTS UNITAIRES - COUCHE 4 : EXTRACTION INFOS
# ==============================================================

def test_info_extractor():
    from app.ecu_engine.info_extractor import extract_technical_info

    print("\n--- Test Info Extractor ---")

    r = extract_technical_info(create_bosch_edc17c64())
    test("HW Number trouve", r.hw_number != "", r.hw_number)
    test("Evidence non vide", len(r.evidence) > 0)
    test("Confiance > 0", r.confidence > 0, f"{r.confidence}")

    r2 = extract_technical_info(create_delphi_dcm37())
    test("Delphi HW trouve", r2.hw_number != "", r2.hw_number)


# ==============================================================
#  TESTS UNITAIRES - COUCHE 5 : SIGNATURES
# ==============================================================

def test_signature_scanner():
    from app.ecu_engine.signature_scanner import scan_signatures

    print("\n--- Test Signature Scanner ---")

    r = scan_signatures(create_bosch_edc17c64())
    test("Scan genere", r is not None)
    test("Confiance >= 0", r.confidence >= 0, f"{r.confidence}")
    test("Signatures liste", isinstance(r.signatures, list))

    r2 = scan_signatures(create_empty_file())
    test("Empty pas de crash", r2 is not None)
    test("Empty confiance 0", r2.confidence == 0)


# ==============================================================
#  TESTS UNITAIRES - COUCHE 6 : SEGMENTS
# ==============================================================

def test_segment_analyzer():
    from app.ecu_engine.segment_analyzer import analyze_segments

    print("\n--- Test Segment Analyzer ---")

    r = analyze_segments(create_bosch_edc17c64())
    test("Segments analyses", r is not None)
    test("Segments trouves", len(r.segments) > 0)
    test("Coherence >= 0", r.coherence_score >= 0, f"{r.coherence_score}")


# ==============================================================
#  TESTS UNITAIRES - COUCHE 7 : CARTOGRAPHIES
# ==============================================================

def test_map_detector():
    from app.ecu_engine.map_detector import detect_maps

    print("\n--- Test Map Detector ---")

    r = detect_maps(create_bosch_edc17c64(), 0x20000, 0x20000)
    test("Maps detectees", r is not None)
    test("Confiance >= 0", r.confidence >= 0, f"{r.confidence}")

    r2 = detect_maps(create_empty_file())
    test("Empty pas de crash", r2 is not None)
    test("Empty 0 maps", r2.total_maps_found == 0)


# ==============================================================
#  TESTS UNITAIRES - COUCHE 8 : CHECKSUM
# ==============================================================

def test_checksum_engine():
    from app.ecu_engine.checksum_engine import (
        _crc16_ccitt, _crc32_standard, _crc32_bosch,
        _sum8, _sum16, _xor16, verify_checksum, auto_detect_checksum
    )

    print("\n--- Test Checksum Engine ---")

    data = b'123456789'
    test("CRC16 CCITT", _crc16_ccitt(data) == 0x29B1)
    test("CRC32 standard", _crc32_standard(data) == 0xCBF43926)
    test("CRC16 deterministe", _crc16_ccitt(data) == _crc16_ccitt(data))
    test("CRC32 deterministe", _crc32_bosch(data) == _crc32_bosch(data))
    test("Sum8 non-nul", _sum8(data) != 0)
    test("Sum16 non-nul", _sum16(data) != 0)

    r = verify_checksum(create_bosch_edc17c64(), "bosch_edc17", 0x1FFC, 4, 0, 0x1FFB)
    test("Checksum result", r is not None)

    r2 = auto_detect_checksum(create_bosch_edc17c64(), "EDC17C64")
    test("Auto detect result", r2 is not None)


# ==============================================================
#  TESTS UNITAIRES - COUCHE 9 : VALIDATION CROISEE
# ==============================================================

def test_cross_validator():
    from app.ecu_engine.cross_validator import cross_validate
    from app.ecu_engine.models import (
        FormatResult, ProcessorResult, TechnicalInfo,
        SignatureScanResult, MemoryLayout, MapDetectionResult, FileFormat
    )

    print("\n--- Test Cross Validator ---")

    fmt = FormatResult(file_size=1048576, format_type=FileFormat.BINARY)
    proc = ProcessorResult(detected=True, confidence=80.0)
    tech = TechnicalInfo(hw_number="EDC17C64", sw_number="1037356247", confidence=90.0)
    sig = SignatureScanResult(confidence=50.0)
    mem = MemoryLayout(total_size=1048576, confidence=60.0)
    maps = MapDetectionResult(total_maps_found=5, confidence=70.0)
    cs = []

    r = cross_validate(create_bosch_edc17c64(), fmt, proc, tech, sig, mem, maps, cs)
    test("Cross-validation genere", r is not None)
    test("Hypotheses >= 1", len(r.hypotheses) > 0, f"{len(r.hypotheses)}")
    if r.best_hypothesis:
        test("Best score > 0", r.best_hypothesis.confidence > 0, f"{r.best_hypothesis.confidence}")


# ==============================================================
#  TESTS INTEGRATION - PIPELINE COMPLET
# ==============================================================

async def test_full_pipeline():
    from app.ecu_engine.engine import analyze_ecu_file

    print("\n--- Test Pipeline Complet : Bosch EDC17C64 ---")
    t0 = time.time()
    result = await analyze_ecu_file("test_edc17c64.bin", create_bosch_edc17c64())
    dt = time.time() - t0

    test("Result non vide", result is not None)
    test("ECU detecte", result.get("ecu_type", "") != "", result.get("ecu_type", ""))
    test("Confiance > 0", result.get("confidence", 0) > 0, f"{result.get('confidence')}")
    test("Format binary", result.get("file_format", "") == "binary")
    test("Hypotheses >= 1", len(result.get("hypotheses", [])) >= 1)
    test("Steps = 10", len(result.get("pipeline_steps", [])) == 10, f"{len(result.get('pipeline_steps', []))}")
    test("Temps < 5s", dt < 5, f"{dt:.2f}s")
    test("Consistency score", result.get("consistency_score", 0) >= 0)
    test("Risks est liste", isinstance(result.get("risks", []), list))
    test("Review reasons est liste", isinstance(result.get("review_reasons", []), list))
    print(f"  Temps total pipeline: {dt:.2f}s")


async def test_pipeline_delphi():
    from app.ecu_engine.engine import analyze_ecu_file

    print("\n--- Test Pipeline Complet : Delphi DCM3.7 ---")
    t0 = time.time()
    result = await analyze_ecu_file("test_dcm37.bin", create_delphi_dcm37())
    dt = time.time() - t0

    test("Delphi ECU detecte", result.get("ecu_type", "") != "")
    test("Delphi confiance > 0", result.get("confidence", 0) > 0)
    test("Delphi temps < 5s", dt < 5, f"{dt:.2f}s")


async def test_pipeline_siemens():
    from app.ecu_engine.engine import analyze_ecu_file

    print("\n--- Test Pipeline Complet : Siemens Simos 18.1 ---")
    t0 = time.time()
    result = await analyze_ecu_file("test_simos181.bin", create_siemens_simos181())
    dt = time.time() - t0

    test("Simos ECU detecte", result.get("ecu_type", "") != "")
    test("Simos confiance > 0", result.get("confidence", 0) > 0)


async def test_pipeline_empty():
    from app.ecu_engine.engine import analyze_ecu_file

    print("\n--- Test Pipeline : Fichier vide ---")
    result = await analyze_ecu_file("empty.bin", b'')
    test("Empty needs_review", result.get("needs_review", False))
    test("Empty format empty", result.get("file_format") == "empty")


async def test_pipeline_unknown():
    from app.ecu_engine.engine import analyze_ecu_file

    print("\n--- Test Pipeline : Fichier inconnu ---")
    unk = b'\x00' * 100000 + b'UnknownECU' + b'\xFF' * 50000
    result = await analyze_ecu_file("unknown.bin", unk)
    test("Unknown needs_review", result.get("needs_review", False))
    test("Unknown has hypotheses", isinstance(result.get("hypotheses"), list))


async def test_api_compat():
    from app.agents.ecu_ai_engine import analyze_ecu_file, generate_modified_file

    print("\n--- Test Compatibilite API ---")
    result = await analyze_ecu_file("compat_test.bin", create_bosch_edc17c64())
    test("Compat analyze OK", result is not None)
    test("Compat has ecu_type", "ecu_type" in result)
    test("Compat has confidence", "confidence" in result)

    mod = await generate_modified_file(create_bosch_edc17c64(), result, ["Stage 1", "DPF OFF"])
    test("Compat modified file", len(mod) == len(create_bosch_edc17c64()))
    test("Compat modified different", mod != create_bosch_edc17c64())


# ==============================================================
#  TESTS PERFORMANCE
# ==============================================================

async def test_performance():
    from app.ecu_engine.engine import analyze_ecu_file

    print("\n--- Test Performance ---")
    data = create_bosch_edc17c64()
    times = []
    for i in range(3):
        t0 = time.time()
        await analyze_ecu_file(f"perf_{i}.bin", data)
        times.append(time.time() - t0)
    avg = sum(times) / len(times)
    test("3 runs completes", len(times) == 3)
    test("Avg < 3s", avg < 3, f"{avg:.2f}s")
    print(f"  Temps moyens: {avg:.2f}s (min: {min(times):.2f}s, max: {max(times):.2f}s)")


# ==============================================================
#  MAIN
# ==============================================================

async def main():
    global total_time
    t_start = time.time()

    print("=" * 70)
    print("TESTS SUITE - MOTEUR ECU ENGINE v2")
    print("=" * 70)

    test_format_detector()
    test_processor_identifier()
    test_memory_identifier()
    test_info_extractor()
    test_signature_scanner()
    test_segment_analyzer()
    test_map_detector()
    test_checksum_engine()
    test_cross_validator()

    await test_full_pipeline()
    await test_pipeline_delphi()
    await test_pipeline_siemens()
    await test_pipeline_empty()
    await test_pipeline_unknown()
    await test_api_compat()
    await test_performance()

    total_time = time.time() - t_start
    print("\n" + "=" * 70)
    print(f"  RESULTATS: {passed} passes, {failed} echecs, {passed+failed} total")
    print(f"  Temps total: {total_time:.2f}s")
    print("=" * 70)

    if failed > 0:
        print("\n  ATTENTION: Certains tests ont echoue!")
        sys.exit(1)
    else:
        print("\n  TOUS LES TESTS REUSSIS")


if __name__ == "__main__":
    asyncio.run(main())
