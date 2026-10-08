# RRC-ACT entrance review — 2026-10-08

Scope: three static research pages and their shared CSS. Direction: readable research entrance, restrained green/white palette, fixed type sizes, real published-paper thumbnail, primary paper link, current evidence limits and historical context. Existing research URLs are retained.

Two independent read-only reviewers covered scientific copy/version integrity and site navigation/design/accessibility leads. The main reviewer refuted or reproduced the findings against files, timestamps and browser output. A separate official multi-model documentation audit returned conditional approval, not theory validation.

## Findings closed

- P2: Chinese registration advice omitted the v1.2 amendment. Now requires v1.1 history, v1.2 corrections and complete inputs.
- P2: Independent replication appeared under prerequisites for first execution. Split into later validation stages.
- P2: Social image path lacked an asset. Added an accurate RRC-ACT bitmap with the published cover and pending-validation disclosure.
- P2: Minimum effect wording lacked direction. Clarified positive d=+0.50, distinguishes opposite effects from equivalence and wide intervals from evidence of absence.

## Evidence

- Deterministic detector: four frontend files, zero findings after cleanup.
- Chromium screenshots: home/English/Chinese at 1440, 390 and 320 pixels; no horizontal overflow, one h1 each, images loaded, first keyboard focus is the skip link.
- Reduced-motion mode uses the same static content; no animation or user telemetry is introduced.
- Browser-rendered text/background values converted through canvas to sRGB: body contrast 15.57, metadata 6.97, primary button and link 7.23. These are sampled checks, not a full WCAG certification.
- Relative navigation and scholarly metadata parse checks pass. Source, DOI, author/date and citation files agree with the publication record.
- All five pre-cleanup front-door snapshots are byte-identical to the source commit; timestamp protocol and published PDF were not modified.

No verified open P0/P1 frontend blocker. Scientific incompleteness, PDF internal v2.2 label in a v2.2.1 record, and toolchain-dependent timestamp verification are disclosed in the version map. They are not concealed by this design verdict. No field performance dataset or complete screen-reader conformance audit exists, so no claim of measured p75 Core Web Vitals or full WCAG certification is made.
