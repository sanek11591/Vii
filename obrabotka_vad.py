import torch
import pathlib
import ffmpeg
import shutil
import random


class VAD:
    @staticmethod
    def selerio_vad(path_to_audio, directory_for_save_files):
        directory = ".\\silero"
        sampling_rate = 16000
        name_of_audio = pathlib.Path(path_to_audio).name

        torch.set_num_threads(8)
        use_onnx = True
        model, utils = torch.hub.load(directory,
                                      source='local',
                                      model='silero_vad',
                                      onnx=use_onnx)

        (get_speech_timestamps,
         save_audio,
         read_audio,
         VADIterator,
         collect_chunks) = utils
        audio_formats = [".mp3", ".ogg", ".m4a"]
        change_format = False
        if pathlib.Path(path_to_audio).suffix in audio_formats:
            p = pathlib.Path(str(pathlib.PurePath(path_to_audio).parent) + "\\temp")
            p.mkdir(parents=True, exist_ok=True)
            stream = ffmpeg.input(path_to_audio)
            stream = ffmpeg.output(stream,
                                   str(pathlib.PurePath(path_to_audio).parent) + "\\temp\\" + str(
                                       pathlib.Path(path_to_audio).stem) + ".wav")
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            path_to_audio = str(pathlib.PurePath(path_to_audio).parent) + "\\temp\\" + str(
                pathlib.Path(path_to_audio).stem) + ".wav"
            name_of_audio = pathlib.Path(path_to_audio).name
            change_format = True
        try:
            wav = read_audio(f'{path_to_audio}', sampling_rate=sampling_rate)
            speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate, max_speech_duration_s=30,
                                                      speech_pad_ms=1000)

            save_audio(f'{directory_for_save_files}\\{random.randint(1, 100000)}_речь_{name_of_audio}',
                       collect_chunks(speech_timestamps, wav), sampling_rate=sampling_rate)
            if change_format:
                shutil.rmtree(pathlib.Path(path_to_audio).parent)
            return f"Обработка записи {name_of_audio} с помощью VAD завершена.", True
        except Exception as e:
            return f"Произошла ошибка: {e}", False
