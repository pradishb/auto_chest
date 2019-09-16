''' Module that does image releated tasks '''
import json
import os

from settings import OUTPUT_DIR


def download_image(connection, path):
    ''' Downloads image from server '''
    file_name = os.path.join(OUTPUT_DIR, 'images', path[1:])
    if os.path.exists(file_name):
        return
    res = connection.get(path, stream=True)
    try:
        if 'errorCode' in res.json():
            return
    except json.decoder.JSONDecodeError:
        pass
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'wb') as file:
        file.write(res.content)
    del res
