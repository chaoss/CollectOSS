#SPDX-License-Identifier: MIT
"""
Creates routes for the LibrariesIO data source plugin
"""

def create_routes(server):

    librariesio = server._augur['librariesio']()

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################

    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################

    #####################################
    ###            RISK               ###
    #####################################

    #####################################
    ###            VALUE              ###
    #####################################

    #####################################
    ###           ACTIVITY            ###
    #####################################

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################   

    """
    @api {get} /:owner/:repo/dependencies Dependencies
    @apiName dependencies
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://libraries.io/">LibrariesIO</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            "full_name": "rails/rails",
                            "description": "Ruby on Rails",
                            "fork": false,
                            "created_at": "2008-04-11T02:19:47.000Z",
                            "updated_at": "2018-05-08T14:18:07.000Z",
                            "pushed_at": "2018-05-08T11:38:30.000Z",
                            "homepage": "http://rubyonrails.org",
                            "size": 163747,
                            "stargazers_count": 39549,
                            "language": "Ruby",
                            "has_issues": true,
                            "has_wiki": false,
                            "has_pages": false,
                            "forks_count": 16008,
                            "mirror_url": null,
                            "open_issues_count": 1079,
                            "default_branch": "master",
                            "subscribers_count": 2618,
                            "uuid": "8514",
                            "source_name": null,
                            "license": "MIT",
                            "private": false,
                            "contributions_count": 2627,
                            "has_readme": "README.md",
                            "has_changelog": null,
                            "has_contributing": "CONTRIBUTING.md",
                            "has_license": "MIT-LICENSE",
                            "has_coc": "CODE_OF_CONDUCT.md",
                            "has_threat_model": null,
                            "has_audit": null,
                            "status": null,
                            "last_synced_at": "2018-03-31T12:40:28.163Z",
                            "rank": 28,
                            "host_type": "GitHub",
                            "host_domain": null,
                            "name": null,
                            "scm": "git",
                            "fork_policy": null,
                            "github_id": "8514",
                            "pull_requests_enabled": null,
                            "logo_url": null,
                            "github_contributions_count": 2627,
                            "keywords": [
                                "activejob",
                                "activerecord",
                                "framework",
                                "html",
                                "mvc",
                                "rails",
                                "ruby"
                            ],
                            "dependencies": [
                                {
                                    "project_name": "blade-sauce_labs_plugin",
                                    "name": "blade-sauce_labs_plugin",
                                    "platform": "rubygems",
                                    "requirements": "0.7.2",
                                    "latest_stable": "0.7.3",
                                    "latest": "0.7.3",
                                    "deprecated": false,
                                    "outdated": true,
                                    "filepath": "Gemfile.lock",
                                    "kind": "runtime"
                                },
                                {
                                    "project_name": "blade-qunit_adapter",
                                    "name": "blade-qunit_adapter",
                                    "platform": "rubygems",
                                    "requirements": "2.0.1",
                                    "latest_stable": "2.0.1",
                                    "latest": "2.0.1",
                                    "deprecated": false,
                                    "outdated": false,
                                    "filepath": "Gemfile.lock",
                                    "kind": "runtime"
                                }
                        ]
    """
    server.addMetric(librariesio.dependencies, 'dependencies')
    
    """
    @api {get} /:owner/:repo/dependency_stats Dependency Stats
    @apiName dependency-stats
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://libraries.io/">LibrariesIO</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "dependencies": "10",
                                "dependent_projects": "10.6K",
                                "dependent_repositories": "392K"
                            }
                        ]
    """
    server.addMetric(librariesio.dependency_stats, 'dependency_stats')

    """
    @api {get} /:owner/:repo/dependents Dependents
    @apiName dependents
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://libraries.io/">LibrariesIO</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "name": "rspec-rails",
                                "platform": "Rubygems",
                                "description": "rspec-rails is a testing framework for Rails 3+.",
                                "homepage": "https://github.com/rspec/rspec-rails",
                                "repository_url": "https://github.com/rspec/rspec-rails",
                                "normalized_licenses": [
                                    "MIT"
                                ],
                                "rank": 26,
                                "latest_release_published_at": "2017-11-20T09:27:22.144Z",
                                "latest_release_number": "3.7.2",
                                "language": "Ruby",
                                "status": null,
                                "package_manager_url": "https://rubygems.org/gems/rspec-rails",
                                "stars": 3666,
                                "forks": 732,
                                "keywords": [],
                                "latest_stable_release": {
                                    "id": 11315605,
                                    "project_id": 245284,
                                    "number": "3.7.2",
                                    "published_at": "2017-11-20T09:27:22.144Z",
                                    "created_at": "2017-11-20T09:31:11.532Z",
                                    "updated_at": "2017-11-20T09:31:11.532Z",
                                    "runtime_dependencies_count": 7
                                },
                                "latest_download_url": "https://rubygems.org/downloads/rspec-rails-3.7.2.gem",
                                "dependents_count": 4116,
                                "dependent_repos_count": 129847,
                                "versions": [
                                    {
                                        "number": "2.12.2",
                                        "published_at": "2013-01-12T18:56:40.027Z"
                                    },
                                    {
                                        "number": "2.12.1",
                                        "published_at": "2013-01-07T23:04:53.104Z"
                                    },
                                    {
                                        "number": "2.12.0",
                                        "published_at": "2012-11-13T03:37:01.354Z"
                            }
                        ]
    """
    server.addMetric(librariesio.dependents, 'dependents')
