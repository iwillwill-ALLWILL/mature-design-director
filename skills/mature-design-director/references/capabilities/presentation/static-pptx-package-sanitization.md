# Static PPTX Package Sanitization

Use after a strict OOXML audit finds dormant placeholders, stale metadata, or aspect-ratio mismatch in an image-backed competition deck. This is a remediation workflow, not a read-only audit.

## Why visual QA is insufficient

`python-pptx` can generate a visually correct deck while retaining default master/layout text such as `Click to edit Master title style`, stale dates, slide-number tokens, `Steve Canny`, `Slides=0`, `screen4x3`, and `generated using python-pptx`. Full-slide images hide these on screen but do not remove them from the OOXML package.

## Rebuild pattern

1. Start from the approved authored PNGs; never redesign during package repair.
2. Make source and destination aspect ratios mathematically identical before embedding:
   - verify `width × slide_height == height × slide_width` using integers, not rounded decimal ratios;
   - for exact 16:9, verify `width × 9 == height × 16` for both raster pixels **and OOXML EMUs**;
   - do not assume `Inches(13.333333)` is exact: `python-pptx` may round it to `12,191,999 EMU`, while `7.5 in` is `6,858,000 EMU`, leaving a one-EMU width defect and a nonzero cross-product;
   - when using a 7.5-inch slide height, assign the exact integer dimensions directly: `slide_width = 12_192_000`, `slide_height = 6_858_000`; assert `slide_width * 9 - slide_height * 16 == 0` in the verifier;
   - if a renderer rounded a logical 16:9 canvas (for example 3920×2208), crop only the minimal non-semantic edge pixels to an exact ratio (3920×2205), then visually recheck risk pages.
3. Add exactly one picture per blank slide at offset `(0,0)` and at the full slide extent.
4. Set current core metadata explicitly:
   - title, subject, creator, last modifier;
   - created/modified timestamp;
   - use `core_properties.comments`, not an ad-hoc `description` attribute, to replace python-pptx's default `dc:description`.
5. Post-process the saved OOXML ZIP:
   - in every `ppt/slideMasters/*.xml` and `ppt/slideLayouts/*.xml`, remove drawable children (`p:sp`, `p:pic`, `p:graphicFrame`, `p:cxnSp`, `p:contentPart`) from `p:spTree`, preserving required group-property nodes;
   - set `ppt/presentation.xml` `p:sldSz/@type` to `screen16x9` when that is the real format;
   - set `docProps/app.xml` `PresentationFormat`, `Slides`, and `Company` to current values;
   - rewrite through a temporary ZIP and atomically replace the output.
6. Do not place manifests, editable sources, QA renders, supplements, or receipts in the strict upload directory unless the official format explicitly requires them.

## Strict regression verifier

The rebuild is incomplete unless an automated verifier asserts all of the following against the final binary:

- final directory contains exactly the approved upload file set;
- ZIP CRC passes; no duplicate or encrypted members;
- exact slide count from `presentation.xml`;
- one `p:pic` and zero `p:sp` / `p:graphicFrame` / `p:cxnSp` per slide;
- picture offset `(0,0)` and extent exactly equal to `p:sldSz`;
- every embedded page has the expected dimensions and no APNG chunks (`acTL`, `fcTL`, `fdAT`);
- master/layout drawable shapes are zero;
- placeholder strings are absent across every XML part, including unused layouts;
- no external relationship in any `.rels` part;
- no GIF/video/audio, notes, comments, macros, ActiveX, OLE, or embeddings;
- `screen16x9`, `Slides=N`, company, creator, last modifier, and current dates are consistent;
- stale authors, dates, and generator descriptions are absent;
- final size is under the official cap and a fresh SHA-256 is recorded.

## Content-regression companion

Package cleanup does not prove official content coverage. Keep a source-level contract that searches the authored deck source for every mandatory concept, especially capabilities often left implicit:

- multi-turn modification/replanning;
- current memory boundary versus planned learning;
- proactive trigger mechanism;
- stack, data path, model/hardware/dependency boundary, and future adapter path;
- lead background, roles, team/company structure, and truthful partner status;
- business model and go-to-market;
- full originality/truthfulness and required IP-liability wording.

After any content repair: re-render affected pages, inspect them at full resolution, update the canonical contact sheet and lower-density QA renders, rebuild the PPTX, rerun the package verifier, and invalidate every previous approval/hash.

## Compatibility wording

Exercise available viewers separately and report only what was tested:

- macOS Quick Look first-slide render;
- LibreOffice headless PDF export and page count;
- ONLYOFFICE actual file open/handle;
- Microsoft PowerPoint remains `NOT TESTED` when absent.

Successful rendering never substitutes for package sanitation or official-content coverage.
