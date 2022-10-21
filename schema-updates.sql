-- DO NOT IMPLEMENT YET .. trying to figure out why this happened. Running again.
--
-- 10/1/2022: SPG - Got an error on this login constraint, which actually makes no sense. So, trying this change. 
/*
Traceback (most recent call last):
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/app/trace.py", line 451, in trace_task
    R = retval = fun(*args, **kwargs)
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/app/trace.py", line 734, in __protected_call__
    return self.run(*args, **kwargs)
  File "/home/sean/github/rh-augur-new-dev/augur/tasks/start_tasks.py", line 159, in start_task
    augur_collection.start_data_collection()
  File "/home/sean/github/rh-augur-new-dev/augur/tasks/start_tasks.py", line 139, in start_data_collection
    raise e
  File "/home/sean/github/rh-augur-new-dev/augur/tasks/start_tasks.py", line 132, in start_data_collection
    phaseResult.join()
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 747, in join
    value = result.get(
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 224, in get
    return self.backend.wait_for_pending(
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/backends/asynchronous.py", line 221, in wait_for_pending
    for _ in self._wait_for_pending(result, **kwargs):
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/backends/asynchronous.py", line 287, in _wait_for_pending
    for _ in self.drain_events_until(
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/backends/asynchronous.py", line 58, in drain_events_until
    on_interval()
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/vine/promises.py", line 160, in __call__
    return self.throw()
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/vine/promises.py", line 157, in __call__
    retval = fun(*final_args, **final_kwargs)
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 237, in _maybe_reraise_parent_error
    node.maybe_throw()
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 609, in maybe_throw
    result.maybe_throw(callback=callback, propagate=propagate)
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 609, in maybe_throw
    result.maybe_throw(callback=callback, propagate=propagate)
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 336, in maybe_throw
    self.throw(value, self._to_remote_traceback(tb))
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/celery/result.py", line 329, in throw
    self.on_ready.throw(*args, **kwargs)
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/vine/promises.py", line 234, in throw
    reraise(type(exc), exc, tb)
  File "/home/sean/github/virtualenv/k12/lib/python3.8/site-packages/vine/utils.py", line 30, in reraise
    raise value
Exception: <class 'sqlalchemy.exc.IntegrityError'>(['(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "GL-cntrb-LOGIN-UNIQUE"\nDETAIL:  Key (cntrb_login)=(name) already exists.\n'])
*/

ALTER TABLE "augur_data"."commits" DROP CONSTRAINT "fk_commits_contributors_3";

ALTER TABLE "augur_data"."commits" DROP CONSTRAINT "fk_commits_contributors_4";

ALTER TABLE "augur_data"."contributors" 
  DROP CONSTRAINT "GL-cntrb-LOGIN-UNIQUE",
  ADD CONSTRAINT "GL-cntrb-LOGIN-UNIQUE" UNIQUE ("cntrb_login") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."commits" ADD CONSTRAINT "fk_commits_contributors_3" FOREIGN KEY ("cmt_author_platform_username") REFERENCES "augur_data"."contributors" ("cntrb_login") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."commits" ADD CONSTRAINT "fk_commits_contributors_4" FOREIGN KEY ("cmt_author_platform_username") REFERENCES "augur_data"."contributors" ("cntrb_login") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;
