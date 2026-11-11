from download_tracks import Go_audio_downloanding

import os
from datetime import datetime
import threading as thr
import subprocess

from imageio_ffmpeg import get_ffmpeg_exe
from imageio_ffmpeg import get_ffmpeg_version



from functools import partial

# https://youtu.be/_WLdLUlBGOo

# Уил Смит
# https://www.youtube.com/watch?v=fiBLgEx6svA&list=RDfiBLgEx6svA&start_radio=1

# Playlist
# https://www.youtube.com/playlist?list=PLF2wVlabSmeE
# https://youtube.com/playlist?list=PLD6SPjEPomathzOFzCSvvMAlthuqRnSa9&si=KY77eGjr3fWRXrZH


###############    Exceptions   #################
from pytubefix.exceptions import VideoUnavailable
from pytubefix.exceptions import RegexMatchError
from pytubefix.exceptions import AgeRestrictedError
from pytubefix.exceptions import MaxRetriesExceeded

from pytubefix import YouTube, Playlist

from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.image import Image
from kivy.clock import mainthread
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.core.window import Window

from kivy.metrics import sp, dp

"""Директория main.py"""
current_dir = os.path.dirname(__file__)  # путь к папке
DIR_KV_FILE = os.path.join(current_dir, "main_kv.kv")
DIR_IMG_FILE = os.path.join(current_dir, "IMG")
current_download_path = os.getcwd()
if not os.path.exists(os.path.join(current_download_path, "Download")):
    os.mkdir(os.path.join(current_download_path, "Download"))
DIR_DOWNLOAD = os.path.join(current_download_path, "Download")

FFMPEG_LIB_VERSION = get_ffmpeg_version()
FFMPEG_LIB_EXE = get_ffmpeg_exe()

Builder.load_file(DIR_KV_FILE)


class MySlider(Slider):
    pass


class MyCarousel(Carousel):
    pass


