## Running the ghdata project

There are two ways to run the project. The recommended way is from a github download that allows you to store and commit changes locally and ultimately back to your team repo. For example, if you clone a repo locally, you would then navigate to that directory and follow these four steps.

1. Start the server

  > **mwc-084037:ghdata gogginss$** python -m ghdata.server

  > Failed to open config file.

  > Default config saved to ghdata.cfg

2. Configure the ghtdata.cfg to be as below

  > **mwc-084037:ghdata gogginss$**

  > **ghdata.cfg should look like this:**

  > [Database]

  > host = opendata.missouri.edu

  > port = 3306

  > user = msr

  > pass = ghtorrent

  > name = msr
  >
  > [PublicWWW]
  >
  > apikey = 0
  >
  > [Development]

  > developer = 1

3. Restart the server
  > **mwc-084037:ghdata gogginss$** python -m ghdata.server

4. Start Front End

 > **mwc-084037:ghtdata gogginss$** cd frontend

 > **mwc-084037:frontend gogginss$** python -m http.server
