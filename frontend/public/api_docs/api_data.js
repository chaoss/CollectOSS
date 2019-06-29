define({ "api": [
  {
    "type": "post",
    "url": "/batch",
    "title": "Batch Requests",
    "name": "Batch",
    "group": "Batch",
    "description": "<p>Returns results of batch requests POST JSON of api requests</p>",
    "version": "0.0.0",
    "filename": "../augur/server.py",
    "groupTitle": "Batch"
  },
  {
    "type": "post",
    "url": "/batch",
    "title": "Batch Request Metadata",
    "name": "BatchMetadata",
    "group": "Batch",
    "description": "<p>Returns metadata of batch requests POST JSON of API requests metadata</p>",
    "version": "0.0.0",
    "filename": "../augur/server.py",
    "groupTitle": "Batch"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issues-closed-resolution-duration",
    "title": "Closed Issue Resolution Duration (Repo)",
    "name": "Closed_Issue_Resolution_Duration_Repo_",
    "group": "Evolution",
    "description": "<p>Duration of time for issues to be resolved. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"gh_issue_number\":4223,\n        \"issue_title\":\"Cloud Native PR\",\n        \"created_at\":\"2019-05-31T07:55:44.000Z\",\n        \"closed_at\":\"2019-06-17T03:12:48.000Z\",\n        \"diffdate\":16.0\n    },\n    {\n        \"gh_issue_number\":4131,\n        \"issue_title\":\"Reduce context switching cost by optimizing thread model on consumer side.\",\n        \"created_at\":\"2019-05-23T06:18:21.000Z\",\n        \"closed_at\":\"2019-06-03T08:07:27.000Z\",\n        \"diffdate\":11.0\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-closed-resolution-duration",
    "title": "Closed Issue Resolution Duration (Repo Group)",
    "name": "Closed_Issue_Resolution_Duration_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Duration of time for issues to be resolved. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n     {\n         \"repo_name\":\"incubator-dubbo\",\n         \"gh_issue_number\":4110,\n         \"issue_title\":\"rm incubating word\",\n         \"created_at\":\"2019-05-22T03:18:13.000Z\",\n         \"closed_at\":\"2019-05-22T05:27:29.000Z\",\n         \"diffdate\":0.0\n     },\n     {\n         \"repo_name\":\"incubator-dubbo\",\n         \"gh_issue_number\":4111,\n         \"issue_title\":\"nacos registry serviceName may conflict\",\n         \"created_at\":\"2019-05-22T03:30:23.000Z\",\n         \"closed_at\":\"2019-05-23T14:36:17.000Z\",\n         \"diffdate\":1.0\n     }\n ]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-closed",
    "title": "Closed Issues New Contributors (Repo)",
    "name": "Closed_Issues_New_Contributors_Repo_",
    "group": "Evolution",
    "description": "<p>Number of persons closing an issue for the first time. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-closed.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_date\": \"2018-05-20T00:00:00.000Z\",\n        \"count\": 3\n    },\n    {\n        \"issue_date\": \"2019-06-03T00:00:00.000Z\",\n        \"count\": 23\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-first-time-closed",
    "title": "Closed Issues New Contributor (Repo Group)",
    "name": "Closed_Issues_New_Contributors_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Number of persons closing an issue for the first time. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-closed.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_date\": \"2018-05-20T00:00:00.000Z\",\n        \"count\": 3\n    },\n    {\n        \"issue_date\": \"2019-06-03T00:00:00.000Z\",\n        \"count\": 23\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/contributors",
    "title": "Contributors (Repo)",
    "name": "Contributors_Repo_",
    "group": "Evolution",
    "description": "<p>List of contributors and their contributions. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n   {\n        \"user\": 1,\n        \"commits\": 0,\n        \"issues\": 2,\n        \"commit_comments\": 0,\n        \"issue_comments\": 0,\n        \"pull_requests\": 0,\n        \"pull_request_comments\": 0,\n        \"total\": 2\n    },\n    {\n        \"user\": 2,\n        \"commits\": 0,\n        \"issues\": 2,\n        \"commit_comments\": 0,\n        \"issue_comments\": 0,\n        \"pull_requests\": 0,\n        \"pull_request_comments\": 0,\n        \"total\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/contributors",
    "title": "Contributors (Repo Group)",
    "name": "Contributors_Repo_Group_",
    "group": "Evolution",
    "description": "<p>List of contributors and their contributions. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"user\": 1,\n        \"commits\": 0,\n        \"issues\": 2,\n        \"commit_comments\": 0,\n        \"issue_comments\": 0,\n        \"pull_requests\": 0,\n        \"pull_request_comments\": 0,\n        \"total\": 2\n    },\n    {\n        \"user\": 2,\n        \"commits\": 0,\n        \"issues\": 2,\n        \"commit_comments\": 0,\n        \"issue_comments\": 0,\n        \"pull_requests\": 0,\n        \"pull_request_comments\": 0,\n        \"total\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/contributors-new",
    "title": "New Contributors (Repo)",
    "name": "New_Contributors_Repo_",
    "group": "Evolution",
    "description": "<p>Time series of number of new contributors during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"contribute_at\": \"2018-05-20T00:00:00.000Z\",\n        \"count\": 3\n    },\n    {\n        \"contribute_at\": \"2019-06-03T00:00:00.000Z\",\n        \"count\": 23\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/contributors-new",
    "title": "New Contributors (Repo Group)",
    "name": "New_Contributors_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Time series of number of new contributors during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"contribute_at\": \"2018-05-20T00:00:00.000Z\",\n        \"count\": 3\n    },\n    {\n        \"contribute_at\": \"2019-06-03T00:00:00.000Z\",\n        \"count\": 23\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/pull-requests-merge-contributor-new",
    "title": "New Contributors of Commits (Repo)",
    "name": "New_Contributors_of_Commits_Repo_",
    "group": "Evolution",
    "description": "<p>Number of persons contributing with an accepted commit for the first time. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"commit_date\": \"2018-01-01T00:00:00.000Z\",\n        \"count\": 2287\n    },\n    {\n        \"commit_date\": \"2018-02-01T00:00:00.000Z\",\n        \"count\": 1939\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/pull-requests-merge-contributor-new",
    "title": "New Contributors of Commits (Repo Group)",
    "name": "New_Contributors_of_Commits_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Number of persons contributing with an accepted commit for the first time. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"commit_date\": \"2018-01-01T00:00:00.000Z\",\n        \"count\": 5140\n    },\n    {\n        \"commit_date\": \"2019-01-01T00:00:00.000Z\",\n        \"commit_count\": 711\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-opened",
    "title": "New Contributors of Issues (Repo)",
    "name": "New_Contributors_of_Issues_Repo_",
    "group": "Evolution",
    "description": "<p>Number of persons opening an issue for the first time. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_date\": \"2018-05-20T00:00:00.000Z\",\n        \"count\": 3\n    },\n    {\n        \"issue_date\": \"2019-06-03T00:00:00.000Z\",\n        \"count\": 23\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-first-time-opened",
    "title": "New Contributors of Issues (Repo Group)",
    "name": "New_Contributors_of_Issues_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Number of persons opening an issue for the first time. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_date\": \"2018-05-20T00:00:00.000Z\",\n        \"count\": 3\n    },\n    {\n        \"issue_date\": \"2019-06-03T00:00:00.000Z\",\n        \"count\": 23\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issues-open-age",
    "title": "Open Issue Age (Repo)",
    "name": "Open_Issue_Age_Repo_",
    "group": "Evolution",
    "description": "<p>Age of open issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"gh_issue_number\":2045,\n        \"issue_title\":\"Add possibility to render partial from subfolder with inheritance\",\n        \"repo_name\":\"rails\",\n        \"datedifference\":2899.0\n    },\n    {\n        \"gh_issue_number\":2686,\n        \"issue_title\":\"Attachments not visible in mail clients when additional inline attachments present\",\n        \"repo_name\":\"rails\",\n        \"datedifference\":2856.0\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-open-age",
    "title": "Open Issue Age (Repo Group)",
    "name": "Open_Issue_Age_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Age of open issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"gh_issue_number\":1,\n        \"issue_title\":\"Property Place holder for namespaced attributes is not working\",\n        \"repo_name\":\"jrugged\",\n        \"datedifference\":2414.0\n    },\n    {\n        \"gh_issue_number\":2,\n        \"issue_title\":\"Update custom namespace to work with annotation driven config\",\n        \"repo_name\":\"jrugged\",\n        \"datedifference\":2414.0\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/sub-projects",
    "title": "Sub-Projects (Repo)",
    "name": "Sub_Projects_Repo_",
    "group": "Evolution",
    "description": "<p>Number of sub-projects. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"sub_protject_count\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/sub-projects",
    "title": "Sub-Projects (Repo Group)",
    "name": "Sub_Projects_Repo_Group_",
    "group": "Evolution",
    "description": "<p>Number of sub-projects. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"sub_protject_count\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/closed-issues-count",
    "title": "Closed Issues Count (Repo)",
    "name": "closed_issues_count_repo",
    "group": "Evolution",
    "description": "<p>Count of closed issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21681,\n        \"closed_count\": 26,\n        \"date\": \"2018-11-26T00:00:00.000Z\"\n    },\n    {\n        \"repo_id\": 21681,\n        \"closed_count\": 14,\n        \"date\": \"2018-12-03T00:00:00.000Z\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/closed-issues-count",
    "title": "Closed Issues Count (Repo Group)",
    "name": "closed_issues_count_repo_group",
    "group": "Evolution",
    "description": "<p>Count of closed issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"rg_name\": \"Apache\",\n        \"closed_count\": 4,\n        \"date\": \"2014-06-02T00:00:00.000Z\"\n    },\n    {\n        \"rg_name\": \"Apache\",\n        \"closed_count\": 6,\n        \"date\": \"2014-06-09T00:00:00.000Z\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/code-changes-lines",
    "title": "Code Changes Lines (Repo)",
    "name": "code_changes_lines_repo",
    "group": "Evolution",
    "description": "<p>Time series of lines added &amp; removed during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"commit_date\": \"2014-01-01T00:00:00.000Z\",\n        \"added\": 19,\n        \"removed\": 1\n    },\n    {\n        \"commit_date\": \"2015-01-01T00:00:00.000Z\",\n        \"added\": 429535,\n        \"removed\": 204015\n    },\n    {\n        \"commit_date\": \"2016-01-01T00:00:00.000Z\",\n        \"added\": 2739765,\n        \"removed\": 944568\n    },\n    {\n        \"commit_date\": \"2017-01-01T00:00:00.000Z\",\n        \"added\": 3945001,\n        \"removed\": 1011396\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/code-changes-lines",
    "title": "Code Changes Lines (Repo Group)",
    "name": "code_changes_lines_repo_group",
    "group": "Evolution",
    "description": "<p>Time series of lines added &amp; removed during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"commit_date\": \"2018-01-01T00:00:00.000Z\",\n        \"repo_id\": 1,\n        \"added\": 640098,\n        \"removed\": 694608\n    },\n    {\n        \"commit_date\": \"2019-01-01T00:00:00.000Z\",\n        \"repo_id\": 1,\n        \"added\": 56549,\n        \"removed\": 48962\n    },\n    {\n        \"commit_date\": \"2014-01-01T00:00:00.000Z\",\n        \"repo_id\": 25001,\n        \"added\": 19,\n        \"removed\": 1\n    },\n    {\n        \"commit_date\": \"2015-01-01T00:00:00.000Z\",\n        \"repo_id\": 25001,\n        \"added\": 429535,\n        \"removed\": 204015\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/code-changes",
    "title": "Code Changes (Repo)",
    "name": "code_changes_repo",
    "group": "Evolution",
    "description": "<p>Time series number of commits during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"commit_date\": \"2018-01-01T00:00:00.000Z\",\n        \"commit_count\": 2287\n    },\n    {\n        \"commit_date\": \"2018-02-01T00:00:00.000Z\",\n        \"commit_count\": 1939\n    },\n    {\n        \"commit_date\": \"2018-03-01T00:00:00.000Z\",\n        \"commit_count\": 1979\n    },\n    {\n        \"commit_date\": \"2018-04-01T00:00:00.000Z\",\n        \"commit_count\": 2159\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/code-changes",
    "title": "Code Changes (Repo Group)",
    "name": "code_changes_repo_group",
    "group": "Evolution",
    "description": "<p>Time series of number of commits during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"commit_date\": \"2018-01-01T00:00:00.000Z\",\n        \"repo_id\": 1,\n        \"commit_count\": 5140\n    },\n    {\n        \"commit_date\": \"2019-01-01T00:00:00.000Z\",\n        \"repo_id\": 1,\n        \"commit_count\": 711\n    },\n    {\n        \"commit_date\": \"2015-01-01T00:00:00.000Z\",\n        \"repo_id\": 25001,\n        \"commit_count\": 1071\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issue-backlog",
    "title": "Issue Backlog (Repo)",
    "name": "issue_backlog_repo",
    "group": "Evolution",
    "description": "<p>Number of issues currently open. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_backlog\": 3\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issue-backlog",
    "title": "Issue Backlog (Repo Group)",
    "name": "issue_backlog_repo_group",
    "group": "Evolution",
    "description": "<p>Number of issues currently open. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 1,\n        \"issue_backlog\": 3\n    },\n    {\n        \"repo_id\": 25001,\n        \"issue_backlog\": 32\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issue-backlog",
    "title": "Issue Duration (Repo)",
    "name": "issue_duration_repo",
    "group": "Evolution",
    "description": "<p>Time since an issue is proposed until it is closed. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_id\": 43893,\n        \"duration\": \"8 days 18:53:54.000000000\"\n    },\n    {\n        \"issue_id\": 43896,\n        \"duration\": \"0 days 01:06:31.000000000\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issue-duration",
    "title": "Issue Duration (Repo Group)",
    "name": "issue_duration_repo_group",
    "group": "Evolution",
    "description": "<p>Time since an issue is proposed until it is closed. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21682,\n        \"issue_id\": 41786,\n        \"duration\": \"0 days 00:56:26.000000000\"\n    },\n    {\n        \"repo_id\": 21682,\n        \"issue_id\": 41787,\n        \"duration\": \"0 days 13:25:04.000000000\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issue-participants",
    "title": "Issue Participants (Repo)",
    "name": "issue_participants_repo",
    "group": "Evolution",
    "description": "<p>How many persons participated in the discussion of issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_id\": 38829,\n        \"participants\": 23\n    },\n    {\n        \"issue_id\": 38830,\n        \"participants\": 8\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issue-participants",
    "title": "Issue Participants (Repo Group)",
    "name": "issue_participants_repo_group",
    "group": "Evolution",
    "description": "<p>How many persons participated in the discussion of issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21326,\n        \"issue_id\": 38803,\n        \"participants\": 11\n    },\n    {\n        \"repo_id\": 21327,\n        \"issue_id\": 26422,\n        \"participants\": 4\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issue-throughput",
    "title": "Issue Throughput (Repo)",
    "name": "issue_throughput_repo",
    "group": "Evolution",
    "description": "<p>Ratio of issues closed to total issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"throughput\": 0.301124\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issue-throughput",
    "title": "Issue Throughput (Repo Group)",
    "name": "issue_throughput_repo_group",
    "group": "Evolution",
    "description": "<p>Ratio of issues closed to total issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21682,\n        \"throughput\": 0.783692\n    },\n    {\n        \"repo_id\": 21681,\n        \"throughput\": 0.301124\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-active",
    "title": "Issues Active (Repo)",
    "name": "issues_active_repo",
    "group": "Evolution",
    "description": "<p>Time series of number of issues that showed some activity during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2015-07-01T00:00:00.000Z\",\n        \"issues\": 32\n    },\n    {\n        \"date\": \"2015-08-01T00:00:00.000Z\",\n        \"issues\": 62\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-active",
    "title": "Issues Active (Repo Group)",
    "name": "issues_active_repo_group",
    "group": "Evolution",
    "description": "<p>Time series of number of issues that showed some activity during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2019-05-01T00:00:00.000Z\",\n        \"repo_id\": 21326,\n        \"issues\": 27\n    },\n    {\n        \"date\": \"2019-05-01T00:00:00.000Z\",\n        \"repo_id\": 21327,\n        \"issues\": 54\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issues-closed",
    "title": "Issues Closed (Repo)",
    "name": "issues_closed_repo",
    "group": "Evolution",
    "description": "<p>Time series of number of issues closed during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_close_date\": \"2019-05-01T00:00:00.000Z\",\n        \"issues\": 55\n    },\n    {\n        \"issue_close_date\": \"2019-06-01T00:00:00.000Z\",\n        \"issues\": 79\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-closed",
    "title": "Issues Closed (Repo Group)",
    "name": "issues_closed_repo_group",
    "group": "Evolution",
    "description": "<p>Time series of number of issues closed during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Closed.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_close_date\": \"2019-05-01T00:00:00.000Z\",\n        \"repo_id\": 21681,\n        \"issues\": 55\n    },\n    {\n        \"issue_close_date\": \"2019-06-01T00:00:00.000Z\",\n        \"repo_id\": 21681,\n        \"issues\": 79\n    },\n    {\n        \"issue_close_date\": \"2013-02-01T00:00:00.000Z\",\n        \"repo_id\": 21682,\n        \"issues\": 3\n    },\n    {\n        \"issue_close_date\": \"2014-06-01T00:00:00.000Z\",\n        \"repo_id\": 21682,\n        \"issues\": 10\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/repos/:repo_id/issues-new",
    "title": "Issues New (Repo)",
    "name": "issues_new_repo",
    "group": "Evolution",
    "description": "<p>Time series of number of new issues opened during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_date\": \"2019-05-01T00:00:00.000Z\",\n        \"issues\": 1\n    },\n    {\n        \"issue_date\": \"2019-06-01T00:00:00.000Z\",\n        \"issues\": 31\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/issues-new",
    "title": "Issues New (Repo Group)",
    "name": "issues_new_repo_group",
    "group": "Evolution",
    "description": "<p>Time series of number of new issues opened during a certain period. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "day",
              "week",
              "month",
              "year"
            ],
            "optional": true,
            "field": "period",
            "defaultValue": "day",
            "description": "<p>Periodicity specification.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "begin_date",
            "defaultValue": "1970-1-1 0:0:0",
            "description": "<p>Beginning date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "end_date",
            "defaultValue": "current date",
            "description": "<p>Ending date specification. E.g. values: <code>2018</code>, <code>2018-05</code>, <code>2019-05-01</code></p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"issue_date\": \"2019-05-01T00:00:00.000Z\",\n        \"repo_id\": 1,\n        \"issues\": 3\n    },\n    {\n        \"issue_date\": \"2019-05-01T00:00:00.000Z\",\n        \"repo_id\": 25001,\n        \"issues\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/open-issues-count",
    "title": "Open Issues Count (Repo)",
    "name": "open_issues_count_repo",
    "group": "Evolution",
    "description": "<p>Count of open issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21681,\n        \"open_count\": 18,\n        \"date\": \"2019-04-15T00:00:00.000Z\"\n    },\n    {\n        \"repo_id\": 21681,\n        \"open_count\": 16,\n        \"date\": \"2019-04-22T00:00:00.000Z\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/open-issues-count",
    "title": "Open Issues Count (Repo Group)",
    "name": "open_issues_count_repo_group",
    "group": "Evolution",
    "description": "<p>Count of open issues. <a href=\"https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"rg_name\": \"Netflix\",\n        \"open_count\": 1,\n        \"date\": \"2017-09-11T00:00:00.000Z\"\n    },\n    {\n        \"rg_name\": \"Netflix\",\n        \"open_count\": 4,\n        \"date\": \"2019-06-10T00:00:00.000Z\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Evolution"
  },
  {
    "type": "get",
    "url": "/git/annual_commit_count_ranked_by_new_repo_in_repo_group",
    "title": "Annual Commit Count Ranked by New Repo in Repo Group",
    "name": "annual_commit_count_ranked_by_new_repo_in_repo_group",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repos_id\": 1,\n        \"net\": 2479124,\n        \"patches\": 1,\n        \"name\": \"twemoji\"\n    },\n    {\n        \"repos_id\": 63,\n        \"net\": 2477911,\n        \"patches\": 1,\n        \"name\": \"twemoji-1\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/annual_commit_count_ranked_by_repo_in_repo_group",
    "title": "Annual Commit Count Ranked by Repo in Repo Group",
    "name": "annual_commit_count_ranked_by_repo_in_repo_group",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repos_id\": 1,\n        \"name\": \"twemoji\",\n        \"net\": 2479124.0,\n        \"patches\": 1\n    },\n    {\n        \"repos_id\": 63,\n        \"name\": \"twemoji-1\",\n        \"net\": 2477911.0,\n        \"patches\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/annual_lines_of_code_count_ranked_by_new_repo_in_repo_group",
    "title": "Annual Lines of Code Count Ranked by New Repo in Repo Group",
    "name": "annual_lines_of_code_count_ranked_by_new_repo_in_repo_group",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repos_id\": 1,\n        \"net\": 2479124,\n        \"patches\": 1,\n        \"name\": \"twemoji\"\n    },\n    {\n        \"repos_id\": 63,\n        \"net\": 2477911,\n        \"patches\": 1,\n        \"name\": \"twemoji-1\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/annual_lines_of_code_count_ranked_by_repo_in_repo_group",
    "title": "Annual Lines of Code Count Ranked by Repo in Repo Group",
    "name": "annual_lines_of_code_count_ranked_by_repo_in_repo_group",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repos_id\": 1,\n        \"name\": \"twemoji\",\n        \"net\": 2479124.0,\n        \"patches\": 1\n    },\n    {\n        \"repos_id\": 63,\n        \"name\": \"twemoji-1\",\n        \"net\": 2477911.0,\n        \"patches\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/commits_by_week",
    "title": "Commits By Week",
    "name": "commits_by_week",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"author_email\": \"andrea.giammarchi@gmail.com\",\n        \"affiliation\": \"(Unknown)\",\n        \"week\": 44,\n        \"year\": 2014,\n        \"patches\": 1\n    },\n    {\n        \"author_email\": \"caniszczyk@gmail.com\",\n        \"affiliation\": \"(Unknown)\",\n        \"week\": 44,\n        \"year\": 2014,\n        \"patches\": 5\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/repos",
    "title": "Facade Downloaded Repos",
    "name": "facade_downloaded_repos",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"url\": \"github.com\\/twitter\\/twemoji\",\n        \"status\": \"Update\",\n        \"project_name\": \"Twitter\",\n        \"base64_url\": \"Z2l0aHViLmNvbS90d2l0dGVyL3R3ZW1vamk=\"\n    },\n    {\n        \"url\": \"github.com\\/twitter\\/hadoop-lzo.git\",\n        \"status\": \"Complete\",\n        \"project_name\": \"Twitter\",\n        \"base64_url\": \"Z2l0aHViLmNvbS90d2l0dGVyL2hhZG9vcC1sem8uZ2l0\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/facade_project",
    "title": "Facade Project",
    "name": "facade_project",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"name\": \"Twitter\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/changes_by_author",
    "title": "Lines Changed by Author",
    "name": "lines_changed_by_author",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"author_email\":\"s@goggins.com\",\n        \"author_date\":\"2018-05-14\",\n        \"affiliation\": \"(Unknown)\",\n        \"additions\":2,\n        \"deletions\":0,\n        \"whitespace\": 3\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/lines_changed_by_month",
    "title": "Lines Changed by Month",
    "name": "lines_changed_by_month",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"author_email\": \"agiammarchi@twitter.com\",\n        \"affiliation\": \"Twitter\",\n        \"month\": 11,\n        \"year\": 2014,\n        \"additions\": 5477,\n        \"deletions\": 50511,\n        \"whitespace\": 37\n    },\n    {\n        \"author_email\": \"andrea.giammarchi@gmail.com\",\n        \"affiliation\": \"(Unknown)\",\n        \"month\": 11,\n        \"year\": 2014,\n        \"additions\": 0,\n        \"deletions\": 0,\n        \"whitespace\": 0\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/lines_changed_by_week",
    "title": "Lines Changed by Week",
    "name": "lines_changed_by_week",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2014-11-07T00:00:00.000Z\",\n        \"additions\": 1263564,\n        \"deletions\": 1834,\n        \"whitespace\": 27375\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/lines_of_code_commit_counts_by_calendar_year_grouped",
    "title": "Lines of Code Commit Counts by Calendar Year Grouped",
    "name": "lines_of_code_commit_counts_by_calendar_year_grouped",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"net_lines_minus_whitespace\": 0,\n        \"added\": 0,\n        \"removed\": 0,\n        \"whitespace\": 0,\n        \"commits\": 0,\n        \"month\": 1,\n        \"year\": 2018\n    },\n    {\n        \"net_lines_minus_whitespace\": -11489,\n        \"added\": 1046479,\n        \"removed\": 1051389,\n        \"whitespace\": 6579,\n        \"commits\": 4,\n        \"month\": 2,\n        \"year\": 2018\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/repo_group_lines_of_code_commit_counts_calendar_year_grouped",
    "title": "Repo Group Lines of Code Commit Counts by Calendar Year Grouped",
    "name": "repo_group_lines_of_code_commit_counts_by_calendar_year_grouped",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"name\": \"pelikan\",\n        \"added\": 127,\n        \"whitespace\": 39,\n        \"removed\": 17,\n        \"net_lines_minus_whitespace\": 71,\n        \"patches\": 4,\n        \"month\": 1\n    },\n    {\n        \"name\": \"bijection\",\n        \"added\": 1,\n        \"whitespace\": 1,\n        \"removed\": 0,\n        \"net_lines_minus_whitespace\": 0,\n        \"patches\": 2,\n        \"month\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/git/unaffiliated_contributors_lines_of_code_commit_counts_by_calendar_year_grouped",
    "title": "Unaffiliated Countributors Lines of Code Commit Counts by Calendar Year Grouped",
    "name": "unaffiliated_contributors_lines_of_code_commit_counts_by_calendar_year_grouped",
    "group": "Facade__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo_url_base",
            "description": "<p>Base64 version of the URL of the GitHub repository as it appears in the Facade DB</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"added\": 53480,\n        \"whitespace\": 5141,\n        \"removed\": 20291,\n        \"net_lines_minus_whitespace\": 28048,\n        \"patches\": 180,\n        \"month\": 1,\n        \"affiliation\": \"(Unknown)\"\n    },\n    {\n        \"added\": 1,\n        \"whitespace\": 0,\n        \"removed\": 1,\n        \"net_lines_minus_whitespace\": 0,\n        \"patches\": 1,\n        \"month\": 1,\n        \"affiliation\": \"(Academic)\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/facade/routes.py",
    "groupTitle": "Facade__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/issues/closed",
    "title": "Closed Issues",
    "name": "closed_issues",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/issues-closed.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "group_by",
            "description": "<p>(default to week) allows for results to be grouped by day, week, month, or year</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2011-03-19T00:00:00.000Z\",\n        \"issues_closed\": 3\n    },\n    {\n        \"date\": \"2011-03-25T00:00:00.000Z\",\n        \"issues_closed\": 6\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/commits?group_by=:group_by",
    "title": "Code Commits",
    "name": "code_commits",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"com/chaoss/metrics/blob/master/activity-metrics/code-commits.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "group_by",
            "description": "<p>(Default to week) Allows for results to be grouped by day, week, month, or year</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2017-08-27T00:00:00.000Z\",\n        \"commits\": 44\n    },\n    {\n        \"date\": \"2017-08-20T00:00:00.000Z\",\n        \"commits\": 98\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/code_review_iteration",
    "title": "Code Review Iteration",
    "name": "code_review_iteration",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2012-05-16T00:00:00.000Z\",\n        \"iterations\": 2\n    },\n    {\n        \"date\": \"2012-05-16T00:00:00.000Z\",\n        \"iterations\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/commits/comments",
    "title": "Commit Comments",
    "name": "commit_comments",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n        {\n            \"date\": \"2008-07-10T00:00:00.000Z\",\n            \"counter\": 2\n        },\n        {\n            \"date\": \"2008-07-25T00:00:00.000Z\",\n            \"counter\": 1\n        }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/commits100",
    "title": "Commits100",
    "name": "commits100",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2017-08-13T00:00:00.000Z\",\n        \"commits\": 114\n    },\n    {\n        \"date\": \"2017-08-06T00:00:00.000Z\",\n        \"commits\": 113\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/committer_locations",
    "title": "Committer Locations",
    "name": "committer_locations",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"login\": \"rafaelfranca\",\n        \"location\": \"São Paulo, Brazil\",\n        \"commits\": 7171\n    },\n    {\n        \"login\": \"tenderlove\",\n        \"location\": \"Seattle\",\n        \"commits\": 4605\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/community_age",
    "title": "Community Age",
    "name": "community_age",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"login\": \"bonnie\",\n        \"location\": \"Rowena, TX\",\n        \"commits\": 12\n    },\n    {\n        \"login\":\"clyde\",\n        \"location\":\"Ellis County, TX\",\n        \"commits\": 12\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/community_engagement",
    "title": "Community Engagement",
    "name": "community_engagement",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2011-04-16T00:00:00.000Z\",\n        \"issues_opened\": 0,\n        \"issues_closed\": 0,\n        \"pull_requests_opened\": 32,\n        \"pull_requests_merged\": 0,\n        \"pull_requests_closed\": 19,\n        \"issues_opened_total\": 4,\n        \"issues_closed_total\": 0,\n        \"issues_closed_rate_this_window\": null,\n        \"issues_closed_rate_total\": 0,\n        \"issues_delta\": 0,\n        \"issues_open\": 4,\n        \"pull_requests_opened_total\": 284,\n        \"pull_requests_closed_total\": 242,\n        \"pull_requests_closed_rate_this_window\": 0.59375,\n        \"pull_requests_closed_rate_total\": 0.8521126761,\n        \"pull_requests_delta\": 13,\n        \"pull_requests_open\": 42\n    },\n    {\n        \"date\": \"2011-04-17T00:00:00.000Z\",\n        \"issues_opened\": 0,\n        \"issues_closed\": 0,\n        \"pull_requests_opened\": 15,\n        \"pull_requests_merged\": 1,\n        \"pull_requests_closed\": 14,\n        \"issues_opened_total\": 4,\n        \"issues_closed_total\": 0,\n        \"issues_closed_rate_this_window\": null,\n        \"issues_closed_rate_total\": 0,\n        \"issues_delta\": 0,\n        \"issues_open\": 4,\n        \"pull_requests_opened_total\": 299,\n        \"pull_requests_closed_total\": 256,\n        \"pull_requests_closed_rate_this_window\": 0.9333333333,\n        \"pull_requests_closed_rate_total\": 0.856187291,\n        \"pull_requests_delta\": 1,\n        \"pull_requests_open\": 43\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/contributing_github_organizations",
    "title": "Contributing Github Organizations",
    "name": "contributing_github_organizations",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"com/chaoss/metrics/blob/master/activity-metrics/contributing-organizations.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"contributing_org\": 4066,\n        \"commits\": 36069,\n        \"issues\": 432,\n        \"commit_comments\": 1597,\n        \"issue_comments\": 15421,\n        \"pull_requests\": 808,\n        \"pull_request_comments\": 0,\n        \"total\": 54327,\n        \"count\": 35\n    },\n    {\n        \"contributing_org\": 16465,\n        \"commits\": 39111,\n        \"issues\": 332,\n        \"commit_comments\": 524,\n        \"issue_comments\": 3188,\n        \"pull_requests\": 57,\n        \"pull_request_comments\": 18,\n        \"total\": 43230,\n        \"count\": 11\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/contribution_acceptance",
    "title": "Contribution Acceptance",
    "name": "contribution_acceptance",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://www.github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2012-05-16T00:00:00.000Z\",\n        \"ratio\": 1.1579\n    },\n    {\n        \"date\": \"2012-05-20T00:00:00.000Z\",\n        \"ratio\": 1.3929\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/contributions",
    "title": "Contributions",
    "name": "contributions",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ],
        "String": [
          {
            "group": "String",
            "optional": false,
            "field": "user",
            "description": "<p>Limit results to the given user's contributions</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n     {\n         \"date\": \"2004-11-24T00:00:00.000Z\",\n         \"commits\": 3,\n         \"pull_requests\": null,\n         \"issues\": null,\n         \"commit_comments\": null,\n         \"pull_request_comments\": null,\n         \"issue_comments\": null,\n         \"total\": null\n     },\n     {\n         \"date\": \"2004-11-30T00:00:00.000Z\",\n         \"commits\": 7,\n         \"pull_requests\": null,\n         \"issues\": null,\n         \"commit_comments\": null,\n         \"pull_request_comments\": null,\n         \"issue_comments\": null,\n         \"total\": null\n     }\n ]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/contributors",
    "title": "Total Contributions by User",
    "name": "contributors",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n     {\n         \"user\": 8153,\n         \"commits\": 6825,\n         \"issues\": 127,\n         \"commit_comments\": 313,\n         \"issue_comments\": 13152,\n         \"pull_requests\": 1,\n         \"pull_request_comments\": 0,\n         \"total\": 20418\n     },\n     {\n         \"user\": 45381,\n         \"commits\": 2192,\n         \"issues\": 202,\n         \"commit_comments\": 130,\n         \"issue_comments\": 4633,\n         \"pull_requests\": 0,\n         \"pull_request_comments\": 0,\n         \"total\": 7157\n     }\n ]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/fakes",
    "title": "Fakes",
    "name": "fakes",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2010-04-09T00:00:00.000Z\",\n        \"fakes\": 1\n    },\n    {\n        \"date\": \"2010-04-27T00:00:00.000Z\",\n        \"fakes\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/issues/response_time",
    "title": "First Response To Issue Duration",
    "name": "first_response_to_issue_duration",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"id\": 2,\n        \"opened\": \"2012-01-19T05:24:55.000Z\",\n        \"first_commented\": \"2012-01-19T05:30:13.000Z\",\n        \"pull_request\": 0,\n        \"minutes_to_comment\": 5\n    },\n    {\n        \"id\": 3,\n        \"opened\": \"2012-01-26T15:07:56.000Z\",\n        \"first_commented\": \"2012-01-26T15:09:28.000Z\",\n        \"pull_request\": 0,\n        \"minutes_to_comment\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/forks?group_by=:group_by",
    "title": "Forks",
    "name": "forks",
    "group": "GHTorrent__Legacy_",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "group_by",
            "description": "<p>(Default to week) Allows for results to be grouped by day, week, month, or year</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/forks.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2017-08-20T00:00:00.000Z\",\n        \"projects\": 48\n    },\n    {\n        \"date\": \"2017-08-13T00:00:00.000Z\",\n        \"projects\": 53\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/issues/activity",
    "title": "Issue Activity",
    "name": "issue_activity",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"0000-00-00\",\n        \"count\": 2,\n        \"action\": \"closed\"\n    },\n    {\n        \"date\": \"0000-00-00\",\n        \"count\": 70,\n        \"action\": \"opened\"\n    },\n    {\n        \"date\": \"0000-00-00\",\n        \"count\": 0,\n        \"action\": \"reopened\"\n    },\n    {\n        \"date\": \"0000-00-00\",\n        \"count\": 68,\n        \"action\": \"open\"\n    },\n    {\n        \"date\": \"2009-04-01T00:00:00.000Z\",\n        \"count\": 0,\n        \"action\": \"closed\"\n    },\n    {\n        \"date\": \"2009-04-01T00:00:00.000Z\",\n        \"count\": 29,\n        \"action\": \"opened\"\n    },\n    {\n        \"date\": \"2009-04-01T00:00:00.000Z\",\n        \"count\": 0,\n        \"action\": \"reopened\"\n    },\n    {\n        \"date\": \"2009-04-01T00:00:00.000Z\",\n        \"count\": 29,\n        \"action\": \"open\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/issue_comments",
    "title": "Issue Comments",
    "name": "issue_comments",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-comments.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2009-04-05T00:00:00.000Z\",\n        \"counter\": 3\n    },\n    {\n        \"date\": \"2009-04-16T00:00:00.000Z\",\n        \"counter\": 5\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/maintainer_response_time",
    "title": "Maintainer Response to Merge Request Duration",
    "name": "maintainer_response_to_merge_request_duration",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/augurlabs/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2011-05-10T00:00:00.000Z\",\n        \"days\": 32\n    },\n    {\n        \"date\": \"2011-05-21T00:00:00.000Z\",\n        \"days\": 3\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/new_contributing_github_organizations",
    "title": "New Contributing Github Organizations",
    "name": "new_github_contributing_organizations",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/augurlabs/metrics/blob/master/activity-metrics/new-contributing-organizations.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2008-04-12T23:43:38.000Z\",\n        \"organizations\": 1\n    },\n    {\n        \"date\": \"2008-08-23T15:05:52.000Z\",\n        \"organizations\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/new_watchers",
    "title": "New Watchers",
    "name": "new_watchers",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2010-04-09T00:00:00.000Z\",\n        \"new_watchers\": 1\n    },\n    {\n        \"date\": \"2010-04-27T00:00:00.000Z\",\n        \"new_watchers\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/issues",
    "title": "Open Issues",
    "name": "open_issues",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/open-issues.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "group_by",
            "description": "<p>(default to week) allows for results to be grouped by day, week, month, or year</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "owner",
            "description": "<p>username of the owner of the github repository</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo",
            "description": "<p>name of the github repository</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/project_age",
    "title": "Project Age",
    "name": "project_age",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n    \"date\": \"2008-04-11T00:00:00.000Z\",\n    \"{0}\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/acceptance_rate",
    "title": "Pull Request Acceptance Rate",
    "deprecated": {
      "content": "This endpoint was removed. Please use (#Experimental:community-engagement)"
    },
    "name": "pull_request_acceptance_rate",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2010-09-11T00:00:00.000Z\",\n        \"rate\": 0.3333\n    },\n    {\n        \"date\": \"2010-09-13T00:00:00.000Z\",\n        \"rate\": 0.3333\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/response_time",
    "title": "Most Recent Response To Pull Requests Duration",
    "name": "pull_request_comment_duration_",
    "group": "GHTorrent__Legacy_",
    "description": "<p>&lt;a href=&quot;https://github.com/chaoss/wg-gmd/blob/master/metrics/pull-requests-comment-duration.md&gt;CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"pull_request_id\": 1709,\n        \"opened\": \"2012-01-19T05:24:55.000Z\",\n        \"first_commented\": \"2012-01-19T05:30:13.000Z\",\n        \"minutes_to_first_pr_comment\": 5,\n        \"most_recent_comment\": \"2012-01-19T05:30:13.000Z\",\n        \"minutes_to_recent_pr_comment\": 5\n\n    },\n    {\n        \"pull_request_id\": 1721,\n        \"opened\": \"2012-01-19T05:24:55.000Z\",\n        \"first_commented\": \"2012-01-19T05:30:13.000Z\",\n        \"minutes_to_first_pr_comment\": 5,\n        \"most_recent_comment\": \"2012-01-19T05:30:13.000Z\",\n        \"minutes_to_recent_pr_comment\": 5\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/comments?group_by=:group_by",
    "title": "Pull Request Comments",
    "name": "pull_request_comments",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-request-comments.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2011-11-15T00:00:00.000Z\",\n        \"counter\": 3\n    },\n    {\n        \"date\": \"2011-11-25T00:00:00.000Z\",\n        \"counter\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/closed",
    "title": "Pull Requests Closed",
    "name": "pull_requests_closed",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-closed.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2013-01-09T00:00:00.000Z\",\n        \"pull_requests\": 3\n    },\n    {\n        \"date\": \"2016-01-14T00:00:00.000Z\",\n        \"pull_requests\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls/made_closed",
    "title": "Pull Requests Made/Closed",
    "name": "pull_requests_made_closed",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-made-closed.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2010-09-11T00:00:00.000Z\",\n        \"rate\": 0.3333\n    },\n    {\n        \"date\": \"2010-09-13T00:00:00.000Z\",\n        \"rate\": 0.3333\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/pulls",
    "title": "Pull Requests Open",
    "name": "pull_requests_open",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-open.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2013-01-09T00:00:00.000Z\",\n        \"pull_requests\": 3\n    },\n    {\n        \"date\": \"2016-01-14T00:00:00.000Z\",\n        \"pull_requests\": 1\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/total_committers",
    "title": "Total Committers",
    "name": "total_committers",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2004-11-24T00:00:00.000Z\",\n        \"total_total_committers\": 1\n    },\n    {\n        \"date\": \"2005-02-18T00:00:00.000Z\",\n        \"total_total_committers\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/total_watchers",
    "title": "Total Watchers",
    "name": "total_watchers",
    "group": "GHTorrent__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2005-08-26T00:00:00.000Z\",\n        \"total_total_watchers\": 5\n    },\n    {\n        \"date\": \"2005-09-02T00:00:00.000Z\",\n        \"total_total_watchers\": 6\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/watchers",
    "title": "Watchers",
    "name": "watchers",
    "group": "GHTorrent__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/metrics/blob/master/activity-metrics/activity-metrics-list.md\">CHAOSS Metric Definition</a>. Source: <a href=\"http://ghtorrent.org/\">GHTorrent</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2017-08-23T00:00:00.000Z\",\n        \"watchers\": 86\n    },\n    {\n        \"date\": \"2017-08-16T00:00:00.000Z\",\n        \"watchers\": 113\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "GHTorrent__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/bus_factor",
    "title": "Bus Factor",
    "name": "bus_factor",
    "group": "GitHub_API__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://developer.github.com/\">GitHub API</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "threshold",
            "description": "<p>Percentage used to determine how many lost people would kill the project</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"best\": \"5\",\n        \"worst\": \"1\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/downloads",
    "title": "Downloads",
    "name": "downloads",
    "group": "GitHub_API__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://developer.github.com/\">GitHub API</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2018-06-14\",\n        \"downloads\": 129148\n    },\n    {\n        \"date\": \"2018-06-13\",\n        \"downloads\": 131262\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/downloads/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/githubapi/issues/closed",
    "title": "Closed Issues",
    "name": "githubapi_closed_issues",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/wg-gmd/blob/master/metrics/issues-closed.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"created_at\": \"2019-01-09T00:00:00.000Z\",\n        \"count\": 1\n    },\n    {\n        \"created_at\": \"2019-01-10T00:00:00.000Z\",\n        \"count\": 2\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/githubapi/commits",
    "title": "Code Commits",
    "name": "githubapi_code_commits",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/wg-gmd/blob/master/activity-metrics/code-commits.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"created_at\": \"2017-01-30T00:00:00.000Z\",\n        \"count\": 6\n    },\n    {\n        \"created_at\": \"2017-01-31T00:00:00.000Z\",\n        \"count\": 14\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/githubapi/contributors",
    "title": "List of Contributors & their Contributions",
    "name": "githubapi_contributors",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/wg-gmd/blob/master/metrics/contributors.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"login\": \"howderek\",\n        \"contributions\": 372\n    },\n    {\n        \"login\": \"ccarterlandis\",\n        \"contributions\": 190\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/githubapi/issues",
    "title": "Issues Opened",
    "name": "githubapi_issues_opened",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/wg-gmd/blob/master/metrics/issues-open.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"created_at\": \"2019-02-28T00:00:00.000Z\",\n        \"count\": 4\n    },\n    {\n        \"created_at\": \"2019-03-01T00:00:00.000Z\",\n        \"count\": 1\n    },\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/githubapi/pull_requests_closed",
    "title": "Pull Requests Closed",
    "name": "githubapi_pull_requests_Closed",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/ComputationalMystics/wg-gmd/blob/master/activity-metrics/pull-requests-closed.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "{'count': 6}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/githubapi/pull_requests_merged",
    "title": "Pull Requests Merged",
    "name": "githubapi_pull_requests_merged",
    "group": "GitHub_API__Legacy_",
    "description": "<p>Count of pull requests merged.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "{'count': 84}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/githubapi/pull_requests_open",
    "title": "Pull Requests Open",
    "name": "githubapi_pull_requests_open",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/ComputationalMystics/wg-gmd/blob/master/activity-metrics/pull-requests-open.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "{'count': 3}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/lines_changed",
    "title": "Lines of Code Changed",
    "name": "lines_of_code_changed",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/augurlabs/metrics/blob/master/activity-metrics/lines-of-code-changed.md\">CHAOSS Metric Definition</a>.  Source: <a href=\"https://developer.github.com/\">GitHub API</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        'date': '2015-11-01T00:00:00Z',\n        'lines_changed': 396137.0\n    },\n    {\n        'date': '2015-11-08T00:00:00Z',\n        'lines_changed': 3896.0\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/tags/major",
    "title": "Major Tags",
    "name": "major_tags",
    "group": "GitHub_API__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://developer.github.com/\">GitHub API</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2008-04-10T17:25:14-07:00\",\n        \"release\": \"v1.0.0\"\n    },\n    {\n        \"date\": \"2008-04-10T17:25:47-07:00\",\n        \"release\": \"v2.0.0\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/githubapi/repository_size",
    "title": "Repository Size",
    "name": "repository_size",
    "group": "GitHub_API__Legacy_",
    "description": "<p><a href=\"https://github.com/chaoss/wg-gmd/blob/master/metrics/archived_metrics/repository-size.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"best\": \"5\",\n        \"worst\": \"1\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/timeseries/tags/major",
    "title": "Tages",
    "name": "tags",
    "group": "GitHub_API__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://developer.github.com/\">GitHub API</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"date\": \"2008-04-10T17:25:06-07:00\",\n        \"release\": \"v0.9.1\"\n    },\n    {\n        \"date\": \"2008-04-10T17:25:07-07:00\",\n        \"release\": \"v0.9.2\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/githubapi/routes.py",
    "groupTitle": "GitHub_API__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/dependencies",
    "title": "Dependencies",
    "name": "dependencies",
    "group": "Libraries_io__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://libraries.io/\">LibrariesIO</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    \"full_name\": \"rails/rails\",\n    \"description\": \"Ruby on Rails\",\n    \"fork\": false,\n    \"created_at\": \"2008-04-11T02:19:47.000Z\",\n    \"updated_at\": \"2018-05-08T14:18:07.000Z\",\n    \"pushed_at\": \"2018-05-08T11:38:30.000Z\",\n    \"homepage\": \"http://rubyonrails.org\",\n    \"size\": 163747,\n    \"stargazers_count\": 39549,\n    \"language\": \"Ruby\",\n    \"has_issues\": true,\n    \"has_wiki\": false,\n    \"has_pages\": false,\n    \"forks_count\": 16008,\n    \"mirror_url\": null,\n    \"open_issues_count\": 1079,\n    \"default_branch\": \"master\",\n    \"subscribers_count\": 2618,\n    \"uuid\": \"8514\",\n    \"source_name\": null,\n    \"license\": \"MIT\",\n    \"private\": false,\n    \"contributions_count\": 2627,\n    \"has_readme\": \"README.md\",\n    \"has_changelog\": null,\n    \"has_contributing\": \"CONTRIBUTING.md\",\n    \"has_license\": \"MIT-LICENSE\",\n    \"has_coc\": \"CODE_OF_CONDUCT.md\",\n    \"has_threat_model\": null,\n    \"has_audit\": null,\n    \"status\": null,\n    \"last_synced_at\": \"2018-03-31T12:40:28.163Z\",\n    \"rank\": 28,\n    \"host_type\": \"GitHub\",\n    \"host_domain\": null,\n    \"name\": null,\n    \"scm\": \"git\",\n    \"fork_policy\": null,\n    \"github_id\": \"8514\",\n    \"pull_requests_enabled\": null,\n    \"logo_url\": null,\n    \"github_contributions_count\": 2627,\n    \"keywords\": [\n        \"activejob\",\n        \"activerecord\",\n        \"framework\",\n        \"html\",\n        \"mvc\",\n        \"rails\",\n        \"ruby\"\n    ],\n    \"dependencies\": [\n        {\n            \"project_name\": \"blade-sauce_labs_plugin\",\n            \"name\": \"blade-sauce_labs_plugin\",\n            \"platform\": \"rubygems\",\n            \"requirements\": \"0.7.2\",\n            \"latest_stable\": \"0.7.3\",\n            \"latest\": \"0.7.3\",\n            \"deprecated\": false,\n            \"outdated\": true,\n            \"filepath\": \"Gemfile.lock\",\n            \"kind\": \"runtime\"\n        },\n        {\n            \"project_name\": \"blade-qunit_adapter\",\n            \"name\": \"blade-qunit_adapter\",\n            \"platform\": \"rubygems\",\n            \"requirements\": \"2.0.1\",\n            \"latest_stable\": \"2.0.1\",\n            \"latest\": \"2.0.1\",\n            \"deprecated\": false,\n            \"outdated\": false,\n            \"filepath\": \"Gemfile.lock\",\n            \"kind\": \"runtime\"\n        }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/librariesio/routes.py",
    "groupTitle": "Libraries_io__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/dependency_stats",
    "title": "Dependency Stats",
    "name": "dependency_stats",
    "group": "Libraries_io__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://libraries.io/\">LibrariesIO</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"dependencies\": \"10\",\n        \"dependent_projects\": \"10.6K\",\n        \"dependent_repositories\": \"392K\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/librariesio/routes.py",
    "groupTitle": "Libraries_io__Legacy_"
  },
  {
    "type": "get",
    "url": "/:owner/:repo/dependents",
    "title": "Dependents",
    "name": "dependents",
    "group": "Libraries_io__Legacy_",
    "description": "<p>This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href=\"https://libraries.io/\">LibrariesIO</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "owner",
            "description": "<p>Username of the owner of the GitHub repository</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "repo",
            "description": "<p>Name of the GitHub repository</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"name\": \"rspec-rails\",\n        \"platform\": \"Rubygems\",\n        \"description\": \"rspec-rails is a testing framework for Rails 3+.\",\n        \"homepage\": \"https://github.com/rspec/rspec-rails\",\n        \"repository_url\": \"https://github.com/rspec/rspec-rails\",\n        \"normalized_licenses\": [\n            \"MIT\"\n        ],\n        \"rank\": 26,\n        \"latest_release_published_at\": \"2017-11-20T09:27:22.144Z\",\n        \"latest_release_number\": \"3.7.2\",\n        \"language\": \"Ruby\",\n        \"status\": null,\n        \"package_manager_url\": \"https://rubygems.org/gems/rspec-rails\",\n        \"stars\": 3666,\n        \"forks\": 732,\n        \"keywords\": [],\n        \"latest_stable_release\": {\n            \"id\": 11315605,\n            \"project_id\": 245284,\n            \"number\": \"3.7.2\",\n            \"published_at\": \"2017-11-20T09:27:22.144Z\",\n            \"created_at\": \"2017-11-20T09:31:11.532Z\",\n            \"updated_at\": \"2017-11-20T09:31:11.532Z\",\n            \"runtime_dependencies_count\": 7\n        },\n        \"latest_download_url\": \"https://rubygems.org/downloads/rspec-rails-3.7.2.gem\",\n        \"dependents_count\": 4116,\n        \"dependent_repos_count\": 129847,\n        \"versions\": [\n            {\n                \"number\": \"2.12.2\",\n                \"published_at\": \"2013-01-12T18:56:40.027Z\"\n            },\n            {\n                \"number\": \"2.12.1\",\n                \"published_at\": \"2013-01-07T23:04:53.104Z\"\n            },\n            {\n                \"number\": \"2.12.0\",\n                \"published_at\": \"2012-11-13T03:37:01.354Z\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/librariesio/routes.py",
    "groupTitle": "Libraries_io__Legacy_"
  },
  {
    "type": "get",
    "url": "metrics/status/filter?ID=:ID&tag=:tag&group=:group&backend_status=:backend_status&frontend_status=:frontend_status&source=:source&metric_type=:metric_type&is_defined=:is_defined",
    "title": "Filtered Metrics Status",
    "name": "filter_metrics_status",
    "group": "Metrics_Status",
    "description": "<p>Metrics Status that allows for filtering of the results via the query string. Filters can be combined.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "ID",
            "description": "<p>Returns the status of the metric that matches this ID</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "tag",
            "description": "<p>Returns all the statuses of all metrics that have this tag</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "group",
            "description": "<p>Returns all the metrics in this metric grouping</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "\"unimplemented\"",
              "\"undefined\"",
              "\"implemented\""
            ],
            "optional": true,
            "field": "backend_status",
            "description": ""
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "\"unimplemented\"",
              "\"implemented\""
            ],
            "optional": true,
            "field": "frontend_status",
            "description": ""
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "source",
            "description": "<p>Returns the statuses of all metrics from this data source</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": true,
            "field": "metric_type",
            "description": "<p>Returns the statuses of the metrics of this metric type</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "allowedValues": [
              "\"true\"",
              "\"false\""
            ],
            "optional": true,
            "field": "is_defined",
            "description": "<p>Returns the statuses of metrics that are or aren't defined</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Sample Query String: ",
          "content": "metrics/status/filter?group=growth-maturity-decline&metric_type=metric",
          "type": "string"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"ID\": \"ghtorrentplus-closed-issue-resolution-duration\",\n        \"tag\": \"closed-issue-resolution-duration\",\n        \"name\": \"Closed Issue Resolution Duration\",\n        \"group\": \"growth-maturity-decline\",\n        \"backend_status\": \"implemented\",\n        \"frontend_status\": \"unimplemented\",\n        \"endpoint\": \"/api/unstable/<owner>/<repo>/issues/time_to_close\",\n        \"source\": \"ghtorrentplus\",\n        \"metric_type\": \"metric\",\n        \"url\": \"activity-metrics/closed-issue-resolution-duration.md\",\n        \"is_defined\": \"true\"\n    },\n    {\n        \"ID\": \"ghtorrent-contributors\",\n        \"tag\": \"contributors\",\n        \"name\": \"Contributors\",\n        \"group\": \"growth-maturity-decline\",\n        \"backend_status\": \"implemented\",\n        \"frontend_status\": \"implemented\",\n        \"endpoint\": \"/api/unstable/<owner>/<repo>/contributors\",\n        \"source\": \"ghtorrent\",\n        \"metric_type\": \"metric\",\n        \"url\": \"activity-metrics/contributors.md\",\n        \"is_defined\": \"true\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/metrics_status/routes.py",
    "groupTitle": "Metrics_Status"
  },
  {
    "type": "get",
    "url": "metrics/status",
    "title": "Metrics Status",
    "name": "metrics_status",
    "group": "Metrics_Status",
    "description": "<p>Information about the Augur implementation status of CHAOSS metrics.</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n    \n        \"ID\": \"ghtorrent-fakes\",\n        \"tag\": \"fakes\",\n        \"name\": \"Fakes\",\n        \"group\": \"experimental\",\n        \"backend_status\": \"implemented\",\n        \"frontend_status\": \"implemented\",\n        \"endpoint\": \"/api/unstable/<owner>/<repo>/timeseries/fakes\",\n        \"source\": \"ghtorrent\",\n        \"metric_type\": \"timeseries\",\n        \"url\": \"/\",\n        \"is_defined\": \"false\"\n    },\n    {\n        \"ID\": \"ghtorrentplus-closed-issue-resolution-duration\",\n        \"tag\": \"closed-issue-resolution-duration\",\n        \"name\": \"Closed Issue Resolution Duration\",\n        \"group\": \"experimental\",\n        \"backend_status\": \"implemented\",\n        \"frontend_status\": \"unimplemented\",\n        \"endpoint\": \"/api/unstable/<owner>/<repo>/issues/time_to_close\",\n        \"source\": \"ghtorrentplus\",\n        \"metric_type\": \"metric\",\n        \"url\": \"activity-metrics/closed-issue-resolution-duration.md\",\n        \"is_defined\": \"true\"\n    },\n    {\n        \"ID\": \"githubapi-lines-of-code-changed\",\n        \"tag\": \"lines-of-code-changed\",\n        \"name\": \"Lines Of Code Changed\",\n        \"group\": \"experimental\",\n        \"backend_status\": \"implemented\",\n        \"frontend_status\": \"implemented\",\n        \"endpoint\": \"/api/unstable/<owner>/<repo>/timeseries/lines_changed\",\n        \"source\": \"githubapi\",\n        \"metric_type\": \"timeseries\",\n        \"url\": \"activity-metrics/lines-of-code-changed.md\",\n        \"is_defined\": \"true\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/metrics_status/routes.py",
    "groupTitle": "Metrics_Status"
  },
  {
    "type": "get",
    "url": "metrics/status/metadata",
    "title": "Metrics Status Metadata",
    "name": "metrics_status_metadata",
    "group": "Metrics_Status",
    "description": "<p>Metadata about the Augur implemntation status of CHAOSS metrics.</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"groups\": [\n            {\n                \"diversity-inclusion\": \"Diversity and Inclusion\",\n                \"growth-maturity-decline\": \"Growth, Maturity, and Decline\",\n                \"risk\": \"Risk\",\n                \"value\": \"Value\",\n                \"activity\": \"Activity\",\n                \"experimental\": \"Experimental\"\n            }\n        ],\n        \"sources\": [\n            \"ghtorrent\",\n            \"ghtorrentplus\",\n            \"githubapi\",\n            \"downloads\",\n            \"facade\",\n            \"publicwww\",\n            \"librariesio\",\n            \"git\"\n        ],\n        \"metric_types\": [\n            \"timeseries\",\n            \"metric\",\n            \"git\"\n        ],\n        \"tags\": {\n            \"listening\": \"diversity-inclusion\",\n            \"speaking\": \"diversity-inclusion\",\n            ...\n        }\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/metrics_status/routes.py",
    "groupTitle": "Metrics_Status"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/cii-best-practices-badge",
    "title": "CII Best Practices Badge (Repo)",
    "name": "cii_best_practices_badge_repo",
    "group": "Risk",
    "description": "<p>The CII Best Practices Badge level. <a href=\"https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"badge_level\": \"gold\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Risk"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/cii-best-practices-badge",
    "title": "CII Best Practices Badge (Repo Group)",
    "name": "cii_best_practices_badge_repo_group",
    "group": "Risk",
    "description": "<p>The CII Best Practices Badge level. <a href=\"https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21277,\n        \"badge_level\": \"passing\"\n    },\n    {\n        \"repo_id\": 21252,\n        \"badge_level\": \"in_progress\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Risk"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/languages",
    "title": "Languages (Repo)",
    "name": "languages_repo",
    "group": "Risk",
    "description": "<p>The primary language of the repository. <a href=\"https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"primary_language\":\"PHP\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Risk"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/languages",
    "title": "Languages (Repo Group)",
    "name": "languages_repo_group",
    "group": "Risk",
    "description": "<p>The primary language of the repository. <a href=\"https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21277,\n        \"primary_language\": \"Go\"\n    },\n    {\n        \"repo_id\": 21252,\n        \"primary_language\": \"PHP\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Risk"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/license-declared",
    "title": "License Declared (Repo)",
    "name": "license_declared_repo",
    "group": "Risk",
    "description": "<p>The declared software package license (fetched from CII Best Practices badging data). <a href=\"https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID.</p>"
          },
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_id",
            "description": "<p>Repository ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"license\": \"Apache-2.0\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Risk"
  },
  {
    "type": "get",
    "url": "/repo-groups/:repo_group_id/license-declared",
    "title": "License Declared (Repo Group)",
    "name": "license_declared_repo_group",
    "group": "Risk",
    "description": "<p>The declared software package license (fetched from CII Best Practices badging data). <a href=\"https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md\">CHAOSS Metric Definition</a></p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "string",
            "optional": false,
            "field": "repo_group_id",
            "description": "<p>Repository Group ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21277,\n        \"license\": \"Apache-2.0\"\n    },\n    {\n        \"repo_id\": 21252,\n        \"license\": \"Apache-2.0\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Risk"
  },
  {
    "type": "get",
    "url": "/user/:userid",
    "title": "User",
    "name": "User",
    "group": "Utility",
    "description": "<p>Utility endpoint to show information about users on GitHub.</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"id\": 18,\n        \"login\": \"developertown\",\n        \"company\": null,\n        \"created_at\": \"2010-12-09T13:14:35.000Z\",\n        \"type\": \"ORG\",\n        \"fake\": 0,\n        \"deleted\": 0,\n        \"long\": -86.158068,\n        \"lat\": 39.768403,\n        \"country_code\": \"us\",\n        \"state\": \"Marion County\",\n        \"city\": \"Indianapolis\",\n        \"location\": \"Indianapolis, IN\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/ghtorrent/routes.py",
    "groupTitle": "Utility"
  },
  {
    "type": "get",
    "url": "/repos/:owner/:repo",
    "title": "Get Repo",
    "name": "get_repo",
    "group": "Utility",
    "description": "<p>Get the <code>repo_group_id</code> &amp; <code>repo_id</code> of a particular repo.</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21339,\n        \"repo_group_id\": 23\n    },\n    {\n        \"repo_id\": 21000,\n        \"repo_group_id\": 20\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Utility"
  },
  {
    "type": "get",
    "url": "/repo-groups",
    "title": "Repo Groups",
    "name": "repo_groups",
    "group": "Utility",
    "description": "<p>Get all the downloaded repo groups.</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_group_id\": 20,\n        \"rg_name\": \"Rails\",\n        \"rg_description\": \"Rails Ecosystem.\",\n        \"rg_website\": \"\",\n        \"rg_recache\": 0,\n        \"rg_last_modified\": \"2019-06-03T15:55:20.000Z\",\n        \"rg_type\": \"GitHub Organization\",\n        \"tool_source\": \"load\",\n        \"tool_version\": \"one\",\n        \"data_source\": \"git\",\n        \"data_collection_date\": \"2019-06-05T13:36:25.000Z\"\n    },\n    {\n        \"repo_group_id\": 23,\n        \"rg_name\": \"Netflix\",\n        \"rg_description\": \"Netflix Ecosystem.\",\n        \"rg_website\": \"\",\n        \"rg_recache\": 0,\n        \"rg_last_modified\": \"2019-06-03T15:55:20.000Z\",\n        \"rg_type\": \"GitHub Organization\",\n        \"tool_source\": \"load\",\n        \"tool_version\": \"one\",\n        \"data_source\": \"git\",\n        \"data_collection_date\": \"2019-06-05T13:36:36.000Z\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Utility"
  },
  {
    "type": "get",
    "url": "/repos",
    "title": "Repos",
    "name": "repos",
    "group": "Utility",
    "description": "<p>Get all the downloaded repos.</p>",
    "success": {
      "examples": [
        {
          "title": "Success-Response:",
          "content": "[\n    {\n        \"repo_id\": 21996,\n        \"repo_name\": \"incubator-argus\",\n        \"description\": null,\n        \"url\": \"github.com\\/apache\\/incubator-argus.git\",\n        \"repo_status\": \"Update\",\n        \"commits_all_time\": null,\n        \"issues_all_time\": null,\n        \"rg_name\": \"Apache\",\n        \"base64_url\": \"Z2l0aHViLmNvbS9hcGFjaGUvaW5jdWJhdG9yLWFyZ3VzLmdpdA==\"\n    },\n    {\n        \"repo_id\": 21729,\n        \"repo_name\": \"tomee-site\",\n        \"description\": null,\n        \"url\": \"github.com\\/apache\\/tomee-site.git\",\n        \"repo_status\": \"Complete\",\n        \"commits_all_time\": 224216,\n        \"issues_all_time\": 2,\n        \"rg_name\": \"Apache\",\n        \"base64_url\": \"Z2l0aHViLmNvbS9hcGFjaGUvdG9tZWUtc2l0ZS5naXQ=\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "../augur/datasources/augur_db/routes.py",
    "groupTitle": "Utility"
  }
] });
