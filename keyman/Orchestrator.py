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

    def expire_key(self, key, platform, timeout):
        if not platform in self.fresh_keys or not key in self.fresh_keys[platform]:
            return
        
        self.fresh_keys[platform].remove(key)

        self.expired_keys[platform][key] = timeout

    def refresh_keys(self):
        curr_time = time.time()

        for platform in self.expired_keys:
            refreshed_keys = []

            for key, timeout in self.expired_keys[platform].items():
                if timeout <= curr_time:
                    refreshed_keys.append(key)

            for key in refreshed_keys:
                self.fresh_keys[platform].add(key)
                self.expired_keys[platform].pop(key)

    def new_key(self, platform):
        if not len(self.fresh_keys[platform]):
            if not len(self.expired_keys[platform]):
                self.logger.warning(f"Key was requested for {platform}, but none are published")
                return
            
            min = 0
            for key, timeout in self.expired_keys[platform].items():
                if not min or timeout < min:
                    min = timeout

            delta = int(min - time.time())

            raise WaitKeyTimeout(delta + 5 if delta > 0 else 5)
        
        return random.choice(self.fresh_keys[platform])

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
                        self.publish_key(request["key_str"], request["key_platform"])
                    elif request["type"] == "UNPUBLISH":
                        self.unpublish_key(request["key_str"], request["key_platform"])
                    elif request["type"] == "SHUTDOWN":
                        # Close
                        return
                except Exception as e:
                    # This is a bare exception, because we don't really care why failure happened
                    self.logger.exception("Error during ANNOUNCE")
                    continue
            elif channel == self.REQUEST:
                self.refresh_keys()
                stdout = f"{self.REQUEST}-{request['requester_id']}"

                try:
                    if request["type"] == "NEW":
                        new_key = self.new_key(request["key_platform"])
                    elif request["type"] == "EXPIRE":
                        self.expire_key(request["key_str"], request["key_platform"], request["refresh_time"])
                        new_key = self.new_key(request["key_platform"])
                except WaitKeyTimeout as w:
                    timeout = w.tiemout_seconds
                    conn.publish(stdout, json.dumps({
                        "wait": timeout
                    }))
                    continue
                except Exception as e:
                    # This is a bare exception, because we don't really care why failure happened
                    self.logger.exception("Error during REQUEST")
                    continue

                conn.publish(stdout, json.dumps({
                    "key": new_key
                }))
        
        self.logger.info("Got no message on listen(), shutting down")

class WaitKeyTimeout:
    def __init__(self, timeout_seconds) -> None:
        self.tiemout_seconds = timeout_seconds
                    
if __name__ == "__main__":
    manager = KeyOrchestrator()
    
    manager.run()
