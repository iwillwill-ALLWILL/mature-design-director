# Official Competition Rule Research

Use this reference when the task is to determine the exact submission strategy before producing a deck or package.

## Source hierarchy

1. Current official competition page and its public first-party data/API payload.
2. Official FAQ on the same event.
3. Login-gated portal UI, inspected only when authorized; do not register or submit merely to research fields.
4. Official organizer announcements, finalist lists, winner galleries, and showcase materials.
5. Third-party competition indexes only for discovery or corroboration, never to override first-party rules.
6. Generic platform frontend behavior is implementation evidence, not event-specific policy.

## Rule extraction method

Build a matrix with these separate columns:

- stage: registration, preliminary, final, showcase;
- artifact or action;
- mandatory / optional / prohibited / unknown;
- format, size, naming, and packaging;
- exact deadline and timezone;
- resubmission/version behavior;
- portal field/link;
- source URL and exact operative wording;
- confidence and unresolved conflict.

Do not collapse these distinctions:

- registration deadline vs submission deadline;
- final upload deadline vs final roadshow/award date;
- permitted supplement vs mandatory artifact;
- invited showcase opportunity vs required finalist participation;
- public Demo link vs permission for every kind of external link;
- a generic upload-component limit vs the event-specific size cap.

## Resolving contradictory wording

Official pages may call source files “necessary” in narrative text while a later format table labels them optional. Resolve contradictions using the most specific operative language, then cross-check the FAQ. For example:

- explicit `[Required]` / `[Optional]` labels beat loose prose;
- a FAQ saying “proposal-only is allowed” confirms that code/video/Demo are supplements;
- the event-specific 100 MB rule beats a generic frontend component's 150 MB default.

Record the contradiction rather than silently choosing one sentence.

## Portal reconnaissance without login

- Verify the exact event URL and what the public CTA does.
- If the CTA redirects to authentication, stop at the login boundary unless the user authorized login.
- Report post-login fields as **not publicly verified**.
- First-party JavaScript/API contracts may reveal generic fields such as file URL, filename, description, or submission history. Label these as implementation observations, not guaranteed user-facing fields or event rules.
- Never invent portal fields from another competition hosted on the same platform.

## Artifact-permission discipline

Use only officially enumerated supplements as confidently permitted. If the rules allow code files and Demo links but do not mention repository URLs:

- a code snapshot in the ZIP is clearly permitted;
- a repo URL is an optional convenience, not a substitute for the permitted code artifact;
- QR codes can encode an already permitted Demo link, but should not be described as a separately authorized artifact and must not be the sole access path;
- appendices are safest as part of the required PDF/PPT unless the portal explicitly supports separate appendices.

For unspecified limits, say `not published`. A conservative recommendation such as keeping the whole ZIP below the document cap must be labeled advice, not rule.

## Winner/example search

Search for three different evidence classes:

1. same-event winner/finalist materials;
2. organizer-authored scenario and Agent-behavior examples;
3. adjacent-event winners, clearly labeled secondary analogy.

If the event has not yet reached the preliminary deadline, explicitly state that same-event winners/finalists cannot yet exist. Do not turn organizer scenario suggestions into “winning examples.”

## Dynamic official-page pitfalls

Retain these generalized lessons without copying a competition's identity or submission record into the shared skill:

- Event routes and first-party data keys may be case-sensitive; an empty guessed route is not proof that data does not exist.
- A public first-party page-data payload may expose rules, FAQ, dates, rubrics, and resubmission behavior when the rendered page is dynamic.
- An award or roadshow date is not automatically a material-upload deadline.
- A required preliminary proposal can coexist with optional Demo, video, code, prototype, or install supplements despite looser narrative wording.
- Explicitly enumerated links are safer than assuming repository URLs or QR codes are separately authorized.
- Final-stage formats and timelines may legitimately remain unresolved until a later organizer notice.

## Required output

A complete research deliverable should include:

1. concise conclusion on whether the minimum package is strategically suboptimal;
2. rule matrix;
3. rubric-to-evidence matrix;
4. portal/link table with unauthenticated limits disclosed;
5. at least two competing artifact portfolios ranked qualitatively;
6. official example/winner availability statement;
7. unresolved-rule list and organizer contact path.
