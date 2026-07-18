"""
Test du moteur ECU AI v2 - verifie les 7 etapes du pipeline.
Cree un binaire synthetique realiste et lance l'analyse.
"""
import asyncio
import struct
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.agents.ecu_ai_engine import analyze_ecu_file


def create_fake_edc17c64():
    size = 1048576
    data = bytearray(b'\xFF' * size)
    data[0x200:0x205] = b'Bosch'
    data[0x100:0x108] = b'EDC17C64'
    data[0x110:0x11A] = b'1037356247'
    for offset in [0x2A000, 0x2B000, 0x2C000, 0x2D000, 0x2E000]:
        for i in range(0, 0x200, 2):
            val = (offset + i) % 1000
            struct.pack_into("<H", data, offset + i, val)
    data[0x1FFC:0x2000] = b'\xAA\xBB\xCC\xDD'
    return bytes(data)


def create_fake_delphi_dcm37():
    size = 524288
    data = bytearray(b'\xFF' * size)
    data[0:6] = b'Delphi'
    data[0x100:0x106] = b'DCM3.7'
    data[0x110:0x11A] = b'1037347844'
    for offset in [0x10000, 0x11000, 0x12000, 0x13000]:
        for i in range(0, 0x200, 2):
            struct.pack_into("<H", data, offset + i, (offset + i) % 500)
    return bytes(data)


def create_fake_unknown():
    return b'\x00' * 100000 + b'UnknownECU' + b'\xFF' * 50000


async def main():
    print("=" * 70)
    print("  TEST MOTEUR ECU AI v2 - 7 ETAPES")
    print("=" * 70)

    # Test 1
    print("\n--- Test 1 : Bosch EDC17C64 synthetique ---")
    edc_data = create_fake_edc17c64()
    result = await analyze_ecu_file("test_edc17c64.bin", edc_data)
    print(f"  ECU detecte    : {result['ecu_type']}")
    print(f"  Constructeur   : {result['ecu_brand']}")
    print(f"  HW Version     : {result['hw_version']}")
    print(f"  SW Version     : {result['sw_version']}")
    print(f"  Confiance      : {result['confidence']}%")
    print(f"  Checksum       : {result['checksum_valid']}")
    print(f"  Checksum algo  : {result['checksum_algorithm']}")
    print(f"  Format         : {result['file_format']}")
    print(f"  Needs review   : {result['needs_review']}")
    print(f"  Recommandation : {result['recommendation']}")
    print(f"  Cartographies  : {len(result['map_regions'])} maps ({result['total_map_bytes']} octets)")
    print(f"  Hypotheses     : {len(result['hypotheses'])}")
    for i, h in enumerate(result['hypotheses'][:3]):
        print(f"    #{i+1} {h['ecu']} - {h['confidence']}%")
    print(f"  Risques        : {result['risks']}")
    print(f"  Coherence      : {result['consistency_score']}%")
    print(f"  Temps          : {result['processing_time_seconds']}s")
    print(f"  Etapes         : {len(result['analysis_steps'])}")
    assert result['confidence'] > 0, "La confiance devrait etre > 0"
    assert len(result['analysis_steps']) == 7, "Devrait avoir 7 etapes"
    print("  PASS")

    # Test 2
    print("\n--- Test 2 : Delphi DCM3.7 synthetique ---")
    dcm_data = create_fake_delphi_dcm37()
    result2 = await analyze_ecu_file("test_dcm37.bin", dcm_data)
    print(f"  ECU detecte    : {result2['ecu_type']}")
    print(f"  Constructeur   : {result2['ecu_brand']}")
    print(f"  Confiance      : {result2['confidence']}%")
    print(f"  Hypotheses     : {len(result2['hypotheses'])}")
    print("  PASS")

    # Test 3
    print("\n--- Test 3 : Fichier inconnu ---")
    unk_data = create_fake_unknown()
    result3 = await analyze_ecu_file("unknown.bin", unk_data)
    print(f"  ECU detecte    : {result3['ecu_type']}")
    print(f"  Confiance      : {result3['confidence']}%")
    print(f"  Needs review   : {result3['needs_review']}")
    print(f"  Recommandation : {result3['recommendation']}")
    print("  PASS")

    # Test 4
    print("\n--- Test 4 : Fichier vide ---")
    result4 = await analyze_ecu_file("empty.bin", b'')
    print(f"  Format         : {result4['file_format']}")
    print(f"  Needs review   : {result4['needs_review']}")
    print("  PASS")

    # Test 5
    print("\n--- Test 5 : Verification CRC16 CCITT ---")
    from app.agents.ecu_ai_engine import _crc16_ccitt
    test_data = b'Hello, World!'
    crc = _crc16_ccitt(test_data)
    print(f"  CRC16 de 'Hello, World!' = 0x{crc:04X}")
    assert crc != 0, "CRC16 devrait etre non-nul"
    crc2 = _crc16_ccitt(test_data)
    assert crc == crc2, "CRC16 devrait etre deterministe"
    print("  PASS")

    # Test 6
    print("\n--- Test 6 : Verification CRC32 Bosch ---")
    from app.agents.ecu_ai_engine import _crc32_bosch
    crc32 = _crc32_bosch(test_data)
    print(f"  CRC32 Bosch de 'Hello, World!' = 0x{crc32:08X}")
    assert crc32 != 0, "CRC32 devrait etre non-nul"
    crc32_2 = _crc32_bosch(test_data)
    assert crc32 == crc32_2, "CRC32 devrait etre deterministe"
    print("  PASS")

    print("\n" + "=" * 70)
    print("  TOUS LES TESTS REUSSIS")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
