**Notes and ideas:**

Hit wall with libyear and deps.cloud. Both expect structured code that has dependencies listed in a single file for calculation, or at least they don't work reliability when that's not the case. Also both of them expect a single language for identifying deps. Going to take original approach of calculating dependencies on a per-file basis and combining the overall list. I could not find an alternative quickly on google and I will try to have my design flexible enough that it could be replaced with a library if needed.

My end goal is to support the top ten languages by TIOBE(April 2021) at the end of the sprints. (special exception might be needed for assembly language)

My plan is to have a very simple mechanism for identifying dependencies for a file. It will check what programming language is used for that file via extension and will check #include <x> or import x or equivalent for each language. Each step in the two-step process will be its own function in python that takes the already loaded data from augur.

stuart-sprint-2-experimental branch is for testing code just to make sure I know what works and how augur is put together enough for the final design document.



**Progress report:**

- created branches
	- stuart-sprint-2 - for sprint documents
	- stuart-sprint-2-experimental - for experimenting with stuff. not currently used due to time constraints and setup issues
	- stuart-create-framework - for making the basic worker, metric, frontend stuff to make things work
	- stuart-refine-framework - for building off of basic working code to make it prettier, work better, etc. Should be worked on after python is added.
	- stuart-add-python - for adding the first language for actually read in files
	- stuart-add-top-ten - for adding all remaining top ten TIOBE languages
- update issues opened
	- noted location of where things will happen in issues
	- closed out Load project files #5 as it is covered by augur itself
	- noted example worker to follow for Create basic augur worker for overall issue #2
	- made create augur metric #8
	- made more notes on Dependencies display #6
	- summed up how the process will work on Compute dependencies for overall project #4 and Compute dependencies for each file #3
	- created add python deps recognition support #9
	- created deps support for top ten TIOBE #10
- sprint goals:
	- sprint 3
		- have basic framework working
		- have python working
	- sprint 4
		- refine display of stuff
		- add other languages
			- add top ten TIOBE
			- add any others that are important
- Design documentation via  issues
	- some of this done from updating issues.
	- If I have time before submit, I'll update more from full design (this is placeholder and if it's still here I wasn't able to)
- Markdown in feature branch
	- working on this now
	- unsure if graphs are required but probably don't have time.
	- Will try to go over entire process from user request to output depending on how well I understand augur from reading the source
	- limited due to time
	- will be in stuart-sprint-2
	- DONE! File: /augur/sprint 2/design document markdown.md
- Code stubs
	- very basic, might not compile, just placeholders so I know where the rest will go so I can start once sprint 3 is started
	- will be done after basic draft of markdown is done
	- everything is one big commit this sprint
	- I was unable to add worker test stubs in the time remaining due to being unable to locate them. I will find and/or add a location for them and make some for my worker.
	- Following are stub locations:
	- workers/deps_worker/__init__.py
	- workers/deps_worker/runtime.py
	- workers/deps_worker/setup.py
	- workers/deps_worker/value_worker.py
	- tests/test_metrics/test_deps_metrics.py
	- augur/metrics/deps.py
- reflection
	- part of this document.
	- this is a large document this time due to time limits



**Reflection:**

I found issues with the suggested libraries and found the state of open source dep finding lacking from what limited time I could explore. Again this week I was limited in how much time I could spend on this class because of other classes. This is very frustrating because if I had more time I should have had working code by now. Sprint 3 should be better and hopefully I can get ahead of schedule so sprint 4 is more tidying things up and making it good enough for augur mainline rather than just being a student project that's abandoned. So far I've been finding this more interesting than I planned and would like to work on it in summer if I have time, however I probably won't because of already having too many projects to work on. If the work is unfinished or needs improvement before it can be part of mainline augur, I feel obligated to finish what I started after the semester ends.

