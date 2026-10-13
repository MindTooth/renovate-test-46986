# Latest #46986 regression matrix

This fixture broadens the original comparison to dependency identity, target
identity, content identity, source isolation, and interaction with fetched notes.
Frozen Unity-format registry responses are served directly from this repository.
The Nextcloud control uses the live public Nextcloud 30 feed.

The tested source commit is `d356ad69be88eb9d222a57a69005c730f1d92505`.

| Case                                                          | Expected behavior                                                              |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Original Unity duplicate                                      | One Input System section; Cinemachine preserved                                |
| Original separator collision                                  | Both COLLISION_NOTE_A and COLLISION_NOTE_B preserved                           |
| Exact duplicate occurrence                                    | Both file occurrences update; one note section                                 |
| Different current versions, same package and target           | Target notes appear once                                                       |
| Same package, different targets                               | Version 2.0.0 and 3.0.0 notes both appear                                      |
| Different aliases, same package and target                    | One canonical package's notes appear once                                      |
| Different packages, identical content and source              | Identical note marker appears twice                                            |
| Missing embedded notes                                        | Dependency still updates; other notes remain                                   |
| Embedded and repository-fetched notes in one group            | Both embedded packages retain their notes; shared repository notes appear once |
| Same package and target, different datasources                | Both Unity and Nextcloud sections remain                                       |
| Same package and target, different registry URLs and contents | Both registry-specific note markers should remain                              |
| Retry of the same run                                         | PR count, branches, file updates, and note content remain stable               |

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

## Verified results

Live runs of the exact source commit above completed on 2026-10-13 against
fixture commit `fe0111e`. Five of six fixture groups pass. All 22 dependency
references update to their expected targets. A retry preserved all six PR
numbers, branch heads, full PR bodies, note counts, and updated file contents.

| Fixture group                             | Live PR                                                         | Result                           |
| ----------------------------------------- | --------------------------------------------------------------- | -------------------------------- |
| Original Unity duplicate                  | [#6](https://github.com/MindTooth/renovate-test-46986/pull/6)   | Pass                             |
| Separator collision                       | [#8](https://github.com/MindTooth/renovate-test-46986/pull/8)   | Pass                             |
| Dependency/target/content identity matrix | [#7](https://github.com/MindTooth/renovate-test-46986/pull/7)   | Pass                             |
| Embedded and repository-fetched notes     | [#10](https://github.com/MindTooth/renovate-test-46986/pull/10) | Pass                             |
| Datasource isolation                      | [#5](https://github.com/MindTooth/renovate-test-46986/pull/5)   | Pass                             |
| Registry isolation                        | [#11](https://github.com/MindTooth/renovate-test-46986/pull/11) | Fail: REGISTRY_B notes disappear |

The registry case is confirmed against the parent commit
`01303d3d1f828094ca97e391478e99a731e53067`:
[baseline PR #12](https://github.com/MindTooth/renovate-test-46986/pull/12)
includes both REGISTRY_A and REGISTRY_B. The latest patch retains REGISTRY_A
only, although both dependencies update correctly to 2.0.0.
The new key omits registry identity, so distinct registries with the same
datasource, package name, and target version collide semantically.
The key should distinguish the selected registry as well as those fields.

[results.json](results.json) contains full PR-body snapshots, every updated
version, note-marker assertions, retry comparisons, and the baseline control.
The initial minor-only matrix PR was normalized into the complete matrix;
Renovate closed the superseded major branch automatically.

## Verify

With `gh` authenticated:

```bash
python3 latest/verify.py --write latest/verification.json
python3 latest/verify.py --compare latest/results.json
python3 latest/verify.py --prefix renovate/registry-before-46986/ --files latest/registry-deps.txt
```

The complete verifier currently exits with status 1 because the registry-note
regression is intentionally asserted. The baseline registry-only check passes.
PR-body and updated-file checks use live GitHub API reads rather than HTTP mocks.

Unit checks supplement cases that cannot naturally arise from registry lookup,
including the `newValue` fallback when `newVersion` is absent and changelog errors.
Scoped checks passed for the embedding worker, PR worker, and release-note
renderer. This matrix covers the relevant note-deduplication boundaries; it
does not claim to test every Renovate datasource, platform, or versioning scheme.
