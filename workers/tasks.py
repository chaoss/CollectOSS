from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')
 

@app.task
def repo_info():
    pass


@app.task
def pull_requests():
    pass


@app.task
def pull_request_comments():
    pass


@app.task
def pull_request_events():
    pass


@app.task
def pull_request_reviews():
    pass


@app.task
def pull_request_labels():
    pass


@app.task
def pull_request_assignees():
    pass


@app.task
def pull_request_reviewers():
    pass


@app.task
def issues():
    pass


@app.task
def issue_comments():
    pass


@app.task
def issue_events():
    pass


@app.task
def issue_labels():
    pass


@app.task
def issue_assignees():
    pass

