The Augur Release Process
=========================

The first step to releasing any changes is to have changes in the first place.
Augur's `CONTRIBUTING.md <https://github.com/chaoss/augur/blob/main/CONTRIBUTING.md>`__ file contains all the information that is needed to get started with topics like reporting issues, contributing code, and understanding the code review process.

This document outlines how these changes end up in an Augur release after they are merged into the `main` branch.



Release workflow:
Starting after version 0.89.3, Augur follows a workflow similar to those you may already be familiar with (such as github flow and git flow). The Augur workflow has two long-lived branches, `main` and `release` and is designed such that changes only flow in one direction - from main into release.

Branches

`main` 
The `main` branch is the primary development branch that is the target for all new pull requests. At any given point in time, this branch represents the best approximation of what the next upcoming release will look like. Since this is the active development branch, changes happen more frequently and this branch should be considered to be less stable than the `release` branch due to the possibility of breaking changes being made (and potentially reverted) between releases. It is not recommended for production deployment and is primarily intended for use by Augur contributors running their own copies against test data for development purposes.

`release`
The `release` branch is where all augur versions (after 0.89.3) are tagged. Each commit on this branch represents either a hotfix to the prior release or a new major or minor version.

Currently, Augur only officially supports the last-released version represented by the latest commit on the `release` branch. 

.. note::

    If future needs require supporting multiple Augur versions concurrently, individual numbered release branches may be made from this central `release`` branch to allow any hotfixes to be applied to each supported version independently of the others. 


The Release Process

When the next release is set to be cut, some preparation steps need to take place first, these include:
- Ensuring all features planned for that release are merged and any unrelated changes are delayed (as appropriate) until after the release.
- Creating a Pull Request to update any applicable metadata (such as version information and Changelogs) on the `main` branch.

Once all release preparation has been completed, a new Pull Request can be created to merge the main branch into the `release 'branch. This creates a final review opportunity and allows for another run of (potentially more stringent) CI jobs compared to those run on `main`, catching issues that may have come up throughout the various merges or in the process of preparing for release.

After this PR is merged, a tag is created that points to the commit on the `release` branch, effectively labeling it so that it can be returned to later if needed. This labeling process can also be the basis for additional CI jobs that build and upload the released code to distribution platforms such as Docker Hub or the GitHub Container Registry


Why?

This is done to solve a number of problems:
- having changes moving in two directions at once (i.e. features coming from main, and hotfixes coming from release) was often confusing and increased the odds that a change would be missed, such as being shipped as a hotfix but not merged into the main codebase - leading to a regression in the next release.



Special case: Hotfixes
if the fix was a hotfix:
- changelog updates and other metadata changes should be included as part of the PR
- this is where mergeify or something helps re-create the PR targeting the release branch directly. at which point the release process is followed
