from augur.tasks.init.redis_connection import redis_connection as conn
from redis.client import PubSub
from logging import Logger
from os import getpid
import time, json

from .KeyOrchestrationAPI import spec

class KeyClient:
    """ NOT THREAD SAFE!
    
        Only one KeyClient can exist per *process*.
        
        param platform: The default platform to use for key requests
    """
    def __init__(self, platform: str, logger: Logger):
        self.id = getpid()
        
        # Load channel names and IDs from the spec
        for channel in spec["channels"]:
            # IE: self.ANNOUNCE = "augur-oauth-announce"
            setattr(self, channel["name"], channel["id"])
            
        if not platform:
            raise ValueError("Platform must not be empty")
        
        self.stdout = conn
        self.stdin: PubSub = conn.pubsub(f"{self.REQUEST}-{self.id}", ignore_subscribe_messages = True)
        self.platform = platform
        self.logger = logger
    
    """ Request a new key from the Orchestrator
    
    Will block until a key is available. Will block
    *indefinitely* if no keys are available for the
    requested platform.
    
    Optionally supply a platform string, if the default
    one provided during initialization does not match
    the desired platform for this request.
    """
    def request(self, platform = None) -> str:
        message = {
            "type": "NEW",
            "key_platform": platform or self.platform,
            "requester_id": self.id
        }
        
        while True:
            self.stdout.publish(self.REQUEST, json.dumps(message))
            try:
                reply = self.stdin.listen()

                msg = json.loads(reply["data"])

                if "key" in msg:
                    return msg["key"]
                
                if "wait" in msg:
                    time.sleep(msg["wait"])
                else:
                    raise Exception(f"Invalid response type: {msg}")
                
            except Exception as e:
                self.logger.exception("Error during key request")
                time.sleep(20)
    
    """ Expire a key, and get a new key in return
    
    Will block until a key is available. Will block
    *indefinitely* if no keys are available for the
    requested platform.
    
    Optionally supply a platform string, if the default
    one provided during initialization does not match
    the desired platform for this request. The platform
    given *must* match the old key, and also the new key.
    """
    def expire(self, key: str, refresh_timestamp: int, platform: str = None) -> str:
        message = {
            "type": "EXPIRE",
            "key_str": key,
            "key_platform": platform,
            "refresh_time": refresh_timestamp,
            "requester_id": self.id
        }

        self.stdout.publish(self.REQUEST, json.dumps(message))
        time.sleep(0.1)
        return self.request()

class KeyPublisher:
    def __init__(self) -> None:
        # Load channel names and IDs from the spec
        for channel in spec["channels"]:
            # IE: self.ANNOUNCE = "augur-oauth-announce"
            setattr(self, channel["name"], channel["id"])

    def publish(self, key: str, platform: str):
        message = {
            "type": "PUBLISH",
            "key_str": key,
            "key_platform": platform
        }

        conn.publish(self.ANNOUNCE, json.dumps(message))
    
    def unpublish(self, key: str, platform: str):
        message = {
            "type": "UNPUBLISH",
            "key_str": key,
            "key_platform": platform
        }

        conn.publish(self.ANNOUNCE, json.dumps(message))

