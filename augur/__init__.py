import uuid

instance_id = str(uuid.uuid4().hex)
queue_name = f"{instance_id}_queue"