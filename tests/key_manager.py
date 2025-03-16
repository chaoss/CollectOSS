from keyman.KeyClient import KeyClient, KeyPublisher
from augur.application.logs import AugurLogger

from multiprocessing import Process, current_process
from subprocess import Popen, PIPE

import random, time, atexit

keys = {
    "github": [
        "key1",
        "key2",
        "key3",
        "key4"
    ],
    "gitlab": [
        "key5",
        "key6",
        "key7",
        "key8"
    ]
}

def mp_consumer(platform):
    if platform not in keys:
        raise ValueError(f"Platform not valid for testing keys dict: {platform}")
    
    logger = AugurLogger(f"Keyman_test_consumer").get_logger()
    logger.setLevel(1)
    client = KeyClient(platform, logger)
    
    key = client.request()
    for _ in range(len(keys[platform])):
        if key not in keys[platform]:
            raise AssertionError(f"Received key {platform}:{key} not valid")
        
        sleep_timeout = random.randint(10, 30)
        
        """ This is a fairly unrealistic scenario, because theoretically
            every worker that would expire a key would expire it at the
            exact same timestamp (as reported by the platform API).
            
            Whereas for this testing, each worker is just reporting a
            random future timestamp. In effect, this means that two
            workers might assign different timeouts to the same key,
            making it appear as though the orchestrator is not assigning
            keys properly, when in fact it is working as expected.
        """
        logger.info(f"Expiring {platform}:{key} for {sleep_timeout} seconds")
        key = client.expire(key, int(time.time()) + sleep_timeout)

if __name__ == "__main__":
    orchestrator = Popen("python keyman/Orchestrator.py".split())
    
    publisher = KeyPublisher()
    
    if not publisher.wait(republish = True):
        raise AssertionError("Orchestrator not reachable on startup")
    
    atexit.register(publisher.shutdown)
    
    for platform, key_list in keys.items():
        for key in key_list:
            publisher.publish(key, platform)
        
    if not publisher.wait():
        raise AssertionError("Orchestrator did not ACK within the time limit")
    
    logger = AugurLogger("Keyman_test").get_logger()
    logger.info("Keys loaded")
    
    platforms = publisher.list_platforms()
    
    logger.info(f"Loaded platforms: {platforms}")
    
    for platform in platforms:
        key_list = publisher.list_keys(platform)
        logger.info(f"Keys for {platform}: {key_list}")
    
    logger.info("Running expiration tests")
    workers: list[Process] = []
    for platform, key_list in keys.items():
        num_workers = len(key_list) // 2
        
        for i in range(num_workers):
            workers.append(Process(target = mp_consumer, args = [platform]))

    try:    
        for worker in workers:
            worker.start()
            
        for worker in workers:
            worker.join()

        logger.info("Running invalidation tests")
        client = KeyClient(next(k for k in keys), logger)
    
        for platform in keys:
            inv_key = client.request(platform)
            logger.info(f"Invalidating key {platform}: {inv_key}")
            client.invalidate(inv_key, platform)

        logger.info("Keys after invalidation:")
        for platform in platforms:
            key_list = publisher.list_keys(platform)
            logger.info(f"Keys for {platform}: {key_list}")
    except KeyboardInterrupt:
        pass
    