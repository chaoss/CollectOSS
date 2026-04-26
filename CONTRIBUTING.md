# How to Contribute

## Join the Community
We have a public Slack channel in the CHAOSS workspace, as well as public meetings.

We encourage all contributors to join the [CHAOSS Slack workspace](https://chaoss.community/kb-getting-started/) and participate in the `#wg-collectoss-8knot` channel. Our meeting tumes are kept up to date in the Software section of the [CHAOSS Calendar](https://chaoss.community/chaoss-calendar/). We recommend subscribing to the CHAOSS Software calendar so you can automatically stay up to date with any schedule or timezone changes. If you can't attend these meetings, they are also recorded and made available on the [CHAOSS YouTube](https://www.youtube.com/@CHAOSStube).

These resources are a great way to meet the people behind the project, ask questions, get help, participate in discussions, and stay updated on community meetings and planning. Everyone is welcome, so feel free to introduce yourself and ask for help if you get stuck!


## Opening an issue
If you're experiencing an issue with CollectOSS you can search for your problem or question on our [issues](https://github.com/chaoss/collectoss/issues) page to see if someone else has already reported it. If you cannot find your issue, please feel free to [open a new one](https://github.com/chaoss/collectoss/issues/new/choose).

Our issue templates are designed to help us gather all the necessary information that we need to help troubleshoot your issue efficiently. Issues that are missing details may take longer to be fixed.

If you are new to opening issues, we recommend [opensource.guide](https://opensource.guide/how-to-contribute) and their section on [Opening Issues](https://opensource.guide/how-to-contribute/#opening-an-issue).


### How to submit a bug report
To see the template referred to in the above section, click on **New Issue**, then click on the **Get Started** button on the **Bug Report** option.
A dialogue box populated with descriptions of what to put in each section, will pop up on a new page.
Kindly replace the descriptions with your comments to the best of your ability, and please include screenshots and error logs if applicable.

<img width="1563" alt="file1" src="https://github.com/user-attachments/assets/138e5c2e-2595-474c-9642-a48d4a6c5e1b">

<img width="1563" alt="file2" src="https://github.com/user-attachments/assets/59604aa9-d283-4fb2-8220-f3e906e6a203">

<img width="1524" alt="file3" src="https://github.com/user-attachments/assets/8f123c63-641f-4fe5-b28d-6c47ff19d1f1">


## Contributing to the source code
We welcome pull requests from anyone!

We follow the same GitHub workflow that most other projects on GitHub follow: Fork -> create a branch -> make a pull request -> repeat.

Detailed instructions for making your contribution under this workflow can be found on the [GitHub Flow page](https://docs.github.com/en/get-started/using-github/github-flow). There is also an opensource.guide section on [making pull requests](https://opensource.guide/how-to-contribute/#opening-a-pull-request). If you get stuck, please ask for help in the project Slack.


## Signing-off on Commits
To contribute to this project, you must agree to the [Developer Certificate of Origin](https://developercertificate.org/) (DCO) by the [CHAOSS charter](https://chaoss.community/about/charter/#user-content-8-intellectual-property-policy) for each commit you make. The DCO is a simple statement that you, as a contributor, have the legal right to make the contribution.
To signify that you agree to the DCO for contributions, you simply add a line to each of your git commit messages. For example:
```
Signed-off-by: Jane Smith <jane.smith@example.com>
```

This can be easily done by using the `-s` flag when running the `git commit` command,

```
$ git commit -s -m “my commit message w/signoff”
```

To ensure all your commits are signed, you may choose to [configure git](https://gist.github.com/xavierfoucrier/c156027fcc6ae23bcee1204199f177da) properly by editing your global ```.gitconfig```

**Any pull requests containing commits that are not signed off will not be eligible for merge until the commits have been signed off.** 

## Keeping in sync with the CollectOSS Repository

Remember to sync your fork with the ```main``` branch regularly, by taking the following steps:

- Setup your upstream branch to point to the URL of the main CollectOSS repo ```https://github.com/chaoss/collectoss.git```.

- Next, in the root folder of the project, on the ```main``` branch, run:
```
git remote add upstream https://github.com/chaoss/collectoss.git
```
Whenever you need to make changes, make sure your ```main``` branch is in sync with the main repository, by checking out to the ```main``` branch and running:
```
git pull upstream main
git push origin master
```


## Community Resources

### CollectOSS
- [Stable documentation (`release` branch)](https://collectoss.readthedocs.io/en/release/)
- [Nightly/developer build documentation (`main` branch)](https://collectoss.readthedocs.io/en/main/) (warning: this is should be considered an unstable branch and should not be used for production)
- [Live CollectOSS demo](https://ai.chaoss.io)

### CHAOSS
- [Website](https://chaoss.community/)
- [Get Involved](https://chaoss.community/participate)
- [Join the CHAOSS Slack](https://chaoss.community/kb-getting-started/) - Join the `#wg-collectoss-8knot` channel to participate in discussions, meetings, and planning
- [Metrics](https://github.com/chaoss/metrics)
- [Evolution Metrics Working Group](https://github.com/chaoss/wg-evolution)
- [Common Metrics Working Group](https://github.com/chaoss/wg-common)
- [Risk Metrics Working Group](https://github.com/chaoss/wg-risk)
- [Value Metrics Working Group](https://github.com/chaoss/wg-value)
- [Diversity & Inclusion Metrics Working Group](https://github.com/chaoss/wg-diversity-inclusion)

## Technical Resources

### Git & GitHub
- [How to contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [GitHub's Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [GitHub's "Hello World" tutorial](https://guides.github.com/activities/hello-world/)
- [Understanding the GitHub Flow](https://guides.github.com/introduction/flow/)
- [Commit message style guidelines](https://commit.style/)
- [No-nonsense Git reference](https://rogerdudler.github.io/git-guide/) (best to have a cursory understanding of Git before hand)

### Python guides
- [Python's official tutorial](https://docs.python.org/3/tutorial/index.html)
- [Python's official style guide](https://www.python.org/dev/peps/pep-0008/)
- [Python best practices](https://gist.github.com/sloria/7001839)
- [The Zen of Python](https://www.python.org/dev/peps/pep-0020/)

### PostgreSQL guides
- [PostgreSQL installation guide](https://www.postgresql.org/docs/12/tutorial-install.html)
- [PostgreSQL official tutorial](https://www.postgresql.org/docs/)
- [PostgreSQL docker official image](https://hub.docker.com/_/postgres)
- [SQL style guide](https://docs.telemetry.mozilla.org/concepts/sql_style.html)

