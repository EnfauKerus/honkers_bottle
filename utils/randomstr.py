import random
import string

def random_str(digits=32) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=digits))
