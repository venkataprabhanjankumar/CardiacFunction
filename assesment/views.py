from django.http.response import HttpResponse
import json
from rest_framework.decorators import api_view
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
from tensorflow_addons.metrics.r_square import RSquare
import tensorflow as tf
import pickle


@api_view(['POST'])
def get_result(request):
    echo_video = request.FILES.get('echovideo')
    fs = FileSystemStorage(location='temp')
    filename = fs.save(echo_video.name, echo_video)
    captured = cv2.VideoCapture('./temp/' + filename, cv2.CAP_FFMPEG)
    frames = int(captured.get(cv2.CAP_PROP_FRAME_COUNT))
    predicted_result = []
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
        for each in data:
            cmodel = tf.saved_model.load('./model/dnn')
            model_input = tf.constant(each, dtype=tf.float32)[tf.newaxis, ...]
            predicted = cmodel(model_input)
            predicted_result.append(predicted.numpy()[0][0])
        print(predicted_result)
        print(sum(predicted_result) / len(predicted_result))
        final_result = sum(predicted_result) / len(predicted_result)
        captured.release()
        fs.delete(filename)
        return HttpResponse(json.dumps({'status': 'ok', 'ejection_fraction': final_result}))
    else:
        return HttpResponse(json.dumps({'status': 'notok'}))


@api_view(['POST'])
def get_cls(request):
    try:
        age = float(request.POST.get('age'))
        anaemia = int(request.data.get('anaemia'))
        diabetes = int(request.data.get('diabetes'))
        ejection_fraction = float(request.data.get('ejection_fraction'))
        hbp = int(request.data.get('hbp'))
        sex = int(request.data.get('sex'))
        smoking = int(request.data.get('smoking'))
        time = int(request.data.get('time'))
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'status': 'notok','msg': 'Invalid Data'}))
    with open('./model/clsmodel', 'rb') as f:
        cls = pickle.load(f)
        cls_input = np.array([[age, anaemia, diabetes, ejection_fraction, hbp, sex, smoking, time]])
        prediction = cls.predict(cls_input)
        print(prediction)
        result = prediction[0]
        print(result)
        return HttpResponse(json.dumps({'status': 'ok', 'cls': int(result)}))
