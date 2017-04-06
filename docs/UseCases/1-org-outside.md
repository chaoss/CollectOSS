# Title: 1-org-outside

## Background
Organizations evaluate open source communities before becoming engaged or using
open source software to satisfy a need. Depending on the context of the
need, organizations may want to ensure that licensing requirements can be met,
assess the sustainability of the community, or judge the long term alignment of
the community vision and mission with organizational needs. Inside of an
organization, employees are the decision makers and have to justify that
engaging with an open source community meets the needs of the organization and
related guidelines are met.

## Description
The user (employee) provides a URL to a GitHub repository for a community that
she wants to learn about. The software returns
[metrics](https://wiki.linuxfoundation.org/oss-health-metrics/metrics)
that indicate the health and sustainability of the repository.

## Triggers (What prompts the use case to start?)
1. A user (employee) seeks an open source solution to an organizational need and
   must assess the health and sustainability of an open source community before
   getting approval to engage or contribute.

## Actors (Who is involved?)
1. User

## Preconditions (This includes things like “data loaded”. Or, project is flagged as “of interest”; etc.)
1. User provides URL to a GitHub repository

## Main Success Scenario
1. All metrics that can be computed from the provided repository are displayed.

## Alternate Success Scenarios
1. N/A

## Failed End Condition
1. The provided URL points to a non-existent GitHub repository, metrics cannot
   be calculated, and an error message explaining the condition is shown to user.

## Extensions
1. Compare metrics between repositories.

## Steps of Execution (Requirements)
1. The use enters and submits the URL to a GitHub repository.
2. Metrics computed from the provided repository are displayed.

## Dependent Use Cases
1. N/A

## A use case diagram, following the UML Standard for expressing use cases.
![use case diagram](./diagram/ViewMetrics.png)
