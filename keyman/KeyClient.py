from augur.tasks.init.redis_connection import redis_connection as conn
from redis.client import PubSub
from logging import Logger
from os import getpid
import time, json

from keyman.KeyOrchestrationAPI import spec, WaitKeyTimeout

class KeyClient:
    """ NOT THREAD SAFE!
    
        Only one KeyClient can exist at a time per *process*, as
        the process ID is used for async communication between
        the client and the orchestrator.
        
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
        self.stdin: PubSub = conn.pubsub(ignore_subscribe_messages = True)
        self.stdin.subscribe(f"{self.REQUEST}-{self.id}")
        self.platform = platform
        self.logger = logger
    
    def _send(self, req_type, **kwargs):
        kwargs["type"] = req_type
        kwargs["requester_id"] = self.id
        
        self.stdout.publish(self.REQUEST, json.dumps(kwargs))
    
    def _recv(self, timeout = None):
        if timeout is not None:
            return self.stdin.get_message(timeout = timeout)
        
        stream = self.stdin.listen()
        
        reply = next(stream)

        msg = json.loads(reply["data"])
        
        if "wait" in msg:
            raise WaitKeyTimeout(msg["wait"])
        else:
            return msg
    
    """ Request a new key from the Orchestrator
    
        Will block until a key is available. Will block
        *indefinitely* if no keys are available for the
        requested platform.
        
        Optionally supply a platform string, if the default
        one provided during initialization does not match
        the desired platform for this request.
    """
    def request(self, platform = None) -> str:
        while True:
            self._send("NEW", key_platform = platform or self.platform)
            try:
                msg = self._recv()
                if "key" in msg:
                    return msg["key"]

                else:
                    raise Exception(f"Invalid response type: {msg}")
            except WaitKeyTimeout as e:
                self.logger.debug(f"NO FRESH KEYS: sleeping for {e.tiemout_seconds} seconds")
                time.sleep(e.tiemout_seconds)
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
            "key_platform": platform or self.platform,
            "refresh_time": refresh_timestamp,
            "requester_id": self.id
        }

        self.stdout.publish(self.REQUEST, json.dumps(message))
        time.sleep(0.1)
        return self.request()

class KeyPublisher:
    """ NOT THREAD SAFE!
    
        Only one KeyPublisher can exist at a time per *process*,
        as the process ID is used for async communication between
        the publisher and the orchestrator.
    """
    def __init__(self) -> None:
        # Load channel names and IDs from the spec
        for channel in spec["channels"]:
            # IE: self.ANNOUNCE = "augur-oauth-announce"
            setattr(self, channel["name"], channel["id"])
            
        self.id = getpid()
        self.stdin: PubSub = conn.pubsub(ignore_subscribe_messages = True)
        self.stdin.subscribe(f"{self.ANNOUNCE}-{self.id}")

    """ Publish a key to the orchestration server
    
        No reply is sent, and keys are added or overwritten
        silently.
    """
    def publish(self, key: str, platform: str):
        message = {
            "type": "PUBLISH",
            "key_str": key,
            "key_platform": platform
        }

        conn.publish(self.ANNOUNCE, json.dumps(message))
    
    """ Unpublish a key, and remove it from orchestration
    
        They key will remain in use by any workers that are currently
        using it, but it will not be assigned to any new requests.
        
        No reply is sent, and non-existent keys or platforms are
        ignored silently. 
    """
    def unpublish(self, key: str, platform: str):
        message = {
            "type": "UNPUBLISH",
            "key_str": key,
            "key_platform": platform
        }

        conn.publish(self.ANNOUNCE, json.dumps(message))
    
    """ Wait for ACK from the orchestrator
    
        If a lot of publish or unpublish messages are waiting to
        be processed, this will block until all of them have been
        read. If the timeout is reached, this returns False, or if
        the orchestration server acknkowledges within the time
        limit, this returns True.
        
        If republish is true, the initial ACK request will be resent
        10 times per second until the orchestrator responds. This
        should only be used to wait for the orchestrator to come
        online, as it could put a lot of unnecessary messages on the
        queue if the orchestrator is running, but very busy.
    """
    def wait(self, timeout_seconds = 30, republish = False):
        if timeout_seconds < 0:
            raise ValueError("timeout cannot be negative")
        
        message = {
            "type": "ACK",
            "requester_id": self.id
        }
        
        listen_delta = 0.1
        conn.publish(self.ANNOUNCE, json.dumps(message))
        
        # Just wait for and consume the next incoming message
        while timeout_seconds >= 0:
            # get_message supposedly takes a 'timeout' parameter, but that did not work
            reply = self.stdin.get_message(ignore_subscribe_messages = True)
            
            if reply:
                return True
            elif timeout_seconds < listen_delta:
                break
            elif republish:
                conn.publish(self.ANNOUNCE, json.dumps(message))
            
            time.sleep(listen_delta)
            timeout_seconds -= listen_delta
        
        return False

    """ Get a list of currently loaded orchestration platforms
    
        Will raise a ValueError if the orchestration server
        returns a malformed response.
    """
    def list_platforms(self):
        message = {
            "type": "LIST_PLATFORMS",
            "requester_id": self.id
        }
        
        conn.publish(self.ANNOUNCE, json.dumps(message))
        
        reply = next(self.stdin.listen())
        
        try:
            reply = json.loads(reply["data"])
        except Exception as e:
            raise ValueError("Exception during platform list decoding")
        
        if isinstance(reply, list):
            return reply
        
        raise ValueError(f"Unexpected reply during list operation: {reply}")
        
    """ Get a list of currently loaded keys for the given platform
    
        Will raise a ValueError if the orchestration server
        returns a malformed response, or if the platform does
        not exist.
    """
    def list_keys(self, platform):
        message = {
            "type": "LIST_KEYS",
            "requester_id": self.id,
            "key_platform": platform
        }
        
        conn.publish(self.ANNOUNCE, json.dumps(message))
        
        reply = next(self.stdin.listen())
        
        try:
            reply = json.loads(reply["data"])
        except Exception as e:
            raise ValueError("Exception during key list decoding")
        
        if isinstance(reply, list):
            return reply
        elif isinstance(reply, dict) and "status" in reply:
            raise ValueError(f"Orchestration error: {reply['status']}")
        else:
            raise ValueError(f"Unexpected reply during list operation: {reply}")
        
    def shutdown(self):
        conn.publish(self.ANNOUNCE, json.dumps({"type": "SHUTDOWN"}))
