Augur's architecture consists of 4 primary pieces:

Backend:
  1. Python classes that know how to produce metrics from a given datasource (augur.GHTorrent, augur.Git, etc.)
  2. A main class that knows how instantiate the datasource classes (augur.Application)
  3. A WSGI server that exposes the datasources as a REST API (augur.Server, augur.runtime)

Frontend:
  4. Vue frontend, compiled with Brunch - visualizations (usually made with Vega-Lite) for the metrics exposed by the backend