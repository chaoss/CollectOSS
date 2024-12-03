from augur.tasks.init.redis_connection import redis_connection as conn
from augur.application.logs import AugurLogger
import json, random, time

from .KeyOrchestrationAPI import spec

class KeyOrchestrator:
    def __init__(self) -> None:
        self.stdin = conn.pubsub(ignore_subscribe_messages = True)
        self.logger = AugurLogger("KeyOrchestrator").get_logger()
        
        # Load channel names and IDs from the spec
        for channel in spec["channels"]:
            # IE: self.ANNOUNCE = "augur-oauth-announce"
            setattr(self, channel["name"], channel["id"])
            self.stdin.subscribe(channel["id"])

        self.fresh_keys: dict[str, set[str]] = {}
        self.expired_keys: dict[str, dict[str, int]] = {}

    def publish_key(self, key, platform):
        if platform not in self.fresh_keys:
            self.fresh_keys[platform] = {key,}
            self.expired_keys[platform] = {}
        else:
            self.fresh_keys[platform].add(key)

    def unpublish_key(self, key, platform):
        if platform not in self.fresh_keys:
            return
        
        if key in self.fresh_keys[platform]:
            self.fresh_keys[platform].remove(key)
        elif key in self.expired_keys[platform]:
            self.expired_keys[platform].pop(key)

    def run(self):
        while msg := self.stdin.listen():
            try:
                if msg.get("type") != "message":
                    # Filter out unwanted events
                    continue
                elif not (channel := msg.get("channel")):
                    # The pub/sub API makes no guarantee that a channel will be specified
                    continue
            
                channel: str = channel.decode()

                request = json.loads(msg.get("data"))
            except Exception as e:
                self.logger.error("Error during request decoding")
                self.logger.exception(e)
                continue
            
            """ For performance reasons:
            
                Instead of dynamically checking that the
                given channel matches one that we're
                listening for, just check against each
                channel that we have actions prepared for.
            """
            if channel == self.ANNOUNCE:
                try:
                    if request["type"] == "PUBLISH":
                        ...
                    elif request["type"] == "UNPUBLISH":
                        ...
                    elif request["type"] == "SHUTDOWN":
                        # Close
                        return
                except Exception as e:
                    # This is a bare exception, because we don't really care why failure happened
                    self.logger.error("Error during ANNOUNCE")
                    self.logger.exception(e)
            elif channel == self.REQUEST:
                try:
                    if request["type"] == "NEW":
                        ...
                    elif request["type"] == "EXPIRE":
                        ...
                except Exception as e:
                    # This is a bare exception, because we don't really care why failure happened
                    self.logger.error("Error during REQUEST")
                    self.logger.exception(e)
        
        self.logger.info("Got no message on listen(), shutting down")
                    
if __name__ == "__main__":
    manager = KeyOrchestrator()
    
    manager.run()
