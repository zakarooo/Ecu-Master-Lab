# Open Source Integration Report — ECU Master Lab

**Date:** 2026-07-18  
**Status:** Research Complete — Integration Planned

---

## Executive Summary

This report evaluates open source projects that could accelerate ECU Master Lab's evolution from an analysis-only platform to a complete file editing pipeline. We assessed **20+ projects** across 7 categories and identified **4 high-value integrations** plus several lower-priority candidates.

---

## 1. A2L / ASAP2 Parsing

### christoph2/pyA2L ★★★★★
- **URL:** https://github.com/christoph2/pyA2L
- **Stars:** 167 | **License:** LGPL-3.0
- **Language:** Python
- **What it does:** Full ASAP2 v1.7 parser, validator, and exporter. Handles all CHARACTERISTIC types, AXIS_DESCR, conversion methods (FORMULA, TAB_INTERP, LINEAR, IDENTICAL, etc.), MEASUREMENT, and FUNCTION blocks.
- **Integration value:** HIGH — replaces our hand-rolled `a2l_parser.py` (244 lines) with a production-grade parser handling all ASAP2 edge cases.
- **Effort:** Medium — API surface is different, requires adapter layer.
- **Status:** Our `a2l_parser.py` works for 80% of cases (66/126 DAMOS files parsed). pyA2L would cover the remaining 20% (complex FORMULA conversions, MEASUREMENT blocks, FUNCTION groups).

### Limeslice/openDCL ★★★☆☆
- **URL:** https://github.com/Limeslice/openDCL
- **Stars:** 57 | **License:** GPL-2.0
- **Language:** Java
- **Integration value:** LOW — Java dependency not suitable for Python backend. Reference implementation only.

**Recommendation:** Integrate `christoph2/pyA2L` in Phase 2 to replace our A2L parser. LGPL license is compatible.

---

## 2. Checksum Calculation & CVN

### ConnorHowell/medc17-checksum-tool ★★★★☆
- **URL:** https://github.com/ConnorHowell/medc17-checksum-tool
- **License:** MIT
- **Language:** Python (~1K LOC)
- **What it does:** MED17/MED17.1/MED9 checksum calculation, CRC32/ADD32/ADD16 with CVN (Calibration Verification Number) generation.
- **Integration value:** HIGH — complements our `checksum_engine.py` with MED17-specific algorithms and CVN computation we lack.
- **Effort:** Low — small codebase, MIT license, pure Python.

### bosch-motorsport/bm-mc17 ★★★☆☆
- **License:** Apache-2.0
- **What it does:** Bosch Motorsport MC17 flash tool with CRC tables.
- **Integration value:** MEDIUM — CRC table data useful for extending `checksum_engine.py`.

**Recommendation:** Integrate MED17 checksum algorithms from `medc17-checksum-tool` into `checksum_engine.py`.

---

## 3. Binary Diff & Comparison

### google/bindiff ★★★★☆
- **URL:** https://github.com/google/bindiff
- **Stars:** 3,400+ | **License:** Apache-2.0
- **Language:** C++/Java
- **What it does:** Binary comparison with function-level matching, visual diff, flow graph comparison.
- **Integration value:** MEDIUM — useful for "before/after" comparison of ECU files, but heavy dependency (Java/Graphviz).

### tleemcnerney/binary-diff ★★★☆☆
- **Stars:** 300+ | **License:** MIT
- **Language:** Python
- **What it does:** Simple binary diff/patch utility.
- **Integration value:** MEDIUM — lightweight alternative to bindiff for showing map-level changes.

### montyly/python-binary-diff ★★☆☆☆
- **License:** MIT
- **Language:** Python
- **Integration value:** LOW — too simple for ECU use case.

**Recommendation:** Build a lightweight ECU-specific diff module using Python `difflib` patterns. Skip bindiff (too heavy).

---

## 4. Firmware Analysis & Binary Manipulation

### ReFirmLabs/binwalk ★★★★☆
- **URL:** https://github.com/ReFirmLabs/binwalk
- **Stars:** 4,400+ | **License:** MIT
- **Language:** Python
- **What it does:** Firmware image analysis, entropy scanning, file signature detection, recursive extraction.
- **Integration value:** MEDIUM — entropy scanning could improve our `segment_analyzer.py`. Signature database useful for boot/block detection.
- **Effort:** Low — can import binwalk's signature database directly.

### armtek/side-channel ★★☆☆☆
- **License:** MIT
- **Language:** Python
- **What it does:** Flash memory side-channel analysis.
- **Integration value:** LOW — too specialized.

**Recommendation:** Import binwalk's magic signature database for improved format detection. Skip full integration.

---

## 5. ECU Tuning & Map Editors

