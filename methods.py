import os
from flask import request,session 
from werkzeug.utils import secure_filename

def File_handler(file,folder):
    name = file.filename
    if "." in name:        
        string = name[-4:]
        if string[0] == '.':
            ext = string.strip(string[0])
        else:
            ext = string

        if ext.lower() in [ 'png', 'jpg', 'jpeg','gif','jfif''zip','rar','rar4','mp3','wma','m4a' ]:
            file_allowed = True
            file_name = secure_filename(name)
            #file.save(os.path.join(app.config['ART_FOLDER'], file_name))
            path =  str(folder) + '/'+str(file_name)
        else:
           file_allowed = False
           path = None
           file_name = None
    else:
           file_allowed = False
           path = None
           file_name = None

    result = [file_allowed, path, file_name ]
    return result

