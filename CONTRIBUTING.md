# How to Contribute

We love pull requests from everyone! We follow the standard Git workflow of `fork -> change -> pull request -> merge -> update fork -> change ... (repeat forever)`. If you are new to open source, we recommend GitHub's excellent guide on "[How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)". In addition, please feel free to reach out to any of the maintainers or other community members if you are struggling; we are here to help you learn!

Before getting started, please make sure you've read the [README](README.md) to get a primer on our project. Augur's documentation can be found at: https://oss-augur.readthedocs.io/en/master

## Opening an issue
If you're experience an issue with Augur or have a question you'd like help answering, please feel free to open an [issue](https://github.com/chaoss/augur/issues). To help us prevent duplicates, we kindly ask that you briefly search for your problem or question in our issues before opening a new one.

Please note that if you open a bug report and your issue does not follow our template, we cannot help you until you have provided us all the relevant information in that format. Respectfully, we do not have the time to try and recreate an error given with on minimal or no context, so by providing this information you are helping us help you! You will see this template when you open an issue; click on "Bug Report" and it will be populated with descriptions of what to put in each section. Replace the descriptions with your comments to the best of your ability, and please include screenshots and error logs if applicable.

## Contributing to the source code

0. Fork this repo, and then clone it:
```bash
$ git clone github.com:your-username/augur.git
$ cd augur/
```

1. Follow the [development installation instructions](https://oss-augur.readthedocs.io/en/master/development-guide/installation.html).

2. Make your change(s).

3. Push to your fork.

4. Then, [submit a pull request](https://github.com/chaoss/augur/compare).

At this point you're waiting on us. We like to at least comment on pull requests
within three business days (and, typically, one business day). Once one of our maintainers has had a chance to review your PR, we will either mark it as "needs review" and provide specific feedback on your changes, or we will go ahead and complete the pull request.

We require all commits to be signed off with a [Developer Certificate of Origin](https://developercertificate.org/) in accordance with the [CHAOSS charter](https://chaoss.community/about/charter/#user-content-8-intellectual-property-policy). This can be easily done by using the `-s` flag when using `git commit`. For example: `git commit -s -m "Update README.md"`. **Any pull requests containing commits that are not signed off will not be eligible for merge until the commits have been signed off.** 

## Community Resources

### Augur
- [Stable documentation (`master` branch)](https://oss-augur.readthedocs.io/en/master/)
- [Nightly/developer build documentation (`dev` branch)](https://oss-augur.readthedocs.io/en/dev/) (warning: this is should be considered an unstable branch and should not be used for production)
- [Live Augur demo](http://zephyr.osshealth.io/)

### CHAOSS
- [Website](https://chaoss.community/)
- [Get Involved](https://chaoss.community/participate)
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
