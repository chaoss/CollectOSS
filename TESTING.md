To test ghdata, set up your environment for testing:

`
export DB_TEST_URL=mysql+pymysql://<username>:<pass>@<host>:<post>/<database>
`

then run `make test`

If you don't have both Python 2 and 3, you can run the tests individually

 - Python 2: `python2 -m pytest`
 - Python 3: `python3 -m pytest`
