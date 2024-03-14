from os import environ as env
import json, subprocess
from pathlib import Path

rabbit_user = env.get("RABBIT_MQ_DEFAULT_USER")
rabbit_pass = env.get("RABBIT_MQ_DEFAULT_PASSWORD")
rabbit_vhost = env.get("RABBIT_MQ_DEFAULT_VHOST")

if not rabbit_user:
    raise ValueError("No default user set")

if not rabbit_pass:
    raise ValueError("No default password set")
    
if not rabbit_vhost:
    raise ValueError("No default vhost set")

config_file = Path("/etc/rabbitmq/definitions.json")

with config_file.open() as file:
    config = json.load(file)

hash_processor = subprocess.run(f"rabbitmqctl hash_password {rabbit_pass}".split(),
                                text=True,
                                stdout=subprocess.PIPE)

if hash_processor.returncode != 0:
    raise Exception("Could not calculate password hash")

pass_hash = hash_processor.stdout.splitlines()[-1]

config["users"][0]["name"] = rabbit_user
config["users"][0]["password_hash"] = pass_hash

config["vhosts"][0]["name"] = rabbit_vhost

config["permissions"][0]["user"] = rabbit_user
config["permissions"][0]["vhost"] = rabbit_vhost

with config_file.open("w") as file:
    json.dump(config, file)