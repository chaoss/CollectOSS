import uuid
import random


instance_id = uuid.uuid4().hex

# python typically allocates 32 bits for a single 
# integer, so we made this number fit in 32 bits
random_number = random.randint(0, 2147483640)

database_one_id = random_number
database_two_id = random_number + 1
database_three_id = random_number + 2
