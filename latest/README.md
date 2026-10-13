# Latest #46986 regression matrix

This fixture broadens the original comparison to dependency identity, target
identity, content identity, source isolation, and interaction with fetched notes.
Frozen Unity-format registry responses are served directly from this repository.
The Nextcloud control uses the live public Nextcloud 30 feed.

The tested source commit is `d356ad69be88eb9d222a57a69005c730f1d92505`.

| Case | Expected behavior |
| --- | --- |
| Original Unity duplicate | One Input System section; Cinemachine preserved |
| Original separator collision | Both COLLISION_NOTE_A and COLLISION_NOTE_B preserved |
| Exact duplicate occurrence | Both file occurrences update; one note section |
| Different current versions, same package and target | Target notes appear once |
| Same package, different targets | Version 2.0.0 and 3.0.0 notes both appear |
| Different aliases, same package and target | One canonical package's notes appear once |
| Different packages, identical content and source | Identical note marker appears twice |
| Missing embedded notes | Dependency still updates; other notes remain |
| Embedded and repository-fetched notes in one group | Both embedded packages retain their notes; shared repository notes appear once |
| Same package and target, different datasources | Both Unity and Nextcloud sections remain |
| Same package and target, different registry URLs and contents | Both registry-specific note markers should remain |
| Retry of the same run | PR count, branches, file updates, and note content remain stable |

`expectations.json` lists expected note markers, summary counts, and every
updated version. The cross-registry case is a boundary check: each registry
serves different notes for the same package name and target.

`mixed-deps.txt` uses two aliases for this repository's synthetic GitHub release
v2.0.0, plus two embedded-note packages sharing the same source repository.
The release request payloads are retained alongside the fixture.

Run the latest source checkout against this repository with a distinct prefix:

```bash
LOG_LEVEL=debug pnpm start --platform=github --onboarding=false --branch-prefix=renovate/latest-46986/ --branch-prefix-old=renovate/latest-46986/ --pr-hourly-limit=0 --pr-concurrent-limit=0 MindTooth/renovate-test-46986
```

Keep all dependency fixture files on the default branch unchanged.
Results will be recorded after verifying the generated PR bodies and updated files.
Unit checks supplement cases that cannot naturally arise from registry lookup,
including the `newValue` fallback when `newVersion` is absent and changelog errors.
