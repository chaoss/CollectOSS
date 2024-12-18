
""" This is a hybrid-fixed specification

The names of the channels *MUST NOT* change,
but the channel IDs are free to
"""
spec = {
    "channels": [
        {
            "name": "ANNOUNCE",
            "id": "augur-oauth-announce",
            "message_types": {
                "PUBLISH": {
                    "key_str": str,
                    "key_platform": str
                },
                "UNPUBLISH": {
                    "key_str": str,
                    "key_platform": str
                },
                "SHUTDOWN": {}
            }
        }, {
            "name": "REQUEST",
            "id": "worker-oath-request",
            "message_types": {
                "NEW": {
                    "fields": {
                        "key_platform": { "required": str },
                        "requester_id": { "required": str }
                    },
                    "response": {
                        "key": { "optional": str },
                        "wait": { "optional": int }
                    }
                },
                "EXPIRE": {
                    "fields": {
                        "key_str": str,
                        "key_platform": str,
                        "refresh_time": int,
                        "requester_id": str
                    },
                    "response": {
                        "key": { "optional": str },
                        "wait": { "optional": int }
                    }
                }
            }
        }
    ]
}
