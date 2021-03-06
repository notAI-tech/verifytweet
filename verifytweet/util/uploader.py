# Verify Tweet verifies tweets of a public user
# from tweet screenshots: real or generated from
# tweet generators.
# Copyright (C) 2019 Preetham Kamidi

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import uuid
import shutil

import requests

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from verifytweet.util.logging import logger
from verifytweet.config.settings import app_config
from verifytweet.util.result import ResultStatus


def save_to_disk(file_obj):
    """Saves an uploaded file via POST request to disk
    """
    if not isinstance(file_obj, FileStorage):
        raise TypeError(
            'file obj must be type werkzeug.datastructures.FileStorage')
    if not file_obj:
        raise ValueError('file obj cannot be empty')
    filename = secure_filename(file_obj.filename)
    if file_obj and allowed_file(filename):
        saved_file_name = str(uuid.uuid1()) + '.' + \
            filename.rsplit('.', 1)[1].lower()
        saved_file_path = os.path.join(app_config.FILE_DIRECTORY,
                                        saved_file_name)
        logger.debug('Saving file to path: ' + saved_file_path)
        file_obj.save(saved_file_path)
        return saved_file_path
    return None

def save_from_url(image_url: str):
    """Saves image given via url to disk
    """
    if not isinstance(image_url, str):
        raise TypeError('image_url must be a string')
    if not image_url:
        raise ValueError('image_url has to be a valid string')
    r = requests.get(image_url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        raise FileNotFoundError()
    filename = image_url.split("/")[-1]
    if filename and allowed_file(filename):
        saved_file_path = os.path.join(app_config.FILE_DIRECTORY, filename)
        logger.info('Saving file to path: ' + saved_file_path)
        r.raw.decode_content = True
        with open(saved_file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
            logger.info('Image successfully downloaded')
            return saved_file_path

def allowed_file(filename):
    """Checks if uploaded file has valid extenstion
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app_config.ALLOWED_EXTENSIONS