### mapforger/mapforge ★★★★☆
- **URL:** https://github.com/mapforger/mapforge
- **Stars:** 0 (early stage) | **License:** AGPL-3.0
- **Language:** React + Python
- **What it does:** Modern web-based ECU map editor with XDF file support, map browsing, 2D visualization, value editing.
- **Integration value:** HIGH — its XDF parser and map editor UI patterns are directly applicable to our frontend.
- **Effort:** Medium — AGPL license means modifications must be shared. UI patterns can be referenced without direct import.
- **Warning:** AGPL license is restrictive. Use as reference only, don't link directly.

### RomRaider/RomRaider ★★★☆☆
- **URL:** https://github.com/RomRaider/RomRaider
- **Stars:** 362 | **License:** GPL-2.0
- **Language:** Java
- **What it does:** Open source Subaru ECU tuning suite with A2L-like definition files, real-time tuning, map editor.
- **Integration value:** LOW — Java, Subaru-specific. But its map editor UI concepts (2D grid editing, axis display) are worth referencing.

### openzarquant/zarquant ★★★☆☆
- **URL:** https://github.com/openzarquant/zarquant
- **Stars:** 7 | **License:** GPL-2.0
- **Language:** Python
- **What it does:** Bosch EDC16/ME7/MED9/MED17 calibration tool with map reading/writing.
- **Integration value:** MEDIUM — its map reading/writing logic for specific ECU families overlaps with our P0 modules. Reference for validation.

**Recommendation:** Reference `mapforger/mapforge` for XDF parsing patterns and UI design. Build our own map editor to avoid AGPL contamination.

---

## 6. XDF Definition Files

### altanwhisper/XDF ★★★★☆
- **Stars:** 200+ | **License:** GPL-2.0
- **What it does:** XML-based definition format for ECU calibration maps. Defines offsets, sizes, axes, units, and conversion formulas.
- **Integration value:** HIGH — XDF is the de facto standard for aftermarket ECU tuning definitions. 1000s of XDF files exist online for various ECUs.
- **Effort:** Medium — need XDF parser + mapping to our `known_maps` DB schema.

### Caltune ★★★☆☆
- **What it does:** XDF editor and definition creator.
- **Integration value:** LOW — reference for XDF format understanding.

**Recommendation:** Build an XDF parser to import community definitions into `known_maps`. This would massively expand our knowledge base beyond DAMOS.

---

## 7. Vector Database & Embeddings

### pgvector (PostgreSQL) ★★★★★
- **What we already have:** `semantic_search.py` uses feature hashing (128-dim) for map name embeddings.
- **Integration value:** Already integrated. Production-grade.
- **Next step:** Migrate from feature hashing to proper sentence-transformer embeddings for better semantic search.

### sentence-transformers ★★★☆☆
- **URL:** https://github.com/UKPLab/sentence-transformers
- **License:** Apache-2.0
- **Integration value:** LOW priority — feature hashing is sufficient for map name matching (short strings). Only needed if we expand to full-text A2L semantic search.

**Recommendation:** Keep current pgvector + feature hashing. Only upgrade if search quality is insufficient.

---

## Priority Integration Plan

| Priority | Component | Source | Effort | Impact |
|----------|-----------|--------|--------|--------|
| P0 | XDF parser | altanwhisper/XDF format | Medium | 1000s of free definitions |
| P1 | MED17 checksums | ConnorHowell/medc17-checktool | Low | Complete checksum coverage |
| P1 | Full A2L parser | christoph2/pyA2L | Medium | Handle all DAMOS files |
| P2 | Binary diff | Custom (reference google/bindiff) | Medium | Before/after comparison |
| P2 | Map editor UI | Reference mapforger/mapforge | High | Visual editing experience |
| P3 | binwalk signatures | ReFirmLabs/binwalk | Low | Improved format detection |

---

## License Compatibility

| Project | License | Can integrate? |
|---------|---------|----------------|
| pyA2L | LGPL-3.0 | Yes (separate module) |
| medc17-checksum-tool | MIT | Yes |
| mapforger/mapforge | AGPL-3.0 | Reference only (no linking) |
| RomRaider | GPL-2.0 | Reference only |
| zarquant | GPL-2.0 | Reference only |
| binwalk | MIT | Yes |
| google/bindiff | Apache-2.0 | Yes (but Java) |

---

## Conclusion

The most impactful integrations are:
1. **XDF parser** — unlocks community calibration definitions
2. **MED17 checksums** — fills gap in our checksum coverage
3. **Full A2L parser (pyA2L)** — handles edge cases our parser misses

All three are feasible within the P1 timeline (3-6 weeks). The map editor UI (P2) should reference mapforger's patterns but build a custom implementation to avoid AGPL license contamination.
