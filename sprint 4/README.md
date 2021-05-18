# Sprint 4 progress
I finished and posted my video.
I have an example database table for the worker and metric contained in dependencies.sql
I got the worker sort of working. It's having problems connecting to augur but it seems to start up.
I have dependancy detection working for most of the top ten TIOBE languages. Some languages lacking standard dependancy importing syntax or lacking it altogether are unsupported at the moment.
Current support is limited to simple import statements.
Code was successfully designed to have a simple architecture that can be extended later with more languages very easily.
I was not able to make the frontent pretty in time.
The full codepath doesn't work due to issues with making the worker function.
Finals took more time than expected so this is not as complete as I was hoping.
I will make a PR to augur dev but I don't expect it to be accepted.
I will work after the semester to finish this as I want to see it through to the end since I've already invested a bit of time and effort into making it work.

# how to run example
call "python3 test_deps.py [arg]" with a directory containing code as an argument. It will call the same code the worker calls and print the resulting list of dependancies found in the directory for all supported languages and import syntaxes.

The web server was not updated as for this sprint there was nothing new to show.

