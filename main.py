import ffmpeg
import os
from datetime import datetime
import threading as thr
import subprocess

###############    Exceptions   #################
from pytubefix.exceptions import VideoUnavailable
from pytubefix.exceptions import RegexMatchError
from pytubefix.exceptions import AgeRestrictedError
from pytubefix.exceptions import MaxRetriesExceeded



"""urllib.error.URLError: <urlopen error [WinError 10060] Попытка установить соединение была безуспешной, 
т.к. от другого компьютера за требуемое время не получен нужный отклик, или было разорвано уже установленное
 соединение из-за неверного отклика уже подключенного компьютера>"""
from pytubefix import YouTube,Playlist



from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.clock import mainthread
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from kivy.core.window import Window

"""Директория main.py"""
current_dir = os.getcwd()
if not os.path.exists(os.path.join(current_dir, "Download")):
    os.mkdir(os.path.join(current_dir, "Download"))
DIR_DOWNLOAD = os.path.join(current_dir, "Download")

def is_ffmpeg():
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    return result.stdout[:31]  # version ffmpeg

FFMPEG_LIB = False #is_ffmpeg()


Builder.load_file("main_kv.kv")

class LabelMessage(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = 10
        self.lines = []

    def add_line(self, new_line):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        self.lines.append(time_str +" "+ new_line)
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)
        self.update_text()

    def update_text(self):
        """Обновляет текст Label."""
        self.text = '\n'.join(self.lines)

# Уил Смит
# https://www.youtube.com/watch?v=fiBLgEx6svA&list=RDfiBLgEx6svA&start_radio=1&pp=oAcB
# Playlist
# https://www.youtube.com/playlist?list=PLF2wVlabSmeE

class MyCarousel(Carousel):
    pass

class ReadOnlyTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # def do_backspace(self, from_undo=True, mode='bkspc'):
    #     self.text = ""

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.text == "Вставте URL (ссылку) YouTube.":
                self.text = ""
            if touch.is_double_tap:
                self.text = ""


