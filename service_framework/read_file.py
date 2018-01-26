import random as rnd
import string
# import uuid


def __get_content__(filename):
    content = None
    try:
        file = open(filename, 'r')
        content = file.read().replace('\n', '')
        file.close()
        return True, content
    except Exception as e:
        return False, content

def __create_file__(filename, content):
    file = open(filename, 'w+')
    file.write(content)
    file.close()

def get_id(filename):
    isSuccess, content = __get_content__(filename)
    if(not isSuccess):
        content = str(uuid.uuid4())
        __create_file__(filename, content)
    return content 

def get_content(filename, content_length=255):
    isSuccess, content = __get_content__(filename)
    if(not isSuccess):
        letters = string.ascii_letters + string.digits
        content = ''.join(rnd.choice(letters) for _ in range(content_length))
        __create_file__(filename, content)
    return content


