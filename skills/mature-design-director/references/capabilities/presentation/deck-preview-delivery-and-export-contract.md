# Deck preview delivery and export-contract notes

## Why this reference exists

A high-quality deck session exposed two failure modes that are easy to miss in otherwise correct production workflows: a preview can exist without being visible to the user, and a verifier can become stale when exporter pixel density changes.

## Preview-delivery fallback

1. Generate the normal contact sheet.
2. Attach the contact sheet and final artifacts using separate attachment lines.
3. If the user reports that nothing appeared:
   - verify each image exists;
   - inspect pixel width/height;
   - resend individual slide PNGs separately, beginning with the representative pages;
   - do not rely on another tall composite.
4. Treat explicit user visibility/approval as the visual gate—not file existence or a successful tool return.

This is especially important in desktop/chat clients where tall images or multiple attachments may not render uniformly.

## Export-density contract

Slide systems distinguish logical canvas size from exported bitmap size. A logical 980×552 deck may export at approximately 1960×1104 because of a 2× device-pixel ratio.

A durable verifier should check:

- exact numbered slide set;
- PNG signature;
- consistent aspect ratio;
- dimensions compatible with an explicit allowed density scale;
- contact-sheet freshness;
- required assets and labels;
- no temporary build environments.

Avoid silently preserving a prototype-era hardcoded width/height after the exporter configuration changes. If exact bitmap dimensions matter, make scale explicit in the export command and version the verifier contract alongside it.

## Packaging sequence

After the approved representative-page gate:

1. expand to the full narrative;
2. export all resting frames;
3. inspect the full contact sheet and individual risk pages;
4. fix truth/legibility issues;
5. regenerate static PPTX/PDF;
6. reverse-render the current PDF;
7. validate slide count and OOXML integrity;
8. record fresh hashes;
9. remove temporary venvs and stop preview servers;
10. deliver visible previews before external submission.
