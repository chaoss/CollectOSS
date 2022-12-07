<!-- @format -->

# Group Eta (7) Sprint 3 Documentation

## Links to metric issue documentation (updated with details since last sprint)

https://github.com/isaacwengler/augur/issues/1

https://github.com/isaacwengler/augur/issues/2

https://github.com/isaacwengler/augur/issues/3

https://github.com/isaacwengler/augur/issues/4

https://github.com/isaacwengler/augur/issues/5

https://github.com/isaacwengler/augur/issues/6

## Code added

File for complexity metrics:

https://github.com/isaacwengler/augur/blob/augur-new/augur/api/routes/complexity.py

This include 5 of the 6 metrics complete, including:

- [Project files](https://github.com/isaacwengler/augur/blob/augur-new/augur/api/routes/complexity.py#L20)
- [Project lines](https://github.com/isaacwengler/augur/blob/augur-new/augur/api/routes/complexity.py#L57)
- [Comment lines](https://github.com/isaacwengler/augur/blob/augur-new/augur/api/routes/complexity.py#L97)
- [Blank lines](https://github.com/isaacwengler/augur/blob/augur-new/augur/api/routes/complexity.py#L137)
- [File complexity](https://github.com/isaacwengler/augur/blob/augur-new/augur/api/routes/complexity.py#L178)

Added documentation via the `spec.yml` file:

https://github.com/isaacwengler/augur/blob/augur-new/docs/source/rest-api/spec.yml#L5147

## Testing plan

File for tests:

https://github.com/isaacwengler/augur/blob/augur-new/tests/test_routes/test_complexity_routes.py

This contains each test method. We will add on to these to check that the data is returned as expected, similar to other tests in the file. However, our server database does not have data in the `repo_labor`, so we are blocked on this.

We manually test by testing our SQL queries on the database we have access to with the `repo_labor` table, and they all work. In addition, we run our server and can hit our endpoints, which all return empty arrays, as expected, since there is no data in the table.

## Challenges Faced

Overall, the project is going well for our group. Our only challenge is the our server does not have data in the `repo_labor` table. Because of this, we can test our SQL queries (and they are working), and we test the endpoint routes when the server is running (and that is also working), but we cannot test them together yet.

## How to test what we have running

You can hit our enpoints at this link: http://eta.osshealth.io:5180/api/unstable/complexity/project_files or other corresponding links. This should display and empty array of json, `[]`, as long as Augur is running at that point (if it is not, start augur on the server).

Also, using each of the links above in the "Code Added" section, paste only the SQL into in a posgres client and run it on an Augur database with `repo_labor` data, and you will so the output.

## Team reflection

This sprint we worked well together, and were able to complete 5 out of the 6 enpoints that we needed. Along with that, we updated our issues to relect the changes. Our project is running smoothly at this point. For the final sprint, we will look to refine our tests, add the last endpoint SQL, and test everything working together. 