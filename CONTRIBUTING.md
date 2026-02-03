# How to Contribute

We love to pull requests from everyone! We follow the standard Git workflow of `fork -> change -> pull request -> merge -> update fork -> change ... (repeat forever)`.

If you are new to open source, we recommend GitHub's excellent guide on "[How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)". In addition, please feel free to reach out to any of the maintainers or other community members if you are struggling as we are here to help you learn!

Before getting started, please make sure you've read the [README](README.md) to get a primer on our project. Augur's documentation can be found [here](https://oss-augur.readthedocs.io/en/main/).

## Join the Community

We encourage all contributors to join the [CHAOSS Slack workspace](https://chaoss.community/kb-getting-started/) and participate in the `#wg-augur-8knot` channel. This is a great place to ask questions, get help with issues, participate in discussions, and stay updated on community meetings and planning. Don't hesitate to introduce yourself and ask for help if you get stuck!

## Opening an issue
If you're experiencing an issue with Augur or have a question you'd like help answering, please feel free to open an [issue](https://github.com/chaoss/augur/issues). To help us prevent duplicates, we kindly ask that you briefly search for your problem or question in our [issues](https://github.com/chaoss/augur/issues) before opening a new one.

Please note that if you open a bug report and your issue **does not** follow our template, we cannot help you until you have provided us all the relevant information in that format. 
Respectfully, we do not have the time to try and recreate an error given with minimal or no context, so by providing this information you are helping us help you!

### How to submit a bug report
To see the template referred to in the above section, click on **New Issue**, then click on the **Get Started** button on the **Bug Report** option.
A dialogue box populated with descriptions of what to put in each section, will pop up on a new page.
Kindly replace the descriptions with your comments to the best of your ability, and please include screenshots and error logs if applicable.

<img width="1563" alt="file1" src="https://github.com/user-attachments/assets/138e5c2e-2595-474c-9642-a48d4a6c5e1b">

<img width="1563" alt="file2" src="https://github.com/user-attachments/assets/59604aa9-d283-4fb2-8220-f3e906e6a203">

<img width="1524" alt="file3" src="https://github.com/user-attachments/assets/8f123c63-641f-4fe5-b28d-6c47ff19d1f1">


## Contributing to the source code

1. Fork and clone this repo:
```bash
$ git clone github.com:your-username/augur.git
$ cd augur/
$ git remote add upstream https://github.com/chaoss/augur.git
```

2. Follow the [development installation instructions](https://github.com/chaoss/augur/blob/main/docs/new-install.md).

3. Create a new branch
```bash
$ git checkout -b my-new-branch
```

4. Make your change(s).

5. Commit the change(s) and push to your fork
```bash
$ git add .
$ git commit -s -m "This is my first commit"
$ git push -u origin my-new-branch
```
6. Then, [submit a pull request](https://github.com/chaoss/augur/compare).

At this point, you're waiting on us. We like to at least comment on pull requests within three business days (and, typically, one business day).
Once one of our maintainers has had a chance to review your PR, we will either mark it as ```needs review``` and provide specific feedback on your changes, or we will go ahead and complete the pull request.

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

## Generative AI Policy

You can use AI tools to help with your contributions, subject to the requirements below. **You are the author, and you are accountable for the result.**

### What we require

1. **Disclose AI use.** Complete the AI disclosure section in the PR template. This is mandatory. If no AI was used, check the "No generative AI" box — that's a valid answer, and it helps us distinguish from incomplete templates.

2. **Review before submitting.** Read and test all AI-generated code or text before asking maintainers to review it. If you can't explain why a change works, it's not ready for a maintainer to review. If your changes are too long for you to read and review, that is a good indication that they are also too long for maintainers to read.

3. **Engage as yourself.** When maintainers give feedback, respond with your own understanding. Passing review comments into an LLM and pasting the output back doesn't help you learn and doesn't respect the reviewer's time.

### Why we ask

Reviewing contributions takes real time and energy. Submitting unreviewed AI output shifts that burden onto maintainers — this is sometimes called an "extractive contribution."

Disclosure matters because:

- **Respect.** Discovering a PR was unreviewed AI output after spending time on it feels like a waste. Telling us upfront lets us calibrate.
- **Research.** Augur measures open source community health. Understanding how AI tools are used in our own community is directly relevant to our mission.
- **Honesty.** Citing your tools is the same principle as citing Stack Overflow. It builds trust.

### What counts

This applies to all contributions: code, issues, PR comments, documentation.

**Disclose:** code generation, test generation, documentation drafting, AI-assisted code review, substantial refactoring suggestions.

This policy covers generative AI tools specifically. Non-generative tools like spell check, grammar correction, syntax highlighting, and basic IDE autocomplete are not in scope.

### Quality standards

AI-assisted contributions are held to the **same bar** as everything else. Good code is good code regardless of how it was written. Bad code gets rejected regardless of how it was written.

For new contributors: **start small.** Submit changes you fully understand, get feedback, and build from there. Large AI-generated PRs that you can't fully explain are hard to review and unlikely to be merged.

### Copyright

You are responsible for ensuring you have the right to contribute code under our license. AI tools can reproduce copyrighted material, and using an AI to generate it doesn't remove the copyright. Contributions found to contain improperly licensed material will be removed.

### Enforcement

This policy is about transparency, not punishment. If you forget to check the box, just update your PR when asked. All contributions, whether AI-assisted or not, are expected to follow the same standards of quality before being merged.

Patterns of submitting low-quality contributions (such as large, unreviewed, or unfocused contributions made with or without AI) that repeatedly waste maintainer time may be addressed using the [CHAOSS Code of Conduct](https://chaoss.community/code-of-conduct/), which states:

> Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## Keeping in sync with the Augur Repository

Remember to sync your fork with the ```main``` branch regularly, by taking the following steps:

- Setup your upstream branch to point to the URL of the main Augur repo ```https://github.com/chaoss/augur.git```.

- Next, in the root folder of the project, on the ```main``` branch, run:
```
git remote add upstream https://github.com/chaoss/augur.git
```
Whenever you need to make changes, make sure your ```main``` branch is in sync with the main repository, by checking out to the ```main``` branch and running:
```
git pull upstream main
git push origin master
```


## Community Resources

### Augur
- [Stable documentation (`release` branch)](https://oss-augur.readthedocs.io/en/release/)
- [Nightly/developer build documentation (`main` branch)](https://oss-augur.readthedocs.io/en/main/) (warning: this is should be considered an unstable branch and should not be used for production)
- [Live Augur demo](https://ai.chaoss.io)

### CHAOSS
- [Website](https://chaoss.community/)
- [Get Involved](https://chaoss.community/participate)
- [Join the CHAOSS Slack](https://chaoss.community/kb-getting-started/) - Join the `#wg-augur-8knot` channel to participate in discussions, meetings, and planning
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

