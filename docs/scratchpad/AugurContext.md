# augur Context from the Ground Up
## What is augur?
Our project is focused on building **human centered open source software health metrics** defined by collaborations with the Linux Foundation's [CHAOSS Project](http://chaoss.community) and other open source stakeholders. augur is software focused on making sense of data using Four key **human centered data science** strategies:
1. Enable comparisons. People navigate complex unknowns analogically. Let folks see how their project compares with others they are familiar with.
	- This is not ranking
	- If you start thinking about "metrics" like "rankings", you are probably going to create suboptimal metrics.
2. Make time a fundamental dimension in all metrics from the start. "Point in time scores" are useful. They are more useful if we can see how they compare historically and can be used to anticipate a trajectory.
3. All data driving visualizations should be downloadable as a .csv or other data exchange format. This is because
	- People trust metrics when they can see the underlying data
	- Proving traceability back to the CHAOSS Project's metrics standards requires easy transparency.
4. Make all the visualizations downloadable as .svg's. People want to put your visualizations in reports to explain things they care about. And ask for money. Give them the tools. That's what makes folks care about metrics.

Our core team has a long standing interest in social computing, software engineering measurement and the ethical instrumentation of online human behavior.

## Here are some more detailed links:
- Example Website (running on a development grade web server, be gentle): http://augur.sociallycompute.io
- Source Code Repository: http://github.com/OSSHealth/augur
- List of Metrics: https://github.com/chaoss/metrics/blob/master/activity-metrics-list.md
	Here are some examples:
	1. https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-response-rate.md
	2. https://github.com/chaoss/metrics/blob/master/activity-metrics/reopened-issues.md
	3. https://github.com/chaoss/metrics/blob/master/activity-metrics/issues-open.md
- Several "data providers" are available for the project. A good one to start with is GHTORRENT, because it has a number of readily populated tables in a relational structure. You can learn more about GHTorrent here: GHTorrent is explained here: https://github.com/gousiosg/github-mirror

- Notice there is SQL in those python files.
	- The Schema is GHTorrent:
	http://ghtorrent.org/relational.html
	http://ghtorrent.org/files/schema.pdf

  There are limits to ghtorrent as a data source and we are exploring strategies for incorporating higher trust data in our prototyping activities. Some of these concerns are introduced and discussed in this thread on the CHAOSS mailing list. https://lists.linuxfoundation.org/pipermail/oss-health-metrics/2017-September/000112.html
