import os
import subprocess
from time import sleep

from kivy.clock import mainthread
from kivy.clock import Clock

from imageio_ffmpeg import get_ffmpeg_exe
from imageio_ffmpeg import get_ffmpeg_version

###############    Exceptions   #################
from pytubefix.exceptions import VideoUnavailable
from pytubefix.exceptions import RegexMatchError
from pytubefix.exceptions import AgeRestrictedError
from pytubefix.exceptions import MaxRetriesExceeded

from pytubefix import YouTube, Playlist

FFMPEG_LIB_VERSION = get_ffmpeg_version()
FFMPEG_LIB_EXE = get_ffmpeg_exe()

class Go_audio_downloanding:
    def __init__(self, directory, list_urls,
                 box_message, check_buttons:tuple,
                 buttons_navigation,
                 slider, ):
        self.MySliderFlag = True
        self.process_slider = slider
        (self.butt_save_one,self.save_playlist_button,
         self.next_button,self.prev_button) = buttons_navigation
        (self.mp3, self.wav, self.aac, self.alac,
         self.m4a, self.avi, self.mpeg, self.mp4) = check_buttons
        self.gen_urls = list_urls
        self.lab_message = box_message
        self.DIR_DOWNLOAD = directory

    def start(self):
        self.block_button()
        self.MySliderFlag = True
        Clock.schedule_interval(self.slider_callback, .1)
        for url in self.gen_urls:
            OBJ = self.create_obj_YouTube(url)
            STREAM = self.get_audio_stream(OBJ)
            self.start_download(STREAM)
            sleep(5)
            print("**********  sleep 5   *************")

    def create_obj_YouTube(self, url_video):
        print("create_obj_YouTube")
        OBJ_YouTube = YouTube(url_video, )
        return OBJ_YouTube

    def get_audio_stream(self,OBJ_YouTube):
        return OBJ_YouTube.streams.get_default_audio_track().first()

    @mainthread
    def start_download(self,STREAM):
        self.lab_message.add_line(f"[color=#32CD32] Создаю объект YouTube[/color]")
        try:
            path_load_audio_file = STREAM.download(self.DIR_DOWNLOAD, )
        except AttributeError:
            self.lab_message.add_line(f"    [color=#32CD32] Объект не создан.[/color]")
            self.lab_message.add_line(f'    Не является ссылкой YouTube.')
            self.lab_message.add_line(f'    [color=#FF0000]Сорвалась ссылка[/color]')
            self.lab_message.add_line(f'    [color=#FF0000]Перезапустите программу[/color]')
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(False)
            self.MySliderFlag = False
        except AgeRestrictedError:
            self.lab_message.add_line(
                f"    Ютубчег выставил этому видео ограничение 18+ [color=#FF0000]Скачать невозможно.[/color] ")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(False)
            self.MySliderFlag = False
        except MaxRetriesExceeded:
            self.lab_message.add_line(
                f"[color=#FF0000] Превышено максимальное количество повторных попыток соединения[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Плохое интернет соединение.[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Ютубчег просто так не отдаст контент на халяву.[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(False)
            self.MySliderFlag = False
        except VideoUnavailable:
            self.lab_message.add_line(f"[color=#FF0000] Видео не доступно для скачивания[/color]")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(False)
            self.MySliderFlag = False
        except Exception as err:
            self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(False)
            self.MySliderFlag = False
        else:
            directory = os.path.split(path_load_audio_file)[0]
            self.lab_message.add_line(f"[color=#32CD32] Объект YouTube создан.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] Качаю.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ждём![/color]")
            self.lab_message.add_line(f"[color=#32CD32] Сохраняю в:[/color] {directory}")
            self.lab_message.add_line(f"[color=#32CD32] Файл успешно скачан.[/color]")
            check_button = self.is_convert()
            self.choice_convert_for_audio(check_button, path_load_audio_file)


    def is_convert(self):
        for butt in (self.mp3, self.wav, self.aac, self.alac, self.m4a, self.avi, self.mpeg, self.mp4):
            if butt.state == "down":
                return butt.uid

    @mainthread
    def choice_convert_for_audio(self, uid_check_button, path_file):
        match uid_check_button:
            case self.mp3.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в MP3[/color]")
                if self.is_a_file(path_file, ".mp3"):
                    self.text_file_exist(path_file)
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в MP3[/color]")
                    self.start_convert(path_file, ".mp3")
            case self.wav.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в WAV[/color]")
                if self.is_a_file(path_file, ".wav"):
                    self.text_file_exist(path_file)
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в WAV[/color]")
                    self.start_convert(path_file, ".wav")
            case self.aac.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в AAC[/color]")
                if self.is_a_file(path_file, ".aac"):
                    self.text_file_exist(path_file)
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в AAC[/color]")
                    self.start_convert(path_file, ".aac")
            case self.alac.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать кодеком ALAC[/color]")
                if self.is_alac_file(path_file):
                    self.text_file_exist(path_file)
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую M4A кодеком ALAC[/color]")
                    self.start_convert_alac(path_file)
            case self.m4a.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать[/color]")
                if self.is_a_file(path_file, ".m4a"):
                    self.text_file_exist(path_file)

    @mainthread
    def text_file_exist(self,path_file):
        self.lab_message.add_line(f"[color=#32CD32] {15*' '}Файл уже существует.[/color]")
        self.lab_message.add_line(f"{15 * ' '}Аудиофайл в конвертации не нуждается")
        self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
        self.lab_message.add_line(f"{50 * '*'}")
        self.delete_old_files(path_file)
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
            self.block_button()
            self.delete_old_files(path_file)
        else:
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
                self.lab_message.add_line(f"[color=#FF0000] Ошибка imageio_ffmpeg. КОД:[/color] {err.returncode}")
                self.lab_message.add_line(f"[color=#FF0000] Ошибка [/color] {err.stderr}")
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
                self.delete_old_files(path_file)
            else:
                self.delete_old_files(path_file)
                self.lab_message.add_line("         Конвертация завершена")
                self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
                self.lab_message.add_line(f"{50 * '*'}")
        else:
            self.lab_message.add_line(" В конвертации не нуждается")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.positive_slider()
        self.block_button(False)
        self.MySliderFlag = False

    @mainthread
    def delete_old_files(self, path_audio_file):
        self.lab_message.add_line(f"{15 * ' '}[color=#32CD32] Удаляю временные файлы. [/color]")
        try:
            os.remove(path_audio_file)
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
        print("block_button",block)
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
