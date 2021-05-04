## Code demo viewing info
Server is at 3.16.124.82  
Port likely 8080 or 8081  
To view, go to view a repo. At the bottom of the page will be a table with the following header:  
"Library Name	--- 	Files Used"  
That table contains the repo names and number of commits, which is being fed to the frontend via the metric endpoint.  
This likely will not be up until shortly after sprint 3 submit deadline.  

## Design updates compared to sprint 2:

# Clarifications 
Metric provides endpoint for frontend to use.  

# Things already handled by augur:

reading files  
determining language of files  
user interaction flow  

# Things moving forward in design:

Simplicity.  
Using regex for imports for files.  
Worker to calculate information.  

# Plans for sprint 4:

finish everything.  
Number 1 is getting worker working.  
Number 2 is getting python imports working with worker.  
Number 3 is styling chart to fit in with frontend and display loading animation like other charts.  
Number 4 is other top ten languages.  
Number 5 is trying to add unit tests for my code.  
Anything else required before end of semester.  

## Progress updates:

Worked on basics for reading imports for python  
Created metric that provides data  
Created chart on frontend repo overview to display the data  
I am going to get my code working on my augur aws server at 3.16.124.82 but it won't be fully updated by the submission time.  
I used merging and branches to keep work seperated. I mostly followed the workflow I use at work.  
So far I don't think I need to update the requirements much or scale back scope but I might be wrong.  

# Non-progress updates:

Could not start on worker given time left.  
Video has not been started on. Will try to write a summary of what I plan to cover and send it via slack.  
I have not continued with tests for my code at the moment but I would like to add them as I know how useful they are at my workplace.  

## Reflection/status:

I spent a lot more time than expected trying to figure out bugs from the code stubs I ended up having to remove and start over with from sprint 2.  
I also spent a lot of time figuring out how augur works well enough to get my code working. I found it frustrating, mostly because I didn't write much code this sprint, compared to the large amount of time I spent figuring things out. Most of my work was with the frontend with the biggest pain point being unsure how to get the metric endpoint data into something displayed to the user.  
I need help and time understanding the database better so I can make sure the worker will not break existing database stuff.  
As long as I get the worker working I should be good to finish.  
If the code is not of quality enough to be merged to master branch I would still like to keep working on it after the semester is done.  
For sprint 4 I need to try to start earlier but I don't know how easy that will be with finals. I don't have any friday finals so I should have at least four solid days with nothing else to hold me up, including the deadline day.  