class MyScroll(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bar_width = 10
        self.do_scroll_x = False


class LabelMessage(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.size_hint_x = 1
        self.size_hint_y = None
        self.font_size = sp(16)
        self.height = self.font_size + sp(2)
        self.halign = "left"
        self.text_size = (Window.width - dp(20), None)


class BoxMessage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.size_hint_x = 1
        self.bind(minimum_height=self.setter('height'))

    def add_line(self, message):
        """Вставляет время и сообщение в Label.
        Размещает у себя"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        lbl_message = LabelMessage(text=time_str + " " + message)
        self.add_widget(lbl_message)


class ReadOnlyTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.text == "Вставте URL (ссылку) YouTube.":
                self.text = ""
            if touch.is_double_tap:
                self.text = ""


class Main(BoxLayout):
    current_folder = StringProperty(DIR_IMG_FILE)
    mp3 = ObjectProperty()
    wav = ObjectProperty()
    aac = ObjectProperty()
    alac = ObjectProperty()
    m4a = ObjectProperty()
    avi = ObjectProperty()
    mpeg = ObjectProperty()
    mp4 = ObjectProperty()

    lab_quant_videos = ObjectProperty()
    lab_message = ObjectProperty()
    scrll = ObjectProperty()
    process_slider = ObjectProperty()
    butt_save_one = ObjectProperty()
    save_playlist_button = ObjectProperty()
    next_button = ObjectProperty()
    prev_button = ObjectProperty()
    carusel = ObjectProperty()
    input_ref = ObjectProperty()
    youtube_title = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.MySliderFlag = True
        self.OBJ_YouTube = None
        self.OBJ_img_thumb = None
        self.buttons_navigation = (self.butt_save_one,self.save_playlist_button,
                                    self.next_button,self.prev_button)
        self.tuple_checkbox_buttons = (self.mp3, self.wav, self.aac,
                                       self.alac, self.m4a, self.avi,
                                       self.mpeg, self.mp4,)
        self.url_index = 0
        self.gen_all_urls_videos = [None, ]
        self.one_urls_video = [None, ]
        self.lab_message.add_line(f"        [color=#32CD32]{FFMPEG_LIB_VERSION}[/color]")
        self.lab_message.add_line(f"[color=#32CD32]{30 * ' '}Запуск программы.[/color]")
        self.lab_message.add_line(f"{50 * '*'}")
        self.block_button()

    ################################################################################################################
    def slider_callback(self, qt):
        if self.MySliderFlag:
            self.process_slider.value += 1
            if self.process_slider.value >= 100:
                self.process_slider.value = 0
        else:
            return False

    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################

    def thread_create_playlist_YouTube(self, urlvideo, qt):
        thr.Thread(target=self.create_object_playlist_youtube, args=(urlvideo,), daemon=True).start()

    def create_object_youtube(self, url_video):
        """При вставке ссылки на видео в Textinput- получаем
        объект YouTube и уст-ка картинки и названия видео"""
        if url_video:
            try:
                self.create_obj_one_video(url_video)
                self.gen_all_urls_videos[0] = url_video
                self.block_button(block=False)
                self.MySliderFlag = False
                self.positive_slider()
            except (RegexMatchError, Exception) as er:
                self.lab_message.add_line(f' Ошибка:  [color=#FF0000]{er}[/color]')
                self.lab_message.add_line('             Объект YouTube не создан!')
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Создаю объект Playlist YouTube.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Создание плейлиста требует времени.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ожидайте[/color]")
                self.lab_message.add_line(f"{50 * '*'}")
                Clock.schedule_interval(self.slider_callback, .1)
                Clock.schedule_once(partial(self.thread_create_playlist_YouTube, url_video), .1)

        else:
            self.block_button()
            self.OBJ_YouTube = None
            self.gen_all_urls_videos = [None, ]
            self.install_image_carousel_by_default()
            self.process_slider.value_track_color = "green"
            self.process_slider.value = 0
            self.lab_quant_videos.text = "0"


    @mainthread
    def message_create_playlist(self):
        count_videos_url = len(self.gen_all_urls_videos)
        self.lab_message.add_line(f"        Объект Playlist YouTube создан.")
        self.lab_message.add_line(f"[color=#32CD32] Список адресов получен.[/color]")
        self.lab_quant_videos.text = str(count_videos_url)
        self.lab_message.add_line(
            f"[color=#32CD32] Количество видео в плейлисте:[/color] [color=#DCDCDC][size=20]{count_videos_url}[/size][/color]")
        self.lab_message.add_line(f"{50 * '*'}")
        first_video = self.gen_all_urls_videos[0]
        self.create_obj_one_video(first_video)

    @mainthread
    def create_object_playlist_youtube(self, url_video):
        try:
            OBJ_YouTube_Playlist = Playlist(url_video, )
            if OBJ_YouTube_Playlist:
                self.gen_all_urls_videos = OBJ_YouTube_Playlist.video_urls  # список URL
                self.message_create_playlist()
        except (KeyError, Exception):
            self.MySliderFlag = False
            self.lab_message.add_line(
                f' Ошибка: [color=#FF0000]{url_video}[/color] Не является ссылкой на PlayList YouTube.')
            self.lab_message.add_line('         Объект PlayList YouTube не создан!')
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button()
            self.negative_slider()

    def create_obj_one_video(self, url_video):
        self.lab_message.add_line(f"[color=#32CD32] Создаю объект YouTube[/color]")
        self.OBJ_YouTube = YouTube(url_video, )
        self.one_urls_video = [url_video, ]
        self.install_data_this_video()

    def install_data_this_video(self, ):
        self.lab_message.add_line(f"[color=#32CD32] Объект YouTube создан.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] Получаю название.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] Получаю картинку.[/color]")
        self.lab_message.add_line(f"{50 * '*'}")
        try:
            self.youtube_title.text = self.OBJ_YouTube.title[:70]
            img_thumb = self.OBJ_YouTube.thumbnail_url
            img = AsyncImage(source=img_thumb, fit_mode="contain")
            self.carusel.clear_widgets()
            self.carusel.add_widget(img)
            self.positive_slider()
            self.block_button(block=False)
            self.MySliderFlag = False # Останавливает движение Slider

        except Exception as err:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка получения заголовка[/color]")
            self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Ошибка получения картинки[/color]")
            self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
            self.lab_message.add_line(
                f"[color=#FF0000] Возможная причина:[/color] [color=#32CD32]Отсутствует соединение с интернетом[/color]")
            self.lab_message.add_line(f"{50 * '*'}")
            self.block_button(block=False)
            self.negative_slider()

    def previous_video(self):
        self.url_index -= 1
        try:
            url_previous_video = self.gen_all_urls_videos[self.url_index]
            self.create_obj_one_video(url_previous_video)
        except IndexError:
            self.url_index = 0
            url_previous_video = self.gen_all_urls_videos[self.url_index]
            self.create_obj_one_video(url_previous_video)

    def next_video(self):
        self.url_index += 1
        try:
            url_next_video = self.gen_all_urls_videos[self.url_index]
            self.create_obj_one_video(url_next_video)
        except IndexError:
            self.url_index = 0
            url_next_video = self.gen_all_urls_videos[self.url_index]
            self.create_obj_one_video(url_next_video)

    ############################################################################################################################
    ############################################################################################################################
    ############################################################################################################################
    ############################################################################################################################

    def start_save_one_track(self):
        """ При нажатии кнопки 'Сохранить ролик' """
        self.MySliderFlag = True
        if self.mp4.active:  # Если нажата радиокнопка скачивания видео
            self.lab_message.add_line(f"[color=#32CD32] Ищу видео.[/color]")
            self.thread_download_video()
        else:
            thr.Thread(target=self.start_download_one_track, daemon=True).start()

    def start_download_one_track(self):
        Go_audio_downloanding(DIR_DOWNLOAD, self.one_urls_video,
                              self.lab_message,
                              self.tuple_checkbox_buttons,
                              self.buttons_navigation,
                              self.process_slider,
                              ).start()

    def thread_download_video(self):
        thr.Thread(target=self.download_video_stream, daemon=True).start()

    def get_video_stream(self):
        res_s = ["720p", "480p", "360p", "240p", "144p"]  # "1080p"
        for res in res_s:
            video = self.OBJ_YouTube.streams.filter(file_extension='mp4', type="video", res=res)
            if video:
                self.lab_message.add_line(f"[color=#32CD32] Видео найдено.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Качество видео[/color] {res}.")
                self.lab_message.add_line(f"[color=#32CD32] Начинаю кач видео.[/color].")
                return video[0]
            else:
                self.lab_message.add_line(f"[color=#FF0000] Качество видео {res} не найдено.[/color]")
                continue

    @mainthread
    def download_video_stream(self):
        stream_video = self.get_video_stream()
        try:
            path_load_video_file = stream_video.download(DIR_DOWNLOAD, )
        except MaxRetriesExceeded as err:
            self.lab_message.add_line(f"[color=#FF0000] Превышено количество запросов.[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Ошибка: {err}[/color]")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.negative_slider()
            self.block_button(block=False)
        except Exception as err:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка скачивания видео: {err}.[/color]")
            self.lab_message.add_line(f"{30 * ' '}      Работа завершена.")
            self.negative_slider()
            self.block_button(block=False)
        else:
            directory = os.path.split(path_load_video_file)[0]
            self.lab_message.add_line(f"[color=#32CD32] Сохраняю видео в:[/color] {directory}")
            self.lab_message.add_line(f"{15 * ' '}Файл успешно скачан.")
            self.lab_message.add_line(f"{50 * '*'}")
            self.lab_message.add_line(f"{15 * ' '}Начинаю качать аудиопоток")
            path_audio_file = self.start_save_audiotrack_for_video()
            self.start_combine_two_streams(path_load_video_file, path_audio_file)

    def start_save_audiotrack_for_video(self):
        self.mess_audiotrack_for_video("Создание объекта")
        try:
            path_load_audio_file = self.OBJ_YouTube.streams.get_default_audio_track().first().download(DIR_DOWNLOAD, )
            self.mess_audiotrack_for_video("Объект создан")
        except AttributeError:
            self.negative_slider()
            self.block_button(block=False)
            self.install_image_carousel_by_default()
        except AgeRestrictedError:
            self.mess_audiotrack_for_video("AgeRestrictedError")
            self.negative_slider()
            self.block_button(block=False)
        except MaxRetriesExceeded:
            self.mess_audiotrack_for_video("MaxRetriesExceeded")
            self.negative_slider()
            self.block_button(block=False)
        except VideoUnavailable:
            self.mess_audiotrack_for_video("VideoUnavailable")
            self.negative_slider()
            self.block_button(block=False)
        except Exception as err:
            self.err = err
            self.mess_audiotrack_for_video("Exception")
            self.negative_slider()
            self.block_button(block=False)
        else:
            self.directory = os.path.split(path_load_audio_file)[0]
            self.mess_audiotrack_for_video("save")
            return path_load_audio_file  # Возвращает путь для объединения с видео

    @mainthread
    def mess_audiotrack_for_video(self, message):
        match message:
            case "Создание объекта":
                self.lab_message.add_line(
                    f"[color=#32CD32] Соединение....Создание объекта[/color] [color=#FAEBD7]YouTube[/color]")
            case "Объект создан":
                self.lab_message.add_line(
                    f"[color=#32CD32] Объект[/color] [color=#FAEBD7]YouTube[/color] [color=#32CD32]создан.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Качаю аудиопоток.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ждём![/color]")
            case "save":
                self.lab_message.add_line(f"[color=#32CD32] {15 * ' '}Файл успешно скачан.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Сохраняю в:[/color] {self.directory}")
            case "AgeRestrictedError":
                self.lab_message.add_line(
                    f"    Ютубчег выставил этому видео ограничение 18+ [color=#FF0000]Скачать невозможно.[/color] ")
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            case "AttributeError":
                video_url = self.input_ref.text
                self.lab_message.add_line(f"    [color=#32CD32] Объект не создан.[/color]")
                self.lab_message.add_line(f'    "{video_url}"- [color=#FF0000]не является ссылкой YouTube.[/color]')
                self.lab_message.add_line(f'    [color=#FF0000]Сорвалась ссылка[/color]')
                self.lab_message.add_line(f'    [color=#FF0000]Перезапустите программу[/color]')
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            case "MaxRetriesExceeded":
                self.lab_message.add_line(
                    f"[color=#FF0000] Превышено максимальное количество повторных попыток соединения[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Плохое интернет соединение.[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Ютубчег просто так не отдаст контент на халяву.[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            case "VideoUnavailable":
                self.lab_message.add_line(f"[color=#FF0000] Видео не доступно для скачивания[/color]")
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            case "Exception":
                self.lab_message.add_line(f"[color=#FF0000] {self.err}[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")

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
            self.negative_slider()
        else:
            self.delete_old_video_files(path_video_file, path_audio_file)
            self.lab_message.add_line("         Видео готово!")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.lab_message.add_line(f"{50 * '*'}")
            self.MySliderFlag = False
            self.block_button(block=False)
            self.positive_slider()

    def delete_old_video_files(self, path_video_file, path_audio_file):
        try:
            os.remove(path_video_file)
            os.remove(path_audio_file)
        except FileNotFoundError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка удаления временных файлов. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] Файлы не найдены! [/color]")
        except PermissionError:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка удаления временных файлов. [/color]")
            self.lab_message.add_line(f"[color=#FF0000] В доступе отказано! [/color]")

    def delete_old_audio_files(self, path_audio_file):
        self.lab_message.add_line(f"[color=#32CD32] Удаляю временные файлы. [/color]")
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

    ################################################################################################
    ################################################################################################
    ################################################################################################
    ################################################################################################
    @mainthread
    def start_save_audio_track(self):
        self.lab_message.add_line(f"[color=#32CD32] Соединение....Создание объекта YouTube[/color]")
        try:
            # path_load_file = self.OBJ_YouTube.streams.get_audio_only().download(DIR_DOWNLOAD, )
            path_load_audio_file = self.OBJ_YouTube.streams.get_default_audio_track().first().download(DIR_DOWNLOAD, )
        except AttributeError:
            video_url = self.input_ref.text
            self.lab_message.add_line(f"    [color=#32CD32] Объект не создан.[/color]")
            self.lab_message.add_line(f'    "{video_url}"- [color=#FF0000]не является ссылкой YouTube.[/color]')
            self.lab_message.add_line(f'    [color=#FF0000]Сорвалась ссылка[/color]')
            self.lab_message.add_line(f'    [color=#FF0000]Перезапустите программу[/color]')
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(block=False)
            self.install_image_carousel_by_default()
            self.negative_slider()
        except AgeRestrictedError:
            self.lab_message.add_line(
                f"    Ютубчег выставил этому видео ограничение 18+ [color=#FF0000]Скачать невозможно.[/color] ")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(block=False)
            self.negative_slider()
        except MaxRetriesExceeded:
            self.lab_message.add_line(
                f"[color=#FF0000] Превышено максимальное количество повторных попыток соединения[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Плохое интернет соединение.[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Ютубчег просто так не отдаст контент на халяву.[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(block=False)
            self.negative_slider()
        except VideoUnavailable:
            self.lab_message.add_line(f"[color=#FF0000] Видео не доступно для скачивания[/color]")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(block=False)
            self.negative_slider()
        except Exception as err:
            self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
            self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
            self.block_button(block=False)
            self.negative_slider()
        else:
            directory = os.path.split(path_load_audio_file)[0]
            self.lab_message.add_line(f"[color=#32CD32] Объект YouTube создан.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] Качаю.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ждём![/color]")
            self.lab_message.add_line(f"[color=#32CD32] Сохраняю в:[/color] {directory}")
            self.lab_message.add_line(f"[color=#32CD32] Файл успешно скачан.[/color]")
            check_button = self.is_convert()
            self.choice_convert_for_audio(check_button, path_load_audio_file)

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

    def choice_convert_for_audio(self, uid_check_button, path_file):
        match uid_check_button:
            case self.mp3.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в MP3[/color]")
                if self.is_a_file(path_file, ".mp3"):
                    self.text_file_exist()
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в MP3[/color]")
                    self.start_convert(path_file, ".mp3")
            case self.wav.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в WAV[/color]")
                if self.is_a_file(path_file, ".wav"):
                    self.text_file_exist()
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в WAV[/color]")
                    self.start_convert(path_file, ".wav")
            case self.aac.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в AAC[/color]")
                if self.is_a_file(path_file, ".aac"):
                    self.text_file_exist()
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в AAC[/color]")
                    self.start_convert(path_file, ".aac")
            case self.alac.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать кодеком ALAC[/color]")
                if self.is_alac_file(path_file):
                    self.text_file_exist()
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую M4A кодеком ALAC[/color]")
                    self.start_convert_alac(path_file)
            case self.m4a.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать[/color]")
                if self.is_a_file(path_file, ".m4a"):
                    self.text_file_exist()

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
            self.block_button(block=False)
            self.negative_slider()
        else:
            self.delete_old_audio_files(path_file)
            self.lab_message.add_line("         Конвертация завершена")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.lab_message.add_line(f"{50 * '*'}")
            self.block_button(block=False)
            self.positive_slider()

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
                self.block_button(block=False)
                self.negative_slider()
            else:
                self.delete_old_audio_files(path_file)
                self.lab_message.add_line("         Конвертация завершена")
                self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
                self.lab_message.add_line(f"{50 * '*'}")
                self.block_button(block=False)
                self.MySliderFlag = False
                self.positive_slider()
        else:
            self.lab_message.add_line(" В конвертации не нуждается")
            self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
            self.block_button(block=False)
            self.MySliderFlag = False
            self.positive_slider()

    def is_convert(self):
        self.tuple_checkbox_buttons = (self.mp3, self.wav, self.aac,
                                       self.alac, self.m4a, self.avi,
                                       self.mpeg, self.mp4,)
        for butt in self.tuple_checkbox_buttons:
            if butt.state == "down":
                return butt.uid

    def block_button(self, block=True):
        if self.mp4.state == "down":
            self.save_playlist_button.disabled = True
        else:
            self.save_playlist_button.disabled = block
        self.next_button.disabled = block
        self.prev_button.disabled = block
        self.butt_save_one.disabled = block

    @mainthread
    def install_image_carousel_by_default(self):
        self.youtube_title.text = ""
        img = Image(source=os.path.join(current_dir, "IMG", "no_image.jpg"),
                    fit_mode="fill")
        self.carusel.clear_widgets()
        self.carusel.add_widget(img)

    def text_file_exist(self):
        self.lab_message.add_line(f"[color=#32CD32] Файл уже существует.[/color]")
        self.lab_message.add_line("     Аудиофайл в конвертации не нуждается")
        self.lab_message.add_line(f"{30 * ' '}Работа завершена.")
        self.lab_message.add_line(f"{50 * '*'}")
        self.block_button(block=False)
        self.MySliderFlag = False
        self.positive_slider()

    def turnoff_radiobutton(self, act):
        if act:
            self.aac.disabled = act
            self.mp3.disabled = act
            self.wav.disabled = act
            self.alac.disabled = act
            self.m4a.state = "down"
            self.avi.disabled = act
            self.mpeg.disabled = act
            self.save_playlist_button.disabled = act

        else:
            self.mp3.disabled = act
            self.mp3.state = "down"
            self.wav.disabled = act
            self.aac.disabled = act
            self.alac.disabled = act
            self.m4a.disabled = act
            self.save_playlist_button.disabled = act

    ##########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    @mainthread
    def message_playlist(self):
        self.lab_message.add_line(f"[color=#DCDCDC]Чем больше количество видео, тем длительнее работа.[/color]")
        self.lab_message.add_line(f"[color=#32CD32]{30 * ' '}Ожидайте.[/color]")

    def start_save_playlist(self):
        """ При нажатии на кнопку 'Сохранить плейлист' """
        self.message_playlist()
        Go_audio_downloanding(DIR_DOWNLOAD,
                              self.gen_all_urls_videos,
                              self.lab_message,
                              self.tuple_checkbox_buttons,
                              self.buttons_navigation,
                              self.process_slider,
                              ).start()


    def thread_save_playlist_button(self):
        thr.Thread(target=self.start_save_playlist, daemon=True).start()

    def positive_slider(self):
        self.process_slider.value_track_color = "#228B22"  # "green" # "ForestGreen"
        self.process_slider.value = 100

    def negative_slider(self):
        self.process_slider.value_track_color = "red"
        self.MySliderFlag = False


class MyYouTubeApp(App):
    def build(self):
        return Main()


MyYouTubeApp().run()

# command = [
#         'ffmpeg',
#         '-i', video_path,  # входной видеофайл
#         '-i', audio_path,  # входной аудиофайл
#         '-c:v', 'copy',  # копировать видеопоток без перекодирования
#         '-c:a', 'aac', # перекодировать аудио в AAC (для MP4)
#         '-shortest',  # обрезать по самому короткому файлу
#         '-y',  # перезаписать выходной файл без подтверждения
#         video_path, ]

# def play_file(self):
#     self.sound = SoundLoader.load(self.mp3_file_dir)  # self.load_audio)
#     self.sound.play()
#
#
# def stop_play(self):
#     self.sound.stop()
#
#
# def seek_position(self):
#     self.sound.seek(2000)
