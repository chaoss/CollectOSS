# Title: 2-org-engaged

## Background
Organizations that engage with open source communities or use open source
software want to evaluate the value and long-term sustainability of this
engagement. Depending on the context, organizations may want
to assess the engagement level of its employees in the community, identify
early warn signals about deteriorating community health, or the emergence of
risk factors over time.

## Description
The user (employee) provides a URL to a GitHub repository for a community that
she wants to evaluate. The software returns
[metrics](https://wiki.linuxfoundation.org/oss-health-metrics/metrics)
that indicate the health and sustainability of the repository.

## Triggers (What prompts the use case to start?)
1. A user (employee) seeks to assess the value of engaging with an open source
   community and the long-term sustainability to justify continued engagement
   with the community.

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
