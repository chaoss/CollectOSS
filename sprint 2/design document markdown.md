**Title**

Method and metric for determining dependencies used by software project

**Description**

Looks at each source file in the project. If the file type is supported, the dependencies will be calculated. These dependencies will be reported to the user of augur who will make decisions on using or maintaining that project based on the given libraries being used.
The idea behind looking at each file and not the overall project is that for simple or poorly organized projects, they will not have a central dependencies file if it is not required by the given language. It will also allow more fine-grained look at the dependencies.

**steps in user interaction:**

1. user requests repo
2. repo is loaded in augur
3. worker starts processing files
4. each file has deps calculated
5. overall results summed up
6. metrics are calculated
7. results are displayed
8. user views deps metric

**Parts augur does:**

- user requests
- load repo
- display results

**parts I need to do:**

- worker that will call functions
- write functions
- actually support each language
- summing up the results in the worker

**overall goals**

Keeping each step simple so it's easy to change it later.
Keeping things simple so it can be finished.
Trying to keep in mind good test driven development techniques so everything is testable. 

**worker design**

Very simple and designed for having things swapped out and changed.
Just calls functions to get results.
Should be kept simple enough that my functions could later be replaced with ones from a better library.
Expects list of functions with a common calling style/interface so it can be very simple code loop and avoid huge switch statement.
Will track what language goes with each dep so if the same named library is used in multiple languages, it will show up separately.
Also it's possible that if two languages used the same file extensions, it could cause issues in the current design.

**language identifier function design**

Verifying the correct language is simply done via file extension checking against a known list.
Since function just outputs a simple yes/no, it should be able to be modified to support more advanced methods later.
Kept very simple to start to make sure the goal works and hits vast majority of files for language.

**language imports/deps calculator**

Does a very simple regex on each line to see if it matches the given matching string. Matching string will be the basic one for the given language.
If there are multiple import/include styles, the simplest one will be included first and all of them will be attempted to be added.







