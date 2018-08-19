# Overview for creating a brand new metric

1. Look at metric definitions at http://www.github.com/CHAOSS/metrics
2. Once you have identified a metric that you want to implement
  - Determine the data sources available for generating that metric
  - Collect your metrics dataset in a Jupyter Notebook so that you are confident the metric you deploy represents what you intend it to. 
  - We have an example Jupyter Notebook you can copy from under the jupyter directory in docs: augur/docs/jupyter
3. Move the Python code into the appropriate file under the Augur directory. For example, if you are using GHTorrent, it would go in the GHTorrent.py file. 
4. Add the API definition and documentation to Server.py
5. Write tests for your API Endpoint
6. Run Tests
7. Deploy your code
8. Check your local API docs to see if its deployed as you intend
9. *note*: At this point you could issue a pull request for the end point alone if you are not interested in building the front end visualization. 
9. Begin Front end development by adding yoru metric to 
  - AugurAPI.js
  - Modify a card (Risk, Value, Etc.) to include your metric
  - Create a line chart that points to your new metric (What if its not a line chart type of metric? We should have examples for both)
10. Deploy your new metric visualization

