# Developer Guide Part 1 - The Backend

## Structure of the Backend

Augur uses the Flask framework for its backend, which is stored in the directory `augur`. `augur/__init__.py`, `augur/server.py`, `augur/deploy.py`, and `augur/util.py` contain the components. The other `augur/*.py`files contain python funtions that return dataframes to be serialzed into json by the functions in `augur/server.py`. The titles of those files are the data sources the metrics use.

## Writing a Function for Augur

### Should I create a new .py file?

If your python function uses a new data source, create a new Python file. If you use an already implemented data source, create your new functions under that file.

#### Adding a new .py file

In the file, create a class to put your functions into, then in `augur/__init__.py` add a line with the following format

```python
from .file_name import Class
```
For example if I added a file named `augur/chaoss.py` that contains the class `Chaoss` the addition to `augur/__init__.py` would be

```python
from .choass import Chaoss
```

### Writing a function

In Augur there are metrics and timeseries metrics. For all metrics, the function should return a Dataframe that can be serialized into json. For timeseries metrics, the Dataframe needs to have a column named `date` that holds timestamps.

Once you have implemented your function in the corresponding data source file, make sure to 
```bash
pip install -e . 
``` 
once again to reload your changes.

#### Adding dependencies

If you need to add a dependency to Augur for your function, simply add the import statment to the file as usual, then in `setup.py` add the dependency to the `install_requires` list. For example, if my new function uses a package called `mizzou`, I would find the `install_requires` list:

```python
install_requires=['beautifulsoup4', 'flask', 'flask-cors', 'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 'pyevent', 'gunicorn'],
```

and add `mizzou` as such:

```python
install_requires=['beautifulsoup4', 'flask', 'flask-cors', 'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 'pyevent', 'gunicorn', 'mizzou'],
```

#### Adding tests

Augur uses pytest for tests. Tests are in the `test` directory. If you created a new file for your data source, you will also need to create a new file to test it. You can use pytest fixtures and environment variables to pass data to tests.

```python
@pytest.fixture
def chaoss():
    import augur
    chaossServer = os.getenv("CHAOSS_TEST_URL")
    assert chaossServer is not None and len(chaossServer) > 8
    return augur.Chaoss(chaossServer)
```

Now any test that tests functions in the Chaoss class will be able to access an instance of the class

```python
def test_data_source(chaoss):
    assert chaoss.data_source('argument').isin(['expected_value']).any
```

Make sure every function you write has a test.

## Creating an endpoint for a function

If you created a new data source, make sure you create an instance of your class, loading any configuration you need with the `read_config` function.

To create an endpoint for a function, in `augur/server.py`, call  `AddMetric()` or `AddTimeseries()`  as such

```python
addTimeseries(app, file_name.function_name, 'function_name')
```
for a function `foo()` in `augur/bar.py`

```python
addTimeseries(app, bar.foo, 'foo')
```
If the metric is not a timeseries metric, replace `AddTimeseries()` with `AddMetric()`

```bash

## Using the Python Debugger

The server in Augur has a built-in IPython debugger to make testing your functions easier during development.

After you have added an instance of your class to server.py, you can test it by running:

```bash
export AUGUR_INTERACTIVE=1
augur
````

Augur will load configuration and create instances of all the classes, but will drop down to IPDB shell instead of running the Flask server.

To disable the IPDB shell, simply export ```bash export AUGUR_INTERACTIVE=0``` and run `augur`.