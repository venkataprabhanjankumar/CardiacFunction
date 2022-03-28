from django.http.response import HttpResponse
import json
from rest_framework.decorators import api_view
from django.core.files.storage import FileSystemStorage
import pickle
import cv2
import numpy as np


@api_view(['POST'])
def get_result(request):
    echo_video = request.FILES.get('echovideo')
    fs = FileSystemStorage(location='temp')
    filename = fs.save(echo_video.name, echo_video)
    captured = cv2.VideoCapture('./temp/'+filename, cv2.CAP_FFMPEG)
    frames = int(captured.get(cv2.CAP_PROP_FRAME_COUNT))
    if frames > 50:
        fps = 50
        fcount = 0
        fdata = []
        seconds_data = []
        while captured.isOpened():
            result, frame = captured.read()
            if frame is None:
                break
            else:
                fcount = fcount + 1
                if fcount < fps:
                    fdata.append(frame)
                elif fcount == fps:
                    fdata.append(frame)
                    seconds_data.append(np.array(fdata))
                    fdata = []
                    fcount = 0
        data = np.array(seconds_data)
        '''tf.saved_model.LoadOptions(experimental_io_device='/job:localhost')
        with open('./model/model1', 'rb') as f:
            print(f.name)
            model = pickle.load(f)
            model.summary()
            predicted = model.predict(data)
            print(predicted)'''
        print(data.shape)
        captured.release()
        fs.delete(filename)
        return HttpResponse(json.dumps({'status': 'ok'}))
    else:
        return HttpResponse(json.dumps({'status': 'notok'}))
