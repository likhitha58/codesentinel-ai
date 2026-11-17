
import hashlib
import os
import pickle


# TEST CASE 1: Hardcoded credential
password = "demo-not-a-real-password"

# TEST CASE 2: SQL injection
def get_user(cursor, user_id):
    cursor.execute(
        "SELECT * FROM users WHERE id = " + user_id
    )

# TEST CASE 3: Unsafe evaluation
def process_input(user_input):
    return eval(user_input)

# TEST CASE 4: Command injection
def run_command(user_input):
    os.system(user_input)

# TEST CASE 5: Weak cryptography
def generate_hash(data):
    return hashlib.md5(data)

# TEST CASE 6: Unsafe deserialization
def load_data(payload):
    return pickle.loads(payload)

# TEST CASE 7: Debug mode enabled
debug = True
