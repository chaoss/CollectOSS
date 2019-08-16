# Gathering Commit Data from Repositories using the Facade Worker
1. While in the virtual environment you used to build augur, change directories from the root of the augur project to our "repo hunting script directory" `cd docs/setup/augur-get-data/`
2. Next, install the required packages: `pip install -r requirements.txt`
3. You will notice a sample file, called [`repos-orgs-to-get.json`](./repos-orgs-to-get.json). Here you will notice that you can specify a repository directly, or a GitHub organization. The syntactical difference is subtle. 
    - Regular repositories are specified like this: 
```
      {
        "projectName": "Apache Camel",
        "projectDescription": "Camel empowers you to define routing and mediation rules in a variety of domain-specific languages",
        "projectRepository": "https://github.com/apache/camel",
        "projectWebsite": "https://camel.apache.org",
        "category": "Development"
      },
```
    - Github Organizations only specify the organization, and our script will gather **all** of the repositories in that organization: 
```
      {
        "projectName": "Rails",
        "projectDescription": "Rails Ecosystem.",
        "projectRepository": "https://github.com/rails",
        "projectWebsite": "none",
        "category": "Development"
      },
```

4. Edit the file to include the list of repositories (they do *not* have to be github repositories) and GitHub organizations you want to collect repository information for. 
5. Edit line 87 of the file `augur-projects.py` to include a github API key that you generated while logged in as your github user here: https://github.com/settings/tokens 
6. From the command line inside the same directory [`docs/setup/augur-get-data/`](`../../../docs/setup/augur-get-data/`), run `./augur-projects.py`. Its set to be executable, so it will read your `.json` file and produce three outputs: 
    - `projects.csv` will contain a list of the github organizations that were listed in your `.json` file. 
    - `repos.csv` will contain all of the repositories identified. For those projects that were not part of a GitHub organization, a unique "project id" was generated, and you will need to add that, along with any other information, to the projects.csv file itself. You can edit that file and group all repositories that are not part of an organization together into one repository id, or do something else. **Note that standalone repositories that are not part of organizations are written at the "top" of the file** `repos.csv`. 
7. Assuming you have postgresql client libraries installed from earlier in your augur installation, run this command in the directory where you created the `repos.csv` file: `psql -d {your database name} --user=augur --host={your database hostname, localhost or otherwise} --port={specify if not default port of 5432} --password -c "\copy augur_operations.repos_import FROM 'repos.csv' delimiter ',' csv;"` ... If successful, your output should look something like below: 
```
        (hopper) ➜  augur-get-data git:(dev) ✗ psql -d augur_test --user=augur --host=mudcats.augurlabs.io --port=5433 --password -c "\copy augur_operations.repos_import FROM 'repos.csv' delimiter ',' csv;"
        Password: 
        COPY 114

```

8. You now have populated the augur_operations.repos_import table with the repositories you gathered. 
9. The next step is populating the augur_data.repo_groups and augur_data.repo tables after inspecting what you imported to ensure that the repositories are grouped as you wish them to be. You can use SQL or any standard SQL client to group the repositories differently simply by changing the `projects_id` column value. All values that are the same will be added to the same repository groups in the next step. 
10. Run the following SQL to create your repository groups and repositories: 
```sql
        INSERT INTO augur_data.repo_groups( repo_group_id, rg_name, rg_description, rg_website, tool_source, tool_version, data_source, data_collection_date )
             SELECT DISTINCT projects_id, name, description, project_url, 'user import', 'augur 0.0.77.5', 'github', CURRENT_TIMESTAMP FROM augur_operations.repos_import;

        INSERT INTO augur_data.repo ( repo_id, repo_group_id, repo_git, repo_status, repo_added, tool_source, tool_version, data_source, data_collection_date ) 
            SELECT
                repos_id,
                projects_id,
                repo_url,
                status,
                CURRENT_TIMESTAMP,
                'user import',
                'augur 0.0.77.5',
                'github',
                CURRENT_TIMESTAMP 
                FROM
                    augur_operations.repos_import;

```

11. Alter the value of the `repo_directory` row in `augur_data.settings` to reflect a directory path that your augur installation has access to. It should be a new, empty directory. This is where Augur will clone your repos for the purpose of counting commits, contributions and other code oriented aspects of open source software health and sustainability. 
12. Proceed to the [Starting Workers Section](./augur-get-workers-going.md)