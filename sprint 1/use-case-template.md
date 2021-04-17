## Title 
Package Dependencies Metric

## Description 
(This may be several paragraphs. Context is important. You are describing the use case in some detail, and since many of the use cases will involve users changing parameters on data visualizations, you should be exceedingly clear about this type of thing.)
Allows users to view what packages and libraries that the package being examined is dependent upon. Should detect and filter out or separately organize libraries that are part of the package in-question. Needs to be flexible due to different programming languages having different ways of importing or using libraries. This Should allow a user to look for libraries that are of known good or bad quality. This might also allow the user to know if a project is using a lot of dependencies for a very simple task.

## Triggers 
(What prompts the use case to start?)
User requesting information about what packages or libraries are used in a project.

## Actors 
(Who is involved?)
The user requesting information.
Programmers tracking libraries being used.
Open source surveyors looking to track usages of libraries in the wild.
Business person who needs to know if a project could have unexpected bugs due to the libraries it uses.

## Preconditions 
(This includes things like “data loaded”. Or, project is flagged as “of interest”; etc.)
Project is loaded and analyzed in the system. Backend is functioning and some kind of frontend is connected to augur to display information.

## Main Success Scenario (Goals)
(What does it look like when the user’s work is successful in the system?)
User is able to know if the project in question had mostly or entirely good libraries.

## Alternate Success Scenarios 
(For a data analysis and “data playing” focused project like this one, there could be several different success scenarios for each use case. “Sees visualization” is not a success scenario. “Compares four different projects on “indicator X” and saves “project trackers” for each one could be a success scenario.)
User is able to know a project is using bad or outdated libraries and knows to avoid the project or help the project change to newer and better libraries.

## Failed End Condition 
(“crashes” is not a failed end condition. “User is unable to discern the difference between two projects because they are similar on the available indicators” might be).
User is unable to know what libraries a project uses or learns nothing about the project from the data being displayed.

## Extensions
Dependencies tracker to look for dependencies that are out of date or rank poorly on metrics augur measures. Would provide more useful information at a glance compared to just displaying libraries.
More detailed breakdown of dependencies such as tracking how much a dependencies is used in the project such as % of lines of code. Tracking what functions or groups of functions are used most from certain dependencies so it can be identified what is the most important part of each libraries for a project.
Maybe a metric that measures how much a library is intertwined with a project so it can be estimated how much effort would be required for upgrading or replacing a library.

## Steps of Execution (Requirements)
1. Load project into augur.
2. Analyze project for libraries.
3. Display information to user.

## A use case diagram
(following the UML Standard for expressing use cases.)
See "use-case-diagram.png" in this folder.

## Dependent Use Cases
Unknown at current time.
