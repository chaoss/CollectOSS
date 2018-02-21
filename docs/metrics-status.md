[Definitions for these metrics located here](https://github.com/chaoss/metrics/tree/master/activity-metrics)

## Metrics to Implement

#### Activity Metrics
-Pull Request Comment Duration | Average (Mean/Median)* duration of days of all the pull request comments from unique users who have made pull request comments within the analyzed period of time. Calculated as (duration = first pull request comment date – last pull request comment date).
-Commits Duration | Average (Mean/Median)* duration of days of all the commits by unique users who have made commits within the analyzed period of time. Calculated as (duration = first commit date – last commit date).
-Issue Comments Duration | Average (Mean/Median)* duration of days of all the comments a unique user have made on an issue within the analyzed period of time. Calculated as (duration = first issue comment date – last issue comment date).

#### Reward Metrics from GH Torrent:
-Pull request accepted duration | Average (Mean/Median)* duration of days of all the users made the pull request and their request has been accepted within the analyzed period of time.
-Pull request rejected duration | Average (Mean/Median)* duration of days of all the users made the pull request and their request has been rejected within the analyzed period of time.
Average Pull Request Comments | Average (Mean/Median)* number of comments on one single pull request of the focal project within the analyzed period of time.
 
#### Impact Metrics from Libraries.io
-Upstream Dependencies | Number of other projects that depend on the focal project.
-Downstream Dependencies | Number of other projects the focal project depends on.

## In Development
-Pull Request Duration | Average (Mean/Median)* duration of days of all the unique users who have made pull request within the analyzed period of time. Calculated as (user duration = first pull request date – last pull request date).

## Implemented
-Project Age | Total number of days since the start of the project. (Project start date – today’s date)
-Total Commits | Total number of commits to the project within the analyzed period of time (note: frontend implementation should deal with specification of time period)
 (does not display correctly on the front end)
-Total Watchers | Total number of watchers (subscribers) to a project.
-Total Closed Issues | A total number of closed issues within the analyzed period of time.
-Distinct Committers | Total number of unique committers within the analyzed period of time. (return NaN on frontend, returns data when executed in the IPDB shell)

## Fixes Required

#### Needs Optimization
-Issue Response Rate | time between a new issue is opened and a maintainer responds (current SQL query time: 64.5 seconds)

