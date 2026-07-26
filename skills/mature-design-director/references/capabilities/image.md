# Product and Campaign Image Capability

Use this capability for product photography, ecommerce listing images, product-preserving edits, lifestyle scenes, hero banners, campaign imagery, detail shots, multi-angle sets, virtual models, and presentation concept scenes. Use the available image-generation/editing adapter; do not let provider defaults replace the direction.

Do not use generative editing as legal evidence of item condition, for exact logos/dielines/vector packaging, or for real UI screenshots.

## Product-truth contract

When a real product reference exists, preserve unless explicitly changed:

- silhouette, proportions, geometry, and visible dimensions;
- color, material, finish, condition, wear, and defects;
- logo, label, packaging text, controls, ports, seams, closures, and accessories;
- number and placement of parts.

Never invent certifications, ingredients, specifications, discounts, scores, endorsements, or claims. Generated text is untrusted until inspected. For second-hand listings, cleaning presentation must not erase condition evidence.

For text-only visualization of a real SKU, state internally and in any necessary user-facing disclosure that the result is conceptual and may not match unseen geometry.

## Reference-role triage

For one image, use it as the product identity source. For several images, choose one primary identity reference and label every additional role:

- alternate product detail;
- packaging truth;
- palette/brand reference;
- lighting/set reference only;
- composition reference only.

Do not let a style reference replace product identity. Do not hallucinate unseen rear/top geometry; omit the view or label it conceptual.

For edits, state only intended changes and repeat invariants: change lighting, crop, balance, or background; keep the product unchanged.

## Mode selection

| Mode | Typical use | Default orientation |
|---|---|---|
| Product shot | premium neutral studio/catalog | square |
| Marketplace main | strict clean primary listing | square |
| Lifestyle scene | believable use environment | portrait |
| Detail close-up | texture, feature, craftsmanship | square |
| With person | hand/partial person demonstrating use | portrait |
| Hero banner | web/email/campaign header | landscape |
| Social carousel/ad | connected campaign variants | portrait |
| Virtual model | clothing/accessory/use | portrait |
| Conceptual product | sculptural/surreal atmosphere | portrait |
| Restyle | season, set, palette, mood | preserve source unless specified |
| Multi-angle | independently generated verified angles | square |

Output placement wins tie-breaks. If a vague request is safe, generate sooner: default to a square clean studio shot, neutral background, restrained props, no added text, and exact product preservation. Ask only when usage/style/count/brand constraint materially changes output.

## Production prompt contract

Compose prompts in this order:

```text
Task/mode and intended placement
Identity source and role of each reference
Primary requested change/output
Scene/background and prop limit
Composition/camera, product scale, crop, negative space
Lighting and shadow/reflection behavior
Product invariants
Exact text or no added text
Concrete material/edge quality
Avoid: invented parts, geometry drift, duplicate product, altered logo/label, extra accessories, watermark
```

Describe camera, set, material, and lighting choices; remove empty superlatives.

### Studio/marketplace

Use a seamless controlled background, accurate color/material, clean edge, full product visibility, and a subtle natural contact shadow only where permitted. Marketplace requirements must be checked live; generation alone does not prove compliance.

### Lifestyle

Match scale, perspective, contact, reflections, temperature, and depth of field. Limit supporting props and keep the product the visual hero.

### Hero

Place product and focal detail deliberately, reserve negative space for later copy, and do not generate headline text unless exact wording is supplied.

### Restyle

Change background, set, light, and atmosphere; preserve product geometry, scale, position, condition, colors, logo, label, and accessories.

### Multi-angle

Use one call per angle with the same identity contract. Generate only angles established by references. Keep the set coherent in camera language, scale, light, grade, and background.

## Batch discipline

- one requested image → one intentional generation/edit;
- variants → separate calls with meaningful angle/light/set differences;
- multi-angle → separate call per verified angle;
- independent calls may run in parallel;
- repeat the same identity invariants across the set;
- use one selected direction as the grade/composition anchor before scaling a campaign.

Generate at the closest supported aspect ratio, then crop/resize nondestructively to exact pixels. Never stretch.

## Concept scenes and evidence

Generated campaign or deck imagery must not impersonate product proof. Keep atmospheric scenes structurally separate from real screenshots, receipts, deployment photos, or measurements.

Avoid high-risk pseudo-writing, hands holding screens, readable fake UI, pristine CGI deployment, and malformed devices unless essential and rigorously inspected. Prefer powered-off screens, distant/no people, natural imperfection, or architecture-only scenes. Composite real UI into a licensed/real device image when a screen must prove behavior.

A concept label does not rescue a visibly bad image; regenerate it.

## Visual verification

Inspect every important output against its source at full scale and final placement scale:

- product count and silhouette;
- proportions, perspective, and camera geometry;
- color/material/condition accuracy;
- logo and label integrity;
- missing, duplicated, or invented parts;
- hands, faces, devices, text, and reflections;
- contact shadow and physical grounding;
- edge quality, alpha, background cleanliness;
- composition, focal point, crop, and usable negative space;
- accidental text/watermark;
- identity and grade consistency across the set.

Use vision analysis as a second pass, not as a substitute for direct inspection. Correct one identified defect at a time from the original source; do not iteratively edit an already drifted output.

Never claim identity perfection, text perfection, or platform compliance without inspection and the applicable deterministic checks.

## Delivery and provenance

Deliver actual images inline and state only mode, intended change, whether identity came from a real reference or text concept, and unresolved fidelity risks. Preserve source roles, generation/edit truth boundary, license/rights chain, and exact approval scope in private production records.

The mode taxonomy and workflow were adapted from Higgsfield Product Photoshoot under MIT; retain `references/licenses/HIGGSFIELD-PRODUCT-PHOTOSHOOT.txt` with this private workflow.