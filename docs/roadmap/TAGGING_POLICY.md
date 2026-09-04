# Release and Tagging Policy

## Rule

A roadmap document is not a release.

Create a semantic-version tag only after the corresponding milestone has:
- implementation complete
- focused tests passing
- full test suite passing
- migrations validated where applicable
- documentation updated
- known limitations documented
- clean Git worktree
- release commit pushed to main

## Recommended Flow

feature branch
→ implementation
→ focused tests
→ full tests
→ pull request
→ merge to main
→ README/release documentation
→ final validation
→ annotated version tag
→ push tag
→ GitHub Release

## v3.8.0

Adding this roadmap package alone should not be tagged `v3.8.0`.

If a planning checkpoint tag is desired, use a non-release tag such as `roadmap-v4`, or simply commit the roadmap without a release tag.
