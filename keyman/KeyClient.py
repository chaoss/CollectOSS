from augur.tasks.init.redis_connection import redis_connection as conn
from os import getpid

from .KeyOrchestrationAPI import spec

class KeyClient:
    """ NOT THREAD SAFE!
    
        Only one KeyClient can exist per *process*.
        
        param platform: The default platform to use for key requests
    """
    def __init__(self, platform: str):
        self.id = getpid()
        
        # Load channel names and IDs from the spec
        for channel in spec["channels"]:
            # IE: self.ANNOUNCE = "augur-oauth-announce"
            setattr(self, channel["name"], channel["id"])
            
        if not platform:
            raise ValueError("Platform must not be empty")
        
        self.stdout = conn
        self.stdin = conn.pubsub(f"{self.REQUEST}-{self.id}")
        self.platform = platform
    
    """ Request a new key from the Orchestrator
    
    Will block until a key is available. Will block
    *indefinitely* if no keys are available for the
    requested platform.
    
    Optionally supply a platform string, if the default
    one provided during initialization does not match
    the desired platform for this request.
    """
    def request(self, platform = None) -> str:
        pass
    
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
        pass

class KeyPublisher:
    
    def publish(key: str, platform: str):
        pass
    
    def unpublish(key: str, platform: str):
        pass