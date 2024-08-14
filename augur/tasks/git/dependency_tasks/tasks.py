import logging
import traceback
from augur.tasks.git.dependency_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask, AugurSecondaryRepoCollectionTask
from augur.tasks.util.metadata_exception import MetadataException 


@celery.task(base=AugurFacadeRepoCollectionTask)
def process_dependency_metrics(repo_git):

    logger = logging.getLogger(process_dependency_metrics.__name__)

    generate_deps_data(logger, repo_git)


@celery.task(base=AugurSecondaryRepoCollectionTask, bind=True)
def process_ossf_dependency_metrics(self, repo_git):

    engine = self.app.engine
    
    logger = logging.getLogger(process_ossf_dependency_metrics.__name__)

    try: 
        generate_scorecard(logger, repo_git)
    except Exception as e: 
        logger.warning(f'Exception generating scorecard: {e}')
        raise MetadataException 
    
    """
        This try/except block is an attempt to get more information about this occasional error: 
        
        ```bash
        Traceback (most recent call last):
        File "/home/ubuntu/github/virtualenvs/hosted/lib/python3.11/site-packages/billiard/pool.py", line 366, in workloop
            put((READY, (job, i, result, inqW_fd)))
        File "/home/ubuntu/github/virtualenvs/hosted/lib/python3.11/site-packages/billiard/queues.py", line 366, in put
            self.send_payload(ForkingPickler.dumps(obj))
                            ^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/home/ubuntu/github/virtualenvs/hosted/lib/python3.11/site-packages/billiard/reduction.py", line 56, in dumps
            cls(buf, protocol).dump(obj)
        billiard.pool.MaybeEncodingError: Error sending result: ''(1, <ExceptionInfo: MetadataException("\'checks\' | Additional metadata: required_output: {}")>, None)''. Reason: ''PicklingError("Can\'t pickle <class \'augur.tasks.util.metadata_exception.MetadataException\'>: it\'s not the same object as augur.tasks.util.metadata_exception.MetadataException")''.
        ```
    """