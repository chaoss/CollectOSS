# Start Gathering Data
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
5. 

