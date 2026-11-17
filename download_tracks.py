import os
import subprocess
from time import sleep
import threading

from kivy.clock import mainthread
from kivy.clock import Clock

from imageio_ffmpeg import get_ffmpeg_exe
from imageio_ffmpeg import get_ffmpeg_version

###############    Exceptions   #################
from pytubefix.exceptions import VideoUnavailable
from pytubefix.exceptions import AgeRestrictedError
from pytubefix.exceptions import MaxRetriesExceeded

FFMPEG_LIB_VERSION = get_ffmpeg_version()
FFMPEG_LIB_EXE = get_ffmpeg_exe()

class Go_downloanding:
    def __init__(self, directory, list_objs,
                 box_message, check_buttons:tuple,
                 buttons_navigation,
                 slider, ):

        self.MySliderFlag = True
        self.process_slider = slider
        (self.butt_save_one,self.save_playlist_button,
         self.next_button,self.prev_button) = buttons_navigation
        (self.mp3, self.wav, self.aac, self.alac,
         self.m4a, self.avi, self.mpeg, self.mp4) = check_buttons
        self.list_objects = list_objs
        self.lab_message = box_message
        self.DIR_DOWNLOAD = directory
        self.path_load_audio_file = None

    def start(self,video):
        self.block_button()
        if video:
            self.download_video()
        else:
            self.download_sound()

    def start_slider(self):
        Clock.schedule_interval(self.slider_callback, .1)

    def download_sound(self):
        for obj in self.list_objects:
            self.MySliderFlag = True
            Clock.schedule_interval(self.slider_callback, .1)
            audio_stream = self.get_audio_stream(obj)
            threading.Thread(target=self.start_download_audio_file, args=(audio_stream,)).start()
            sleep(5)

    def download_video(self):
        for obj in self.list_objects:
            self.MySliderFlag = True
            Clock.schedule_interval(self.slider_callback, .1)
            audio_stream = self.get_audio_stream(obj)
            threading.Thread(target=self.start_download_audio_file, args=(audio_stream,)).start()

            sleep(5)

            self.MySliderFlag = True
            threading.Thread(target=self.start_slider).start()
            video_stream = self.get_video_stream(obj)
            threading.Thread(target=self.start_download_video_file, args=(video_stream,)).start()



    @mainthread
    def start_download_video_file(self,Video_STREAM):
        try:
            path_load_video_file = Video_STREAM.download(self.DIR_DOWNLOAD, )
        except MaxRetriesExceeded as err:
            self.lab_message.add_line(f"[color=#FF0000] Превышено количество запросов.[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Ошибка: {err}[/color]")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.negative_slider()
            self.block_button(block=False)
            self.MySliderFlag = False
        except Exception as err:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка скачивания видео: {err}.[/color]")
            self.lab_message.add_line(f"{30 * ' '}      Работа завершена.")
            self.negative_slider()
            self.block_button(block=False)
            self.MySliderFlag = False
        else:
            directory = os.path.split(path_load_video_file)[0]
            self.lab_message.add_line(f"[color=#32CD32] Сохраняю видео в:[/color] {directory}")
            self.lab_message.add_line(f"{15 * ' '}Видеопоток успешно скачан.")
            self.lab_message.add_line(f"{50 * '*'}")
            self.start_combine_two_streams(path_load_video_file, self.path_load_audio_file)


    @mainthread
    def start_combine_two_streams(self, path_video_file, path_audio_file):
        self.lab_message.add_line(f"[color=#32CD32] Начинаю объединять потоки.[/color]")
        directory, file = os.path.split(path_video_file)
        new_file = os.path.join(directory, "video_" + file)
        command = [
            FFMPEG_LIB_EXE,
            '-i', path_video_file,  # входной видеофайл
            '-i', path_audio_file,  # входной аудиофайл
            '-c:v', 'copy',  # копировать видеопоток без перекодирования
            '-c:a', 'aac',
            '-shortest',
            '-y',  # перезаписать выходной файл без подтверждения
            new_file, ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as err:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка imageio_ffmpeg. КОД:[/color] {err.returncode}")
            self.lab_message.add_line(f"[color=#FF0000] Ошибка [/color] {err.stderr}")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.MySliderFlag = False
            self.block_button(block=False)
            self.negative_slider()
        else:
            self.delete_old_files(path_audio_file,)
            self.rename_video_file(new_file)
            self.lab_message.add_line("         Видео готово!")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.lab_message.add_line(f"{50 * '*'}")
            self.MySliderFlag = False
            self.block_button(block=False)
            self.positive_slider()

    @mainthread
    def rename_video_file(self,path_videofile):
        try:
            old_path,old_file_name = os.path.split(path_videofile)
            new_file_name = old_file_name.removeprefix("video_")
            new_path_video_file = os.path.join(old_path, new_file_name)
            if os.path.exists(new_path_video_file):
                os.remove(new_path_video_file)
            os.rename(path_videofile,new_path_video_file)
        except FileNotFoundError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка переименования файла. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] Файл не найден! [/color]")
        except PermissionError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка переименования файла. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] В доступе отказано! [/color]")
        except FileExistsError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка переименования файла. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] Файл существует! [/color]")
        else:
            self.lab_message.add_line(f"{50 * '*'}")

    @mainthread
    def message_get_video_stream(self,res,err=False):
        self.lab_message.add_line(f"[color=#32CD32] Видео найдено.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] Качество видео[/color] {res}.")
        self.lab_message.add_line(f"[color=#32CD32] Начинаю кач видео.[/color].")

    def get_video_stream(self,objYT):
        res_s = ["720p", "480p", "360p", "240p", "144p"]  # "1080p"
        for res in res_s:
            video = objYT.streams.filter(file_extension='mp4', type="video", res=res)
            if video:
                self.message_get_video_stream(res)
                return video[0]
            else:
                continue



    @mainthread
    def message_downloanding_audiostream(self, start=True):
        if start:
            self.lab_message.add_line(f"    [color=#32CD32] Получаю аудиопоток.[/color]")
        else:
            self.lab_message.add_line(f"    [color=#32CD32] Аудиопоток готов.[/color]")

    def get_audio_stream(self, objYT):
        self.message_downloanding_audiostream()
        audio_stream = objYT.streams.get_default_audio_track().first()
        self.message_downloanding_audiostream(start=False)
        return audio_stream


    @mainthread
    def message_AttributeError(self,):
        self.lab_message.add_line(f"    [color=#32CD32] Объект не создан.[/color]")
        self.lab_message.add_line(f'    Не является ссылкой YouTube.')
        self.lab_message.add_line(f'    [color=#FF0000]Сорвалась ссылка[/color]')
        self.lab_message.add_line(f'    [color=#FF0000]Перезапустите программу[/color]')
        self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
        self.block_button(False)
        self.MySliderFlag = False
    @mainthread
    def message_AgeRestrictedError(self,):
        self.lab_message.add_line(
            f"    Ютубчег выставил этому видео ограничение 18+ [color=#FF0000] ")
        self.lab_message.add_line(f"[color=#FF0000]Скачать невозможно.[/color]")
        self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
        self.block_button(False)
        self.MySliderFlag = False
    @mainthread
    def message_MaxRetriesExceeded(self,):
        self.lab_message.add_line(
            f"[color=#FF0000] Превышено максимальное количество повторных попыток соединения[/color]")
        self.lab_message.add_line(f"[color=#FF0000] Плохое интернет соединение.[/color]")
        self.lab_message.add_line(f"[color=#FF0000] Ютубчег просто так не отдаст контент на халяву.[/color]")
        self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
        self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
        self.block_button(False)
        self.MySliderFlag = False
    @mainthread
    def message_VideoUnavailable(self,):
        self.lab_message.add_line(f"[color=#FF0000] Видео не доступно для скачивания[/color]")
        self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
        self.block_button(False)
        self.MySliderFlag = False
    @mainthread
    def message_Exception(self,err):
        self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
        self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
        self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
        self.block_button(False)
        self.MySliderFlag = False
    @mainthread
    def message_success_save_file(self,directory,file_name):
        self.lab_message.add_line(f"[color=#32CD32] Качаю.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ждём![/color]")
        self.lab_message.add_line(f"[color=#32CD32] Сохраняю в:[/color] {directory}")
        self.lab_message.add_line(f"[color=#32CD32] Файл[/color] {file_name} [color=#32CD32]успешно скачан.[/color]")



    def start_download_audio_file(self, Audio_STREAM):

        try:
            self.path_load_audio_file = Audio_STREAM.download(self.DIR_DOWNLOAD, )
            directory, file_name = os.path.split(self.path_load_audio_file)
        except AttributeError:
            self.message_AttributeError()
        except AgeRestrictedError:
            self.message_AgeRestrictedError()
        except MaxRetriesExceeded:
            self.message_MaxRetriesExceeded()
        except VideoUnavailable:
            self.message_VideoUnavailable()
        except Exception as err:
            self.message_Exception(err,)
        else:
            self.message_success_save_file(directory,file_name)
            check_button = self.is_convert()
            self.choice_convert_for_audio(check_button, self.path_load_audio_file)


    def is_convert(self):
        for butt in (self.mp3, self.wav, self.aac, self.alac, self.m4a, self.avi, self.mpeg, self.mp4):
            if butt.state == "down":
                return butt.uid
    @ mainthread
    def message_is_convert(self,form,convert=False):
        self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в {form}[/color]")
        if convert:
            self.lab_message.add_line(f"[color=#32CD32] Конвертирую в {form}[/color]")



    def choice_convert_for_audio(self, uid_check_button, path_file):
        match uid_check_button:

            case self.mp3.uid:
                self.message_is_convert("MP3")
                if self.is_a_file(path_file, ".mp3"):
                    self.text_file_exist(path_file)
                else:
                    self.message_is_convert("MP3",True)
                    self.start_convert(path_file, ".mp3")

            case self.wav.uid:
                self.message_is_convert("WAV")
                if self.is_a_file(path_file, ".wav"):
                    self.text_file_exist(path_file)
                else:
                    self.message_is_convert("WAV",True)
                    self.start_convert(path_file, ".wav")

            case self.aac.uid:
                self.message_is_convert("AAC")
                if self.is_a_file(path_file, ".aac"):
                    self.text_file_exist(path_file)
                else:
                    self.message_is_convert("AAC",True)
                    self.start_convert(path_file, ".aac")

            case self.alac.uid:
                self.message_is_convert("ALAC")
                if self.is_alac_file(path_file):
                    self.text_file_exist(path_file)
                else:
                    self.message_is_convert("ALAC",True)
                    self.start_convert_alac(path_file)

            case self.m4a.uid:
                self.message_is_convert("M4A")
                if self.is_a_file(path_file, ".m4a"):
                    self.text_file_exist(path_file)

    @mainthread
    def text_file_exist(self,path_file):
        file_name = os.path.split(path_file)[1]
        self.lab_message.add_line(f"[color=#32CD32]     Файл [/color]{file_name}.")
        self.lab_message.add_line(f"[color=#32CD32] {15*' '}Уже существует.[/color]")
        self.lab_message.add_line(f"{15 * ' '}Аудиофайл в конвертации не нуждается")
        self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
        self.lab_message.add_line(f"{50 * '*'}")
        self.block_button(False)
        self.MySliderFlag = False
        self.positive_slider()

    @mainthread
    def start_convert_alac(self, path_file):
        directory, file = os.path.split(path_file)
        new_file = os.path.join(directory, "_alac_" + file)
        convert_command = [
            FFMPEG_LIB_EXE,
            "-y",
            "-i",
            fr"{path_file}",
            "-c:a", "alac",
            fr"{new_file}"]
        try:
            subprocess.run(convert_command, check=True)
        except subprocess.CalledProcessError as err:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка imageio_ffmpeg. КОД:[/color] {err.returncode}")
            self.lab_message.add_line(f"[color=#FF0000] Ошибка [/color] {err.stderr}")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(False)
            self.delete_old_files(path_file)
        else:
            self.delete_old_files(path_file)
            self.lab_message.add_line("         Конвертация завершена")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.lab_message.add_line(f"{50 * '*'}")
            self.positive_slider()
            self.block_button(False)
            self.MySliderFlag = False


    def is_a_file(self, path_file, format_file):
        new_file_path = os.path.splitext(path_file)[0] + format_file
        directory = os.path.split(path_file)[0]
        new_file = os.path.split(new_file_path)[1]
        if new_file in os.listdir(directory):
            return True

    def is_alac_file(self, path_file):
        directory, file = os.path.split(path_file)
        new_file = "_alac_" + file
        if new_file in os.listdir(directory):
            return True

    @mainthread
    def message_start_convert_error(self,path_file,err):
        self.lab_message.add_line(f"[color=#FF0000] Ошибка imageio_ffmpeg. КОД:[/color] {err.returncode}")
        self.lab_message.add_line(f"[color=#FF0000] Ошибка [/color] {err.stderr}")
        self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")

    @mainthread
    def message_convert_finish(self,file_name):
        self.lab_message.add_line(f" Конвертация {file_name} завершена")
        # self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
        self.lab_message.add_line(f"{50 * '*'}")

    def start_convert(self, path_file, format):
        """-y => разрешить перезапись выходного файла без подтверждения»."""
        if format:
            new_file = os.path.splitext(path_file)[0] + format
            convert_command = [
                FFMPEG_LIB_EXE,
                "-y",
                "-i", fr"{path_file}",
                fr"{new_file}"]
            try:
                subprocess.run(convert_command, check=True)
            except subprocess.CalledProcessError as err:
                self.message_start_convert_error(path_file,err)
                self.delete_old_files(path_file)
                self.MySliderFlag = False
            else:
                self.message_convert_finish(new_file)
                self.delete_old_files(path_file)
                self.MySliderFlag = False
        else:
            file_name = os.path.splitext(path_file)[1]
            self.message_convert_finish(file_name)
            self.positive_slider()
            self.MySliderFlag = False
        self.block_button(False)

    @mainthread
    def delete_old_files(self, path_file):
        self.lab_message.add_line(f"{15 * ' '}[color=#32CD32] Удаляю временные файлы. [/color]")
        try:
            os.remove(path_file)
        except FileNotFoundError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка удаления временных файлов. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] Файлы не найдены! [/color]")
        except PermissionError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка удаления временных файлов. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] В доступе отказано! [/color]")
        else:
            self.lab_message.add_line(f"[color=#32CD32]{25 * ' '} Успешно!. [/color]")
            self.lab_message.add_line(f"{50 * '*'}")

    def block_button(self, block=True):
        self.save_playlist_button.disabled = block
        self.next_button.disabled = block
        self.prev_button.disabled = block
        self.butt_save_one.disabled = block


    def slider_callback(self, qt):
        if self.MySliderFlag:
            self.process_slider.value += 1
            if self.process_slider.value >= 100:
                self.process_slider.value = 0
        else:
            print("slider_callback stop")
            return False

    def positive_slider(self):
        self.process_slider.value_track_color = "#228B22"  # "green" # "ForestGreen"
        self.process_slider.value = 100

    def negative_slider(self):
        self.process_slider.value_track_color = "red"
        self.MySliderFlag = False
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
