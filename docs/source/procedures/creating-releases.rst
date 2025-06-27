The Augur Release Process
=========================


Development:

1. Developer (dev) creates a feature branch
2. dev creates PR proposing this against main
3. code gets reviewed (by humans and CI bots)
    - DCO check, tests pass
    - no merge commits present in the feature branch
    - there are no dependent PRs that need to be merged first (enforced by a bot like mergify)
4. If the PR branch falls behind main [enough to create a merge conflict and/or at all(?)], the author should rebase it to resolve the conflict before merging (super simple cases can probably be resolved in the merge commit, but if its not an obvious resolution it probably requires deeper look in a better set of git tooling than GH's UI anyway)
5. If everything looks ok, merge gets approved and merges into main


Special case: Hotfixes
if the fix was a hotfix:
- changelog updates and other metadata changes should be included as part of the PR
- this is where mergeify or something helps re-create the PR targeting the release branch directly. at which point the release process is followed


Release process

preparation

when the next release is set to be cut (pre-release/release prep):
1.  a PR is created to the main branch to update any applicable metadata (such as version information and Changelogs)
    - if the fx being released is a hotfix, this will have been part of the hotfix PR itself
2.  Once this metadata PR merges the preparation is complete for release

release
1. a new PR is manually created from the main branch to the release branch
2. CI jobs are allowed to run to ensure that the merge didnt cause any issues
    - this will likely be a faster human review since the changes already were thoroughly reviewed when they made it into main
    - This is an opportunity for some additional, more stringent CI checks to run
3. once the PR is merged to the release branch, a tag is created for that commit, labeling it as the version being released
    - This causes CI to build augur and push it to the registry
