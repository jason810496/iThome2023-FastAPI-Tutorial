import moviepy.editor as mp 
import speech_recognition as sr 
from fastapi import UploadFile
from uuid import uuid4
import os

from rq.job import Job
from datetime import datetime

from setting.config import get_settings

settings = get_settings()

def get_text_from_video(uuid:str) -> str:
    print(f"{uuid} : Start")
    video_path = f"{settings.upload_path}/{uuid}.mp4"
    video = mp.VideoFileClip(video_path) 
    audio_file = video.audio 
    tmp_file = f"{settings.tmp_path}/{uuid}.wav"

    audio_file.write_audiofile(tmp_file) 
    r = sr.Recognizer() 

    with sr.AudioFile(tmp_file) as source: 
        data = r.record(source) 
    text = r.recognize_google(data) 

    print(f"{uuid} : Done")

    return text

def get_text_from_video_task(file: UploadFile,hash_name:str) -> str:
    save_path = settings.upload_path
    ext_name = file.filename.split(".")[-1]
    out_file_path = f"{save_path}/{hash_name}.{ext_name}"

    with open(out_file_path, 'wb') as out_file:
        content = file.file.read()
        out_file.write(content)

    video_path = f"{save_path}/{hash_name}.{ext_name}"
    
    video = mp.VideoFileClip(video_path) 
    audio_file = video.audio 
    tmp_file = f"{settings.tmp_path}/{hash_name}.wav"

    audio_file.write_audiofile(tmp_file) 
    r = sr.Recognizer() 

    with sr.AudioFile(tmp_file) as source: 
        data = r.record(source) 
    text = r.recognize_google(data) 

    print(f"{hash_name} : Done")

    return text

def report_success(job:Job, connection, result, *args, **kwargs):
    # print execute result & time
    # print(x.result, x.enqueued_at, x.ended_at) 
    print("job:", job )
    print("result:", result )
    print("start time:", job.enqueued_at )
    print("end time:", job.ended_at )

    start:datetime = job.enqueued_at 
    end:datetime = job.ended_at

    execute_time = end - start
    print("execute time:", execute_time.total_seconds() )


def report_failed(job:Job, connection, exc_type, exc_value, traceback):
    print("job:", job )
    print("exc_type:", exc_type )
    print("exc_value:", exc_value )
    print("traceback:", traceback )



def clean_file(hash_name:str):
    save_path = settings.upload_path
    tmp_path = settings.tmp_path

    video_path = f"{save_path}/{hash_name}.mp4"
    tmp_file = f"{tmp_path}/{hash_name}.wav"

    try:
        print(f"try to remove {video_path}")
        os.remove(video_path)
        print("remove video file success")
    except:
        print("remove video file failed")

    try:
        print(f"try to remove {tmp_file}")
        os.remove(tmp_file)
        print("remove tmp file success")
    except:
        print("remove tmp file failed")

    

