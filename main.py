from download_tracks import Go_downloanding

import os
from datetime import datetime
import threading as thr
import subprocess

from imageio_ffmpeg import get_ffmpeg_exe
from imageio_ffmpeg import get_ffmpeg_version

# https://youtu.be/_WLdLUlBGOo

# Уил Смит
# https://www.youtube.com/watch?v=fiBLgEx6svA&list=RDfiBLgEx6svA&start_radio=1

# Playlist
# https://www.youtube.com/playlist?list=PLF2wVlabSmeE
# https://youtube.com/playlist?list=PLD6SPjEPomathzOFzCSvvMAlthuqRnSa9&si=KY77eGjr3fWRXrZH


###############    Exceptions   #################

from pytubefix.exceptions import RegexMatchError
from pytubefix.exceptions import HTMLParseError
from pytubefix.exceptions import AgeRestrictedError
from pytubefix.exceptions import MaxRetriesExceeded
from pytubefix.exceptions import VideoUnavailable

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
        self.buttons_navigation = (self.butt_save_one, self.save_playlist_button,
                                   self.next_button, self.prev_button)
        self.tuple_checkbox_buttons = (self.mp3, self.wav, self.aac,
                                       self.alac, self.m4a, self.avi,
                                       self.mpeg, self.mp4,)
        self.url_index = 0
        self.gen_all_urls_videos = []
        self.one_urls_video = []
        self.list_urs = []
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

    def thread_create_playlist_YouTube(self, urlvideo):
        thr.Thread(target=self.create_object_playlist_youtube, args=(urlvideo,), daemon=True).start()
        self.MySliderFlag = True
        Clock.schedule_interval(self.slider_callback, .1)

    def create_object_youtube(self, url_video):
        """При вставке ссылки на видео в Textinput- получаем
        объект YouTube и уст-ка картинки и названия видео"""
        if url_video:
            try:
                self.create_obj_one_video(url_video)
            except (RegexMatchError, HTMLParseError,TypeError, Exception) as er:
                self.lab_message.add_line(f' Ошибка:  [color=#FF0000]{er}[/color]')
                self.lab_message.add_line('             Объект YouTube не создан!')
                self.lab_message.add_line(f"[color=#FF0000]{50 * '*'}[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Создаю объект Playlist YouTube.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Создание плейлиста требует времени.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ожидайте[/color]")
                self.lab_message.add_line(f"{50 * '*'}")
                self.thread_create_playlist_YouTube(url_video)
            else:
                self.block_button(block=False)
                self.MySliderFlag = False
                self.positive_slider()
        else:
            self.block_button()
            self.OBJ_YouTube = None
            self.gen_all_urls_videos = []
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
        first_video = self.list_urs[0]
        self.create_obj_one_video(first_video)

    def create_object_playlist_youtube(self, url_video):
        try:
            OBJ_YouTube_Playlist = Playlist(url_video, )
            if OBJ_YouTube_Playlist:
                self.gen_all_urls_videos = OBJ_YouTube_Playlist.videos  # список OBJ
                self.list_urs = OBJ_YouTube_Playlist.video_urls  # список URLs
                self.message_create_playlist()
        except (KeyError, Exception):
            self.message_error_create_playlist(url_video)

    @mainthread
    def message_error_create_playlist(self, url_video):
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
        try:
            self.install_data_this_video()
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

    def install_data_this_video(self, ):
        self.lab_message.add_line(f"[color=#32CD32] Объект YouTube создан.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] Получаю название.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] Получаю картинку.[/color]")
        self.lab_message.add_line(f"{50 * '*'}")
        self.youtube_title.text = self.OBJ_YouTube.title[:70]
        img_thumb = self.OBJ_YouTube.thumbnail_url
        img = AsyncImage(source=img_thumb, fit_mode="contain")
        self.carusel.clear_widgets()
        self.carusel.add_widget(img)
        self.positive_slider()
        self.block_button(block=False)
        self.MySliderFlag = False  # Останавливает движение Slider

    def previous_video(self):
        if self.list_urs:
            self.url_index -= 1
            try:
                url_previous_video = self.list_urs[self.url_index]
                self.create_obj_one_video(url_previous_video)
            except IndexError:
                self.url_index = 0
                url_previous_video = self.list_urs[self.url_index]
                self.create_obj_one_video(url_previous_video)

    def next_video(self):
        if self.list_urs:
            self.url_index += 1
            try:
                url_next_video = self.list_urs[self.url_index]
                self.create_obj_one_video(url_next_video)
            except IndexError:
                self.url_index = 0
                url_next_video = self.list_urs[self.url_index]
                self.create_obj_one_video(url_next_video)

    ############################################################################################################################
    ############################################################################################################################
    ############################################################################################################################
    ############################################################################################################################
    @mainthread
    def message_playlist(self):
        self.lab_message.add_line(f"[color=#DCDCDC]Чем больше количество видео, тем длительнее работа.[/color]")
        self.lab_message.add_line(f"[color=#32CD32]{30 * ' '}Ожидайте.[/color]")

    def start_save_playlist(self):
        """ При нажатии на кнопку 'Сохранить плейлист' """
        self.message_playlist()
        Go_downloanding(DIR_DOWNLOAD,
                              self.gen_all_urls_videos,
                              self.lab_message,
                              self.tuple_checkbox_buttons,
                              self.buttons_navigation,
                              self.process_slider,
                              ).start(video=False)

    ############################################################################################################################
    ############################################################################################################################
    ############################################################################################################################
    ############################################################################################################################

    def start_save_one_track(self):
        """ При нажатии кнопки 'Сохранить ролик' """
        self.MySliderFlag = True
        self.one_urls_video = [self.OBJ_YouTube, ]
        if self.mp4.active:  # Если нажата радиокнопка скачивания видео
            self.lab_message.add_line(f"[color=#32CD32] Ищу видео.[/color]")
            thr.Thread(target=self.start_download_one_video, daemon=True).start()
        else:
            thr.Thread(target=self.start_download_one_sound, daemon=True).start()

    def start_download_one_sound(self):
        Go_downloanding(DIR_DOWNLOAD, self.one_urls_video,
                        self.lab_message,
                        self.tuple_checkbox_buttons,
                        self.buttons_navigation,
                        self.process_slider,
                        ).start(video=False)

    def start_download_one_video(self):
        Go_downloanding(DIR_DOWNLOAD, self.one_urls_video,
                        self.lab_message,
                        self.tuple_checkbox_buttons,
                        self.buttons_navigation,
                        self.process_slider,
                        ).start(video=True)

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

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
        self.title = "Наш ответ Ютубу"
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
