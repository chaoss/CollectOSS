#changes I would make for next time if we were to access the API like this:
#1. mysql.connector, installed from the mysql site, is picky about which version of python you have.
#   I would likely use a different driver, such as MySQLdb
#2. Handling pagination: The api's github events are paginated.  The following code only uses page 1.
#3. My database tables contained simple sums of event types, but my code doesn't take into account whether an event was 
#   already added last time.  It would have to have a way of making sure not to duplicate data. i.e. event id / event date
#4. This code is vulnerable to SQL injection through the data it obtains from the GitHub API.
#    Future code using the API will need SQL injection protection.
#
#   Some good information on using github events api: https://developer.github.com/v3/activity/events/
#   Some good information on using github api pagination: https://developer.github.com/v3/#pagination
#
#   This code is run using Django and depends on the 4 libraries imported at top. 
#   render and HttpResponse should come with Django.
#   requests: pip install requests
#   connector:
#   I got mysql.connector for python 3.4 through the mysql installer which can be downloaded here: https://dev.mysql.com/downloads/installer/
#   I found this as an alternate site for installation, with more python options: https://dev.mysql.com/downloads/connector/python/
#
#   The database used is a mySQL database named 'github'
#   It has the table 'githubevents'
#   with three columns: an id column (unused here), 'EventName' varchar(255)  and 'EventTotal' int(11)
#   No initial data is needed in the table.

from django.shortcuts import render
from django.http import HttpResponse
import requests
import mysql.connector

def index(request):
    
    #Connect to the database and create two cursors.  At one point we will 
    #need to use a second cursor while still using SELECT data from the first.
    cnx = mysql.connector.connect(user='root', password='example_password',
                                  host='127.0.0.1',
                                  database='github')								  
    cursor = cnx.cursor(buffered=True)
    cursor2 = cnx.cursor(buffered=True)
    
    #Get the github api's events
    #If a repo is not specified, the API will return events from all public repos.
    #However, it still returns only a small number of events
    #Because the events are paginated.  If a page number is not specified,
    #only page 1 will be provided
    response = requests.get('https://api.github.com/events')
    eventData = response.json()
	
    #Create a list with the total for each event for this page load
    #and a SQL query which will be used later to determine UPDATE vs INSERT 
    #when adding the events to the database.
    getMatchingEventsSQL = ("SELECT * FROM githubevents WHERE 1 = 1")	
    eventsWithTotals = []
    needParen = False
    for thisEvent in eventData:
        if thisEvent['type'] in eventsWithTotals:
            eventIndex = eventsWithTotals.index(thisEvent['type'])
            eventsWithTotals[eventIndex - 1] += 1
        else:
            if not eventsWithTotals:
                getMatchingEventsSQL = getMatchingEventsSQL + " AND ("
            else:
                getMatchingEventsSQL = getMatchingEventsSQL + " OR "
            eventsWithTotals = eventsWithTotals + [1, thisEvent['type']]
            getMatchingEventsSQL = (getMatchingEventsSQL + "eventName = '" 
                                    + thisEvent['type'] + "'")
            needParen = True
    if needParen:
        getMatchingEventsSQL = getMatchingEventsSQL + ")"
    
    #If none of the new events match events already in the database, INSERT
    #all of them.  If some of them match, UPDATE the ones that do and add to
    #their total, then INSERT the ones that were not already in the database.
    cursor.execute(getMatchingEventsSQL)
    eventsAlreadyInserted = []
    if not cursor.rowcount:
        if eventsWithTotals:
            for key, value in enumerate(eventsWithTotals):
                if key % 2 == 0:
                    addEventSQL = ("INSERT INTO githubevents "
                                   "EventTotal, EventName) VALUES "
                                   "({},'{}')".format(eventsWithTotals[key], 
                                   eventsWithTotals[key + 1]))	
                    cursor2.execute(addEventSQL)
                    cnx.commit()
    else:
        if eventsWithTotals:
            for(gitHubEvent) in cursor:
                for key, value in enumerate(eventsWithTotals):
                    if key % 2 == 1:
                        if gitHubEvent[1] == value:
                            addEventSQL = ("UPDATE githubevents SET "
                                           "EventTotal = EventTotal + {} "
                                           "WHERE EventName = '{}'"
                                           .format(eventsWithTotals[key-1], 
                                           eventsWithTotals[key]))
                            eventsAlreadyInserted = (eventsAlreadyInserted 
                                                     + [value])
                            cursor2.execute(addEventSQL)
                            cnx.commit()
                            break
            for key, value in enumerate(eventsWithTotals):
                if key % 2 == 1:
                    if value not in eventsAlreadyInserted:
                        addEventSQL = ("INSERT INTO githubevents (EventTotal,"
                                       "EventName) VALUES ({},'{}')"
                                       .format(eventsWithTotals[key - 1], 
                                       eventsWithTotals[key]))
                        cursor2.execute(addEventSQL)
                        cnx.commit()
						
    #Construct the HTML output for event totals in the current page load.
    myHTMLOutput = "<h1>Welcome to the GitHub Events Page!</h1>"
    myHTMLOutput = (myHTMLOutput + "<h3>These are the events from the current "
                    "page load:</h3>")
    myHTMLOutput = (myHTMLOutput + "<table><tr><th>Event Type</th><th>Total "
                    "for this Page Load</th></tr>")
    for key,value in enumerate(eventsWithTotals):
        if key % 2 == 0:
            myHTMLOutput = (myHTMLOutput + "<tr><td>" 
                            + str(eventsWithTotals[key + 1]) 
                            + "</td><td>" 
                            + str(eventsWithTotals[key]) + "</td></tr>")
    myHTMLOutput = myHTMLOutput + "</table>"

    #Construct the HTML output for the event totals of past page loads.
    getEventOutputSQL = ("SELECT * from githubevents")
    cursor2.execute(getEventOutputSQL)	
    myHTMLOutput = (myHTMLOutput + "<h3>These are the events from the database"
                    " (the sum of all page loads):</h3>")
    myHTMLOutput = (myHTMLOutput + "<table><tr><th>Event Type</th><th>Total "
                    "for all Page Loads</th></tr>")	
    for(gitHubEvent) in cursor2:
        myHTMLOutput = (myHTMLOutput + "<tr><td>" + str(gitHubEvent[1]) 
                        + "</td><td>" + str(gitHubEvent[2]) + "</td></tr>")
    myHTMLOutput = myHTMLOutput + "</table>"
	
    #Close the cursors and the database connection.
    cursor2.close()
    cursor.close()
    cnx.close()
    
    #Show the HTML output.
    return HttpResponse(myHTMLOutput)
