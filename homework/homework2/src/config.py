import os
from dotenv import load_dotenv

def load_env():
    '''
    Docstring here
    '''
    load_dotenv()

def get_key(key_name: str) -> str:
    '''
    Docstring here
    '''
    return os.getenv(key_name)
