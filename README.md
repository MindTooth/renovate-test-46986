# Renovate #46986 reproduction

Reproduces duplicate embedded release notes after
[Renovate #46733](https://github.com/renovatebot/renovate/pull/46733), and checks
the fix in [#46986](https://github.com/renovatebot/renovate/pull/46986).

This GitHub repository uses Renovate's built-in `unity3d-packages` datasource
through a custom regex manager. It requires no Unity project or Azure account.

## Fixture

| Package               | Installed versions | Target ceiling |
| --------------------- | ------------------ | -------------- |
| com.unity.inputsystem | 1.13.0 and 1.14.0  | 1.15.0         |
| com.unity.cinemachine | 3.1.0              | 3.1.2          |

The three updates are grouped into one PR. Different installed Input System
versions deliberately survive upgrade deduplication while receiving the same
target release notes. Cinemachine checks that a different package keeps its notes.

## Compare

Run the same repository configuration with:

1. Commit `01303d3d1f828094ca97e391478e99a731e53067`, the parent of #46986,
   which already contains #46733.
2. Commit `254f22fc668458df493cfa33460aa36cb91f5463`, the #46986 branch.

Expected release-note sections:

| Implementation | Input System 1.15.0          | Cinemachine 3.1.2 |
| -------------- | ---------------------------- | ----------------- |
| Before #46986  | Twice, with identical bodies | Once              |
| With #46986    | Once                         | Once              |

Keep `unity-deps.txt` on the default branch unchanged and do not merge the bot
PRs while comparing. Separate branch prefixes preserve both results:

```bash
# From the baseline Renovate source checkout:
LOG_LEVEL=debug pnpm start --platform=github --onboarding=false --branch-prefix=renovate/before-46986/ --branch-prefix-old=renovate/before-46986/ --pr-hourly-limit=0 --pr-concurrent-limit=0 MindTooth/renovate-test-46986

# From the #46986 Renovate source checkout:
LOG_LEVEL=debug pnpm start --platform=github --onboarding=false --branch-prefix=renovate/with-46986/ --branch-prefix-old=renovate/with-46986/ --pr-hourly-limit=0 --pr-concurrent-limit=0 MindTooth/renovate-test-46986
```

Use the normal `RENOVATE_TOKEN` environment variable and install the checkout's
dependencies first. Add `--dry-run=full` to inspect proposed PRs without writing.
The repository configuration does not select the Renovate implementation.

## Distinct-package key collision

`key-collision-deps.txt` uses two synthetic package names and frozen registry
responses served from this repository's `registry/` directory. These are
illustrative packages, not packages published by Unity. Renovate still uses the
real `unity3d-packages` datasource, lookup, grouping, and rendering paths;
no HTTP mocks are involved.

| Package             | Installed | Target      | Notes marker     |
| ------------------- | --------- | ----------- | ---------------- |
| com.unity.foo-1.0.0 | 0.1.0     | 2.0.0       | COLLISION_NOTE_A |
| com.unity.foo       | 0.1.0     | 1.0.0-2.0.0 | COLLISION_NOTE_B |

The collision group enables prerelease updates deliberately. Both package/target
pairs produce the key
`unity3d-packages-com.unity.foo-1.0.0-2.0.0` with #46986's hyphen concatenation.
The correct PR contains both note markers. Before #46986 both should be present;
with #46986 one is incorrectly suppressed. Encoding the key as a JSON tuple
should retain both.

## Verified live results

The live self-hosted runs completed successfully on 2026-10-13 using the two
exact source commits above. Both consumed fixture commit `fe83254` for the
complete comparison, with separate branch prefixes and caches.

| Case                             | Before #46986                                                                                                                             | With #46986                                                                                                                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Repeated Input System dependency | [PR #1](https://github.com/MindTooth/renovate-test-46986/pull/1): two identical Input System 1.15.0 note sections; Cinemachine notes once | [PR #3](https://github.com/MindTooth/renovate-test-46986/pull/3): Input System notes once; Cinemachine notes once             |
| Distinct-package key collision   | [PR #2](https://github.com/MindTooth/renovate-test-46986/pull/2): both `COLLISION_NOTE_A` and `COLLISION_NOTE_B` appear                   | [PR #4](https://github.com/MindTooth/renovate-test-46986/pull/4): only `COLLISION_NOTE_B` appears; `COLLISION_NOTE_A` is lost |

Both dependencies in the collision case are updated correctly in both PRs;
the failure concerns release-note selection. Which note survives depends on
upgrade ordering.

[results.json](results.json) records the implementation SHAs, PR URLs, note
counts, marker presence, and update tables. These are real GitHub PRs generated
by Renovate; the collision registry data is synthetic and explicitly hosted
by this repository. All comparison PRs remain open and unmerged.

An unambiguous key such as `JSON.stringify([datasource, packageName, newVersion])`
avoids the collision. The local rendering/unit comparison passed with that
encoding; these four live PRs compare the original patch and its parent.