class Main(BoxLayout):

    mp3 = ObjectProperty()
    wav = ObjectProperty()
    aac = ObjectProperty()
    alac = ObjectProperty()
    m4a = ObjectProperty()
    avi = ObjectProperty()
    mpeg = ObjectProperty()
    mp4 = ObjectProperty()

    butt_save_one = ObjectProperty()
    save_playlist_button = ObjectProperty()
    next_button = ObjectProperty()
    prev_button = ObjectProperty()
    carusel = ObjectProperty()
    input_ref = ObjectProperty()
    youtube_title = ObjectProperty()
    lab_message = ObjectProperty()
    OBJ_YouTube = None
    OBJ_img_thumb = None
    tuple_checkbox_button = None
    url_index = -1
    list_all_urls_videos = [None]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if FFMPEG_LIB:
            self.lab_message.add_line(f"[color=#32CD32]     {FFMPEG_LIB}[/color]")
        else:
            self.lab_message.add_line(f"[color=#FF0000] Чудо библиотека [color=#32CD32]ffmpeg[/color] не установлена[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Программа работает в ограниченном режиме[/color]")
        self.lab_message.add_line(f"[color=#32CD32]{30*' '}Запуск программы.[/color]")


    def get_object_youtube(self,url_video):
        """При вставке ссылки на видео в Textinput- получаем
        объект YouTube и уст-ка картинки и названия видео"""
        if url_video:
            if self.get_one_video(url_video):
                pass
            elif self.get_playlist_video(url_video):
                first_video = self.list_all_urls_videos[-1] #[0]
                self.get_one_video(first_video)
            else:
                self.lab_message.add_line(f'    "{url_video}" Не является ссылкой на YouTube.')
        else:
            self.OBJ_YouTube = None
            self.list_all_urls_videos = [None]
            self.install_image_carousel_by_default()


    def get_playlist_video(self,url_video):
        try:
            self.lab_message.add_line(f"[color=#32CD32] Создаю объект Playlist YouTube.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] Создание плейлиста требует времени.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] {30*' '}Ожидайте[/color]")
            OBJ_YouTube_Playlist = Playlist(url_video, )
            self.list_all_urls_videos = list(OBJ_YouTube_Playlist.video_urls) # список URL
            count_videos_url = len(self.list_all_urls_videos)
            self.lab_message.add_line(f"[color=#32CD32] Объект Playlist YouTube создан.[/color]")
            self.lab_message.add_line(f"[color=#32CD32] Список адресов получен.[/size][/color]")
            self.lab_message.add_line(f"[color=#32CD32] Количество видео в плейлисте: [color=#DCDCDC][size=20]{count_videos_url}[/size][/color]")
            return True
        except KeyError:
            self.lab_message.add_line(f'"{url_video}" Не является ссылкой на Playlist YouTube.')
            return False
        except RegexMatchError:
            return False
        except VideoUnavailable:
            self.lab_message.add_line(f'Video [color=#FF0000]{url_video}[/color] недоступно для скачивания.')
            return False
        except Exception as err:
            self.lab_message.add_line(f'[color=#FF0000]{err}[/color] непредвиденная ошибка.')


    def get_one_video(self,url_video):
        try:
            self.OBJ_YouTube = YouTube(url_video, )
            self.lab_message.add_line(f"[color=#32CD32] Создаю объект YouTube[/color]")
            self.lab_message.add_line(f"[color=#32CD32] Объект YouTube создан.[/color]")
            self.install_data_this_video()
            return True
        except RegexMatchError:
            return False
        except VideoUnavailable:
            self.lab_message.add_line(f'    Видео {url_video} недоступно для скачивания.')
            return False

    def install_data_this_video(self,):
        self.lab_message.add_line(f"[color=#32CD32] Получаю название.[/color]")
        self.lab_message.add_line(f"[color=#32CD32] Получаю картинку.[/color]")
        try:
            self.youtube_title.text = self.OBJ_YouTube.title[:70]
            img_thumb = self.OBJ_YouTube.thumbnail_url
            img = AsyncImage(source=img_thumb, fit_mode="contain")
            self.carusel.clear_widgets()
            self.carusel.add_widget(img)
        except Exception as err:
            self.lab_message.add_line(f"[color=#FF0000] Ошибка получения заголовка[/color]")
            self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Ошибка получения картинки[/color]")
            self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
            self.lab_message.add_line(f"[color=#FF0000] Возможная причина: [color=#32CD32]Отсутствует соединение с интернетом[/color]")
            self.install_image_carousel_by_default()



    def save_one_sound_button(self):
        t_one = thr.Thread(target=self.start_save_one_track,daemon=True)
        t_one.start()
    def save_all_playlist(self):
        t_two = thr.Thread(target=self.start_save_playlist, daemon=True)
        t_two.start()


    def start_save_playlist(self):
        if self.input_ref.text:
            self.block_button()
            self.lab_message.add_line(f"[color=#DCDCDC]Чем больше количество видео, тем длительнее работа.[/color]")
            self.lab_message.add_line(f"[color=#32CD32]{30*' '}Ожидайте.[/color]")
            for url_video in self.list_all_urls_videos:
                self.OBJ_YouTube = YouTube(url_video,)
                self.start_save_one_track()
            else:
                self.block_button(block=False)
                self.lab_message.add_line(f"[color=#32CD32]{30 * ' '}Работа завершена.[/color]")

        else:
            self.lab_message.add_line(f"[color=#FF0000]{30 * ' '}Вставте ссылку.[/color]")






    def start_save_one_track(self):
        if self.input_ref.text:
            self.block_button()
            self.lab_message.add_line(f"[color=#32CD32] Соединение....Создание объекта YouTube[/color]")
            try:
                # path_load_file = self.OBJ_YouTube.streams.get_audio_only().download(DIR_DOWNLOAD, )
                path_load_file = self.OBJ_YouTube.streams.get_default_audio_track().first().download(DIR_DOWNLOAD, )
                directory = os.path.split(path_load_file)[0]
                self.lab_message.add_line(f"[color=#32CD32] Объект YouTube создан.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] Качаю.[/color]")
                self.lab_message.add_line(f"[color=#32CD32] {30 * ' '}Ждём![/color]")
                self.lab_message.add_line(f"[color=#32CD32] Сохраняю в:[/color] {directory}")

            except AttributeError:
                video_url = self.input_ref.text
                self.lab_message.add_line(f"    [color=#32CD32] Объект не создан.[/color]")
                self.lab_message.add_line(f'    "{video_url}"- [color=#FF0000]не является ссылкой YouTube.[/color]')
                self.lab_message.add_line(f'    [color=#FF0000]Сорвалась ссылка[/color]')
                self.lab_message.add_line(f'    [color=#FF0000]Перезапустите программу[/color]')
                self.block_button(block=False)
                self.install_image_carousel_by_default()
            except AgeRestrictedError:
                self.lab_message.add_line(f"    Ютубчег выставил этому видео ограничение 18+ [color=#FF0000]Скачать невозможно.[/color] ")
                self.block_button(block=False)
            except MaxRetriesExceeded:
                self.lab_message.add_line(f"[color=#FF0000] Превышено максимальное количество повторных попыток соединения[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Плохое интернет соединение.[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Ютубчег просто так не отдаст контент на халяву.[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
                self.block_button(block=False)
            except VideoUnavailable:
                self.lab_message.add_line(f"[color=#FF0000] Видео не доступно для скачивания[/color]")
                self.block_button(block=False)
            except Exception as err:
                self.lab_message.add_line(f"[color=#FF0000] {err}[/color]")
                self.lab_message.add_line(f"[color=#FF0000] Попробуйте позже.[/color]")
                self.block_button(block=False)
            else:
                self.lab_message.add_line(f"[color=#32CD32] Файл успешно скачан.[/color]")
                check_button = self.is_convert()
                self.choice_convert_for_audio(check_button,path_load_file)
        else:
            self.install_image_carousel_by_default()

    def is_a_file(self,path_file,format_file):
        new_file_path = os.path.splitext(path_file)[0] + format_file
        directory = os.path.split(path_file)[0]
        new_file = os.path.split(new_file_path)[1]
        if new_file in os.listdir(directory):
            return True

    def is_alac_file(self,path_file):
        directory, file = os.path.split(path_file)
        new_file = "_alac_" + file
        if new_file in os.listdir(directory):
            return True

    def previous_video(self):
        self.url_index += 1
        try:
            url_next_video = self.list_all_urls_videos[self.url_index]
            self.get_object_youtube(url_next_video)
        except IndexError:
            self.url_index = -1
            url_next_video = self.list_all_urls_videos[self.url_index]
            self.get_object_youtube(url_next_video)

    def next_video(self):
        self.url_index -= 1
        try:
            url_next_video = self.list_all_urls_videos[self.url_index]
            self.get_object_youtube(url_next_video)
        except IndexError:
            self.url_index = -1
            url_next_video = self.list_all_urls_videos[self.url_index]
            self.get_object_youtube(url_next_video)

# Clock.schedule_once(self.operation_complete)

    def choice_convert_for_audio(self, uid_check_button,path_file):
        match uid_check_button:
            case self.mp3.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в MP3[/color]")
                if self.is_a_file(path_file,".mp3"):
                    self.lab_message.add_line(f"[color=#32CD32] Файл уже существует.[/color]")
                    self.lab_message.add_line(f"[color=#F8F8FF]     В конвертации не нуждается [/color]")
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в MP3[/color]")
                    self.start_convert(path_file,".mp3")
                self.block_button(block=False)
            case self.wav.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в WAV[/color]")
                if self.is_a_file(path_file,".wav"):
                    self.lab_message.add_line(f"[color=#32CD32] Файл уже существует.[/color]")
                    self.lab_message.add_line(f"[color=#32CD32]     В конвертации не нуждается [/color]")
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в WAV[/color]")
                    self.start_convert(path_file,".wav")
                self.block_button(block=False)
            case self.aac.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать в AAC[/color]")
                if self.is_a_file(path_file,".aac"):
                    self.lab_message.add_line(f"[color=#32CD32] Файл уже существует.[/color]")
                    self.lab_message.add_line(f"[color=#32CD32]     В конвертации не нуждается [/color]")
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую в AAC[/color]")
                    self.start_convert(path_file,".aac")
                self.block_button(block=False)
            case self.alac.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать кодеком ALAC[/color]")
                if self.is_alac_file(path_file):
                    self.lab_message.add_line(f"[color=#32CD32] Файл уже существует.[/color]")
                    self.lab_message.add_line(f"[color=#32CD32]     В конвертации не нуждается [/color]")
                else:
                    self.lab_message.add_line(f"[color=#32CD32] Конвертирую M4A кодеком ALAC[/color]")
                    self.start_convert_alac(path_file)
                self.block_button(block=False)
            case self.m4a.uid:
                self.lab_message.add_line(f"[color=#32CD32] Узнаю надо ли конвертировать[/color]")
                if self.is_a_file(path_file,".m4a"):
                    self.lab_message.add_line(f"[color=#32CD32] Файл уже существует.[/color]")
                    self.lab_message.add_line(f"[color=#32CD32]     В конвертации не нуждается [/color]")
                self.block_button(block=False)


            # case self.avi.uid:
            #     self.start_convert(path_file,".avi")
            # case self.mpeg.uid:
            #     self.start_convert(path_file,".mpeg")
            # case self.mp4.uid:
            #     self.start_convert(path_file,".mp4")

    def start_convert_alac(self,path_file):
        directory,file = os.path.split(path_file)
        new_file = os.path.join(directory,"_alac_"+file)
        ffmpeg.input(path_file).output(new_file, codec="alac").run()
        self.lab_message.add_line("         Конвертация завершена")
        self.ids.butt_save_one.disabled = False

    def start_convert(self,path_file,format):
        if format:
            new_file = os.path.splitext(path_file)[0] + format
            ffmpeg.input(path_file).output(new_file).run()
            # self.delete_original_file(path_file)
        else:
            self.lab_message.add_line(" В конвертации не нуждается")
        self.lab_message.add_line("         Конвертация завершена")
        self.ids.butt_save_one.disabled = False

    # def delete_original_file(self,path_orig_ma4_file):
    #     if os.path.exists(path_orig_ma4_file):
    #         os.remove(path_orig_ma4_file)
    #         print("Файл удалён")
    #     else:
    #         print("Файл не найден")


    def is_convert(self):
        self.tuple_checkbox_button = (self.mp3,self.wav,self.aac,
                                      self.alac,self.m4a,self.avi,
                                      self.mpeg,self.mp4,)
        for butt in self.tuple_checkbox_button:
            if butt.state == "down":
                 return butt.uid

    def block_button(self,block=True):
        self.save_playlist_button.disabled = block
        self.next_button.disabled = block
        self.prev_button.disabled = block
        self.butt_save_one.disabled = block

    @mainthread
    def install_image_carousel_by_default(self):
        self.youtube_title.text = ""
        img = Image(source=os.path.join(current_dir,"IMG","no_image.jpg"),
                    fit_mode="fill")
        self.carusel.clear_widgets()
        self.carusel.add_widget(img)




class MyYouTubeApp(App):
    def build(self):
        return Main()

MyYouTubeApp().run()



# URL_VIDEO_RUS = "https://www.youtube.com/watch?v=hYP_1jeT4H4"
# URL_VIDEO_ENG = "https://www.youtube.com/watch?v=D4P9t9_RjUQ"
# out_path = r"F:\TEST"
#
# def main(url_video):
#     yt = YouTube(url_video,)
#     print(yt.title)
#     # Доступные потоки
#     # for audio_stream in yt.streams.filter(file_extension='mp4',abr="48kbps",):
#     #         print(audio_stream)
#
#
#     load_audio = yt.streams.get_audio_only().download(out_path,)
    # direct,_ = os.path.split(test_audio)
    # file_dir = os.path.join(direct,"test_file.mp4")



# if __name__ == '__main__':
#     main(URL_VIDEO_RUS)

# ffmpeg.input(file_path).output(os.path.join(path_files2,f'{lessen}.mp3'),codec='mp3',bitrate='64k').run()


# out_path = r"F:\TEST"
# URL = "https://www.youtube.com/watch?v=hYP_1jeT4H4"


# def convert_in_mp3(self, file_path):
#     direct, file = os.path.split(file_path)
#     self.mp3_file_dir = os.path.join(direct, f'{file}.mp3')
#     ffmpeg.input(file_path).output(self.mp3_file_dir, codec='mp3', bitrate='64k').run()
#     self.ids.info_load.text = "Загрузка окончена"
#
#
# def load_file(self):
#     self.ids.info_load.text = "Начата загрузка"
#     self.url_video = self.ids.text_inpt.text
#     try:
#         yt = YouTube(self.url_video, )
#     except Exception as err:
#         print(err)
#     else:
#         self.ids.info.text = yt.title
#         self.path_load_audio = yt.streams.get_audio_only().download(out_path, )
#         self.convert_in_mp3(self.path_load_audio)
#
#
# def on_size(self, a, b):
#     print(Window.height)
#     print(Window.width)
#
#
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


