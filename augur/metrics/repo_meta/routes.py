#SPDX-License-Identifier: MIT

def create_repo_meta_routes(server):

    metrics = server._augur.metrics

    """
    @api {get} /repo-groups/:repo_group_id/code-changes Code Changes (Repo Group)
    @apiName code-changes-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of commits during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2018-01-01T00:00:00.000Z",
                            "commit_count": 173
                        },
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 92
                        },
                        {
                            "repo_id": 21338,
                            "repo_name": "foundation",
                            "date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 8
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.code_changes, 'code-changes')

    """
    @api {get} /repos/:repo_id/code-changes Code Changes (Repo)
    @apiName code-changes-repo
    @apiGroup Evolution
    @apiDescription Time series number of commits during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql",
                            "date": "2015-01-01T00:00:00.000Z",
                            "commit_count": 90,
                        },
                        {
                            "repo_name": "graphql",
                            "date": "2016-01-01T00:00:00.000Z",
                            "commit_count": 955,
                        }
                    ]
    """
    server.addRepoMetric(metrics.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/code-changes-lines Code Changes Lines (Repo Group)
    @apiName code-changes-lines-repo-group
    @apiGroup Evolution
    @apiDescription Time series of lines added & removed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2018-01-01T00:00:00.000Z",
                            "added": 1135,
                            "removed": 101
                        },
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2019-01-01T00:00:00.000Z",
                            "added": 872,
                            "removed": 76
                        },
                        {
                            "repo_id": 21338,
                            "repo_name": "foundation",
                            "date": "2019-01-01T00:00:00.000Z",
                            "added": 130,
                            "removed": 5
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repos/:repo_id/code-changes-lines Code Changes Lines (Repo)
    @apiName code-changes-lines-repo
    @apiGroup Evolution
    @apiDescription Time series of lines added & removed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql-js",
                            "date": "2015-06-01T00:00:00.000Z",
                            "added": 17613,
                            "removed": 106
                        },
                        {
                            "repo_name": "graphql-js",
                            "date": "2015-07-01T00:00:00.000Z",
                            "added": 9448,
                            "removed": 5081
                        },
                        {
                            "repo_name": "graphql-js",
                            "date": "2015-08-01T00:00:00.000Z",
                            "added": 6270,
                            "removed": 3833
                        }
                    ]
    """
    server.addRepoMetric(metrics.code_changes_lines, 'code-changes-lines')

    # TODO: document this
    server.addLicenseMetric(metrics.license_files, 'license-files')

    # TODO: document this
    server.addRepoMetric(metrics.sbom_download, 'sbom-download')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_group_route(repo_group_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'period': period,
    #               'begin_date': begin_date, 'end_date': end_date}

    #     data = server.transform(metrics.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/repo/<repo_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_route(repo_group_id, repo_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'repo_id': repo_id,
    #               'period': period, 'begin_date': begin_date,
    #               'end_date': end_date}

    #     data = server.transform(metrics.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    """
    @api {get} /repo-groups/:repo_group_id/sub-projects Sub-Projects (Repo Group)
    @apiName Sub-Projects(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of sub-projects.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "sub_protject_count": 2
                        }
                    ]
    """
    server.addRepoGroupMetric(
        metrics.sub_projects, 'sub-projects')

    """
    @api {get} /repos/:repo_id/sub-projects Sub-Projects (Repo)
    @apiName Sub-Projects(Repo)
    @apiGroup Evolution
    @apiDescription Number of sub-projects.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "sub_protject_count": 2
                        }
                    ]
    """
    server.addRepoMetric(
        metrics.sub_projects, 'sub-projects')

    """
    @api {get} /repo-groups/:repo_group_id/cii-best-practices-badge CII Best Practices Badge (Repo Group)
    @apiName cii-best-practices-badge-repo-group
    @apiGroup Risk
    @apiDescription The CII Best Practices Badge level.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21252,
                            "repo_name": "php-legal-licenses",
                            "badge_level": "in_progress"
                        },
                        {
                            "repo_id": 21277,
                            "repo_name": "trickster",
                            "badge_level": "passing"
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.cii_best_practices_badge, 'cii-best-practices-badge')

    """
    @api {get} /repos/:repo_id/cii-best-practices-badge CII Best Practices Badge (Repo)
    @apiName cii-best-practices-badge-repo
    @apiGroup Risk
    @apiDescription The CII Best Practices Badge level.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "trickster",
                            "badge_level": "passing"
                        }
                    ]
    """
    server.addRepoMetric(metrics.cii_best_practices_badge, 'cii-best-practices-badge')

    """
    @api {get} /repo-groups/:repo_group_id/forks Forks (Repo Group)
    @apiName forks-repo-group
    @apiGroup Risk
    @apiDescription A time series of fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "date": "2019-07-03T23:26:42.000Z",
                            "forks": 519
                        },
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "date": "2019-07-04T16:39:39.000Z",
                            "forks": 519
                        },
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-07-03T23:26:22.000Z",
                            "forks": 20
                        },
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-07-04T16:39:20.000Z",
                            "forks": 20
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.forks, 'forks')

    """
    @api {get} /repos/:repo_id/forks Forks (Repo)
    @apiName forks-repo
    @apiGroup Risk
    @apiDescription A time series of fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-03T23:27:42.000Z",
                            "forks": 843
                        },
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-04T16:40:44.000Z",
                            "forks": 844
                        }
                    ]
    """
    server.addRepoMetric(metrics.forks, 'forks')

    """
    @api {get} /repo-groups/:repo_group_id/fork-count Fork Count (Repo Group)
    @apiName fork-count-repo-group
    @apiGroup Risk
    @apiDescription Fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21364,
                            "repo_name": "irs_process_scripts",
                            "forks": 4
                        },
                        {
                            "repo_id": 21420,
                            "repo_name": "ruby-coffee-script",
                            "forks": 54
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.fork_count, 'fork-count')

    """
    @api {get} /repos/:repo_id/fork-count Fork Count (Repo)
    @apiName fork-count-repo
    @apiGroup Risk
    @apiDescription Fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "forks": 844
                        }
                    ]
    """
    server.addRepoMetric(metrics.fork_count, 'fork-count')

    """
    @api {get} /repo-groups/:repo_group_id/languages Languages (Repo Group)
    @apiName languages-repo-group
    @apiGroup Risk
    @apiDescription The primary language of the repository.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21277,
                            "primary_language": "Go"
                        },
                        {
                            "repo_id": 21252,
                            "primary_language": "PHP"
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.languages, 'languages')

    """
    @api {get} /repo-groups/:repo_group_id/languages Languages (Repo)
    @apiName languages-repo
    @apiGroup Risk
    @apiDescription The primary language of the repository.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "primary_language":"PHP"
                        }
                    ]
    """
    server.addRepoMetric(metrics.languages, 'languages')

    """
    @api {get} /repo-groups/:repo_group_id/license-count License Count (Repo Group)
    @apiName license-count-repo-group
    @apiGroup Risk
    @apiDescription The declared software package license (fetched from CII Best Practices badging data).
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "name": "ActorServiceRegistry",
                            "number_of_license": 2,
                            "file_without_licenses": true
                        },
                        {
                            "name": "adyen-api",
                            "number_of_license": 1,
                            "file_without_licenses": true
                        },
                    ]
    """
    server.addRepoGroupMetric(metrics.license_count, 'license-count')

    """
    @api {get} /repo-groups/:repo_group_id/license-count License Count (Repo)
    @apiName license-count-repo
    @apiGroup Risk
    @apiDescription The declared software package license (fetched from CII Best Practices badging data).
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        [
                            {
                                "name": "zucchini",
                                "number_of_license": 2,
                                "file_without_licenses": true
                            }
                        ]
                    ]
    """
    server.addRepoMetric(metrics.license_count, 'license-count')

    """
    @api {get} /repos/:repo_id/license-coverage License Coverage(Repo)
    @apiName license-coverage-repo
    @apiGroup Risk
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                <a href="https://github.com/chaoss/wg-risk/blob/master/metrics/License_Coverage.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "zucchini",
                            "total_files": 95,
                            "license_declared_file": 33,
                            "coverage": 0.347
                        }
                    ]
    """
    server.addRepoMetric(metrics.license_coverage, 'license-coverage')

    """
    @api {get} /repo-groups/:repo_group_id/license-coverage License Coverage(Repo Group)
    @apiName license-coverage-repo-group
    @apiGroup Risk
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/metrics/License_Coverage.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "name": "ActorServiceRegistry",
                            "total_files": 51,
                            "license_declared_files": 19,
                            "coverage": 0.373
                        },
                        {
                            "name": "adyen-api",
                            "total_files": 92,
                            "license_declared_files": 55,
                            "coverage": 0.598
                        }
                    ]
    """

    server.addRepoGroupMetric(metrics.license_coverage, 'license-coverage')

    """
    @api {get} /repos/:repo_id/license-declared License Declared(Repo)
    @apiName license-declared-repo
    @apiGroup Risk
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                <a href="https://github.com/chaoss/wg-risk/blob/master/metrics/License_Coverage.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "name": "trickster",
                            "short_name": "Apache-2.0",
                            "note": ""
                        }
                    ]
    """
    server.addRepoMetric(metrics.license_declared, 'license-declared')

    """
    @api {get} /repo-groups/:repo_group_id/license-declared License Declared(Repo Group)
    @apiName license-declared-repo-group
    @apiGroup Risk
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/metrics/License_Coverage.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                       {
                            "name": "trickster",
                            "short_name": "Apache-2.0",
                            "note": ""
                        },
                        {
                            "name": "dialyzex",
                            "short_name": "Apache-2.0",
                            "note": ""
                        }
                    ]
    """

    server.addRepoGroupMetric(metrics.license_declared, 'license-declared')

    """
    @api {get} /repo-groups/:repo_group_id/stars Stars (Repo Group)
    @apiName stars-repo-group
    @apiGroup Value
    @apiDescription A time series of stars count.
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21491,
                            "repo_name": "commons-io",
                            "date": "2019-07-03T23:23:36.000Z",
                            "stars": 600
                        },
                        {
                            "repo_id": 21491,
                            "repo_name": "commons-io",
                            "date": "2019-07-04T16:36:27.000Z",
                            "stars": 601
                        },
                        {
                            "repo_id": 21524,
                            "repo_name": "maven",
                            "date": "2019-07-03T23:21:14.000Z",
                            "stars": 1730
                        },
                        {
                            "repo_id": 21524,
                            "repo_name": "maven",
                            "date": "2019-07-04T16:34:04.000Z",
                            "stars": 1733
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.stars, 'stars')

    """
    @api {get} /repos/:repo_id/stars Stars (Repo)
    @apiName stars-repo
    @apiGroup Value
    @apiDescription A time series of stars count.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-03T23:27:42.000Z",
                            "stars": 8652
                        },
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-04T16:40:44.000Z",
                            "stars": 8653
                        }
                    ]
    """
    server.addRepoMetric(metrics.stars, 'stars')

    """
    @api {get} /repo-groups/:repo_group_id/stars-count Stars Count (Repo Group)
    @apiName stars-count-repo-group
    @apiGroup Value
    @apiDescription Stars count.
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21364,
                            "repo_name": "irs_process_scripts",
                            "stars": 20
                        },
                        {
                            "repo_id": 21420,
                            "repo_name": "ruby-coffee-script",
                            "stars": 19
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.stars_count, 'stars-count')

    """
    @api {get} /repos/:repo_id/stars-count Stars Count (Repo)
    @apiName stars-count-repo
    @apiGroup Value
    @apiDescription Stars count.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "stars": 8653
                        }
                    ]
    """
    server.addRepoMetric(metrics.stars_count, 'stars-count')

    """
    @api {get} /repo-groups/:repo_group_id/watchers Watchers (Repo Group)
    @apiName watchers-repo-group
    @apiGroup Value
    @apiDescription A time series of watchers count.
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "date": "2019-07-03T23:26:42.000Z",
                            "watchers": 60
                        },
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "date": "2019-07-04T16:39:39.000Z",
                            "watchers": 60
                        },
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-07-03T23:26:22.000Z",
                            "watchers": 19
                        },
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-07-04T16:39:20.000Z",
                            "watchers": 20
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.watchers, 'watchers')

    """
    @api {get} /repos/:repo_id/watchers Watchers (Repo)
    @apiName watchers-repo
    @apiGroup Value
    @apiDescription A time series of watchers count.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "airflow",
                            "date": "2019-07-03T23:22:26.000Z",
                            "watchers": 649
                        },
                        {
                            "repo_name": "airflow",
                            "date": "2019-07-04T16:35:16.000Z",
                            "watchers": 647
                        }
                    ]
    """
    server.addRepoMetric(metrics.watchers, 'watchers')

    """
    @api {get} /repo-groups/:repo_group_id/watchers-count Watchers Count (Repo Group)
    @apiName watchers-count-repo-group
    @apiGroup Value
    @apiDescription Watchers count.
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "watchers": 20
                        },
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "watchers": 60
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.watchers_count, 'watchers-count')

    """
    @api {get} /repos/:repo_id/watchers-count watchers Count (Repo)
    @apiName watchers-count-repo
    @apiGroup Value
    @apiDescription Watchers count.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "airflow",
                            "watchers": 649
                        }
                    ]
    """
    server.addRepoMetric(metrics.watchers_count, 'watchers-count')

    """
    @api {get} /repo-groups/:repo_group_id/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group Annual Lines of Code Ranked by New Repo in Repo Group(Repo Group)
    @apiName annual-lines-of-code-count-ranked-by-new-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "repo_name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "repo_name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoGroupMetric(metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')

    """
    @api {get} /repo-groups/:repo_group_id/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group Annual Lines of Code Ranked by New Repo in Repo Group(Repo)
    @apiName annual-lines-of-code-count-ranked-by-new-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "repo_name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "repo_name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoMetric(metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')

    """
    @api {get} /repo-groups/:repo_group_id/annual-lines-of-code-count-ranked-by-repo-in-repo-group Annual Lines of Code Ranked by Repo in Repo Group(Repo Group)
    @apiName annual-lines-of-code-count-ranked-by-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "repo_name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "repo_name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoGroupMetric(metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-repo-in-repo-group')

    """
    @api {get} /repo-groups/:repo_group_id/annual-lines-of-code-count-ranked-by-repo-in-repo-group Annual Lines of Code Ranked by Repo in Repo Group(Repo)
    @apiName annual-lines-of-code-count-ranked-by-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoMetric(metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-repo-in-repo-group')

    # TODO: document this
    server.addRepoMetric(metrics.lines_of_code_commit_counts_by_calendar_year_grouped,'lines-of-code-commit-counts-by-calendar-year-grouped')
