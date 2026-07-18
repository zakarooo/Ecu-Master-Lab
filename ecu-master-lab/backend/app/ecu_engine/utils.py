"""
Utilitaires binaires pour l'analyse ECU.

Fonctions pures, pas d'etat, optimisees pour les gros fichiers.
"""

import struct
import hashlib
from typing import List, Tuple, Optional


def compute_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    length = len(data)
    import math
    entropy = 0.0
    for count in freq:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy / 8.0


def compute_hashes(data: bytes) -> dict:
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
        "crc32": format(crc32(data), "08X"),
    }


def crc32(data: bytes) -> int:
    import binascii
    return binascii.crc32(data) & 0xFFFFFFFF


def find_ascii_strings(data: bytes, min_length: int = 4, max_offset: int = -1) -> List[Tuple[int, str]]:
    if max_offset <= 0:
        max_offset = len(data)
    results = []
    current = bytearray()
    start = 0
    limit = min(max_offset, len(data))
    for i in range(limit):
        b = data[i]
        if 32 <= b < 127:
            if not current:
                start = i
            current.append(b)
        else:
            if len(current) >= min_length:
                results.append((start, current.decode("ascii", errors="ignore")))
            current = bytearray()
    if len(current) >= min_length:
        results.append((start, current.decode("ascii", errors="ignore")))
    return results


def find_binary_pattern(data: bytes, pattern: bytes, start: int = 0, end: int = -1) -> List[int]:
    if end <= 0:
        end = len(data)
    results = []
    idx = start
    while idx < end:
        pos = data.find(pattern, idx, end)
        if pos == -1:
            break
        results.append(pos)
        idx = pos + 1
        if len(results) > 1000:
            break
    return results


def read_uint8(data: bytes, offset: int) -> int:
    if offset >= len(data):
        return 0
    return data[offset]


def read_uint16_be(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        return 0
    return struct.unpack_from(">H", data, offset)[0]


def read_uint16_le(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        return 0
    return struct.unpack_from("<H", data, offset)[0]


def read_uint32_be(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        return 0
    return struct.unpack_from(">I", data, offset)[0]


def read_uint32_le(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        return 0
    return struct.unpack_from("<I", data, offset)[0]


def read_int16_be(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        return 0
    return struct.unpack_from(">h", data, offset)[0]


def read_int16_le(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        return 0
    return struct.unpack_from("<h", data, offset)[0]


def count_byte_frequency(data: bytes, sample_size: int = 65536) -> dict:
    if not data:
        return {}
    sample = data[:sample_size]
    freq = {}
    for b in sample:
        freq[b] = freq.get(b, 0) + 1
    return freq


def detect_null_fill(data: bytes, region_start: int, region_size: int = 4096) -> float:
    end = min(region_start + region_size, len(data))
    if region_start >= end:
        return 0.0
    null_count = 0
    for i in range(region_start, end):
        if data[i] == 0x00:
            null_count += 1
    return null_count / (end - region_start)


def detect_ff_fill(data: bytes, region_start: int, region_size: int = 4096) -> float:
    end = min(region_start + region_size, len(data))
    if region_start >= end:
        return 0.0
    ff_count = 0
    for i in range(region_start, end):
        if data[i] == 0xFF:
            ff_count += 1
    return ff_count / (end - region_start)


def block_entropy(data: bytes, block_size: int = 256, max_blocks: int = 256) -> List[float]:
    results = []
    for i in range(0, min(len(data), block_size * max_blocks), block_size):
        block = data[i:i + block_size]
        results.append(compute_entropy(block))
    return results


def is_likely_data_region(data: bytes, offset: int, size: int = 256) -> bool:
    end = min(offset + size, len(data))
    if offset >= end:
        return False
    non_empty = 0
    unique = set()
    for i in range(offset, end):
        b = data[i]
        unique.add(b)
        if b not in (0x00, 0xFF):
            non_empty += 1
    total = end - offset
    return non_empty > total * 0.2 and len(unique) > 20
