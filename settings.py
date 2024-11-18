import base64
import os
from os.path import join, dirname
from dotenv import load_dotenv
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SNOWFLAKE_HOST = os.environ.get("SNOWFLAKE_HOST")
ACCOUNT = os.environ.get("ACCOUNT")
USER = os.environ.get("USER")
ROLE = os.environ.get("ROLE")
PASSWORD = os.environ.get("PASSWORD")
password_encrypted = os.environ.get("PASSWORD_ENCRYPTED")
if password_encrypted is not None:
    password_encrypted_decoded = base64.b64decode(password_encrypted.encode('utf-8'))
    key = RSA.importKey(open("keys/private-key.pem", "r").read())
    decryptor = PKCS1_v1_5.new(key)
    sentinel = get_random_bytes(16)
    decrypted_password = decryptor.decrypt(password_encrypted_decoded, sentinel)
    PASSWORD = decrypted_password.decode('utf-8').replace("\n", "")
