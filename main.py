import streamlit as st
from vosk import Model, KaldiRecognizer, SetLogLevel
from pydub import AudioSegment
import subprocess
import json
import os

# Настройка боковой панели
st.sidebar.title("About")
st.sidebar.info(
    """
    This service for recognition and processing audio to text.
    """
)
st.sidebar.info("Feel free to collaborate and comment on the work. The github link can be found "
                "[here](https://github.com/")


st.header("Trascribe Audio, only mp3 format!")
fileObject = st.file_uploader(label="Please upload your file")

if fileObject:
    st.text("Processing: ")

    # Получаем обьект файла
    bytes_data = fileObject.getvalue()
    f = open("soung.mp3", "wb")
    f.write(bytes_data)

    # Обрезаем файл до 30 сек
    file_name = 'soung'

    startMin = 0
    startSec = 0
    endMin = 0
    endSec = 60

    # Time to miliseconds
    startTime = startMin * 60 * 1000 + startSec * 1000
    endTime = endMin * 60 * 1000 + endSec * 1000

    # Opening file and extracting segment
    song = AudioSegment.from_mp3(file_name + '.mp3')
    extract = song[startTime:endTime]

    # Saving
    extract.export(file_name + '-extract.mp3', format="mp3")
    with st.spinner('Wait for it...'):
        SetLogLevel(0)

        # Проверяем наличие модели
        if not os.path.exists("model"):
            print(
                "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)

        # Устанавливаем Frame Rate
        FRAME_RATE = 16000
        CHANNELS = 1

        model = Model("model")
        rec = KaldiRecognizer(model, FRAME_RATE)
        rec.SetWords(True)

        # Используя библиотеку pydub делаем предобработку аудио
        mp3 = AudioSegment.from_mp3("soung-extract.mp3")
        mp3 = mp3.set_channels(CHANNELS)
        mp3 = mp3.set_frame_rate(FRAME_RATE)

        # Преобразуем вывод в json
        rec.AcceptWaveform(mp3.raw_data)
        result = rec.Result()
        text = json.loads(result)["text"]

        cased = subprocess.check_output('python3 recasepunc/recasepunc.py predict recasepunc/checkpoint', shell=True,
                                        text=True, input=text)

        audio_file = open('soung-extract.mp3', 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio / ogg')
        audio_file.close()

        st.subheader("Trascribe result: ")
        st.markdown(cased)
        f.close()
        os.remove("soung.mp3")
        os.remove("soung-extract.mp3")

    st.success('Done!')