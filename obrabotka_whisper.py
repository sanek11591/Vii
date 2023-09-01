import whisper
from datetime import timedelta


class Whisper:
    @staticmethod
    def speach_to_text(directory_of_audio_for_processing, model_size="large", device='cpu'):
        try:
            model = whisper.load_model(download_root=".\\whisper_models", name=model_size, in_memory=True,
                                       device=device)
            result = model.transcribe(str(directory_of_audio_for_processing))
            with open(str(directory_of_audio_for_processing.parent) + "\\" +
                      str(directory_of_audio_for_processing.stem) + "_метки_" + ".txt", "w") as file:
                for i in result['segments']:
                    file.write(f'{i["start"]}-{i["end"]}: {i["text"]}' + '\n')
            with open(str(directory_of_audio_for_processing.parent) + "\\" +
                      str(directory_of_audio_for_processing.stem) + "_без_метки_" + ".txt", "w") as file:
                for i in result['segments']:
                    file.write(f'{i["text"]}' + '\n')
            for segment in result['segments']:
                start_time = str(0) + str(timedelta(seconds=int(segment['start']))) + ',000'
                end_time = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
                text = segment['text']
                segment_id = segment['id'] + 1
                segment = f"{segment_id}\n{start_time} --> {end_time}\n{text[1:] if text[0] == ' ' else text}\n\n"

                srt_filename = (str(directory_of_audio_for_processing.parent) + "\\" +
                                str(directory_of_audio_for_processing.stem) + f".srt")
                with open(srt_filename, 'a', encoding='utf-8') as srtFile:
                    srtFile.write(segment)
            return f"Обработка файла {directory_of_audio_for_processing.name} завершена.", True
        except RuntimeError as rn:
            return f"Ошибка: {rn}", False
