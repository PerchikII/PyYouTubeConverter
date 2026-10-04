import ffmpeg
import os,sys
from datetime import datetime

###############    Exceptions   #################
from pytubefix.exceptions import VideoUnavailable
from pytubefix.exceptions import RegexMatchError
from pytubefix.exceptions import AgeRestrictedError
"""urllib.error.URLError: <urlopen error [WinError 10060] Попытка установить соединение была безуспешной, 
т.к. от другого компьютера за требуемое время не получен нужный отклик, или было разорвано уже установленное
 соединение из-за неверного отклика уже подключенного компьютера>"""
from pytubefix import YouTube,Playlist



import kivy
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from kivy.core.window import Window

"""Директория main.py"""
current_dir = os.getcwd()
if not os.path.exists(os.path.join(current_dir, "Music")):
    os.mkdir(os.path.join(current_dir, "Music"))
DIR_MUSIC = os.path.join(current_dir,"Music")
# print(DIR_MUSIC)


Builder.load_file("main_kv.kv")


class LabelMessage(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = 5
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



class MyCarousel(Carousel):
    pass

class Main(BoxLayout):
    mp3 = ObjectProperty()
    wav = ObjectProperty()
    aac = ObjectProperty()
    alac = ObjectProperty()
    m4a = ObjectProperty()
    avi = ObjectProperty()
    mpeg = ObjectProperty()
    mp4 = ObjectProperty()

    carusel = ObjectProperty()
    input_ref = ObjectProperty()
    youtube_title = ObjectProperty()
    lab_message = ObjectProperty()
    OBJ_YouTube = None
    OBJ_img_thumb = None
    tuple_checkbox_button = None
    lst_message = []
    # lab_message.text = f"[color=#32CD32]Запуск программы.[/color]"

    def save_one_sound_button(self):
        self.lab_message.add_line(f"UID:{str(self.is_convert())}")
        self.lab_message.add_line(f"[color=#32CD32]Соединение....[/color]")#32CD32
        self.lab_message.add_line(f"[color=#32CD32]Создание объекта YouTube[/color]")
        try:
            path_load_file = self.OBJ_YouTube.streams.get_audio_only().download(DIR_MUSIC, )
            directory = os.path.split(path_load_file)[0]
            self.lab_message.add_line(f"[color=#32CD32]Объект YouTube создан.[/color]")
            self.lab_message.add_line(f"[color=#32CD32]Качаю.[/color]")
            self.lab_message.add_line(f"[color=#32CD32]Сохраняю в:[/color] {directory}")
        except AttributeError:
            url_video = self.input_ref.text
            self.lab_message.add_line(f'"{url_video}"- [color=#FF0000]не является ссылкой YouTube.[/color]')
        except AgeRestrictedError:
            self.lab_message.add_line("Ютубчег выставил этому видео ограничение 18+\n[color=#FF0000]Скачать невозможно.[/color] ")
        except VideoUnavailable:
            self.lab_message.add_line("[color=#FF0000]Видео не доступно для скачивания[/color]")
        else:
            self.lab_message.add_line(f"[color=#32CD32]Файл успешно скачан.[/color]")
            self.lab_message.add_line(f"[color=#32CD32]Узнаю надо ли конвертировать[/color]")
            check_button = self.is_convert()
            print("check_button",check_button)
            self.choice_convert_for_audio(check_button,path_load_file)



    def choice_convert_for_audio(self, uid_check_button,path_file):
        match uid_check_button:
            case 158:
                self.lab_message.add_line(f"[color=#32CD32]Конвертирую в MP3[/color]")
                self.start_convert(path_file,".mp3")
            case 174:
                self.lab_message.add_line(f"[color=#32CD32]Конвертирую в WAV[/color]")
                self.start_convert(path_file,".wav")
            case 190:
                self.lab_message.add_line(f"[color=#32CD32]Конвертирую в AAC[/color]")
                self.start_convert(path_file,".aac")
            case 206:
                self.lab_message.add_line(f"[color=#32CD32]Конвертирую M4A кодеком ALAC[/color]")
                self.start_convert_alac(path_file)
            case 222:
                file = os.path.split(path_file)[-1]
                self.lab_message.add_line(f"[color=#32CD32]Файл[/color] {file} [color=#32CD32]конвертации не нуждается[/color]")
                self.start_convert(path_file,None) # ".m4a"
            # case 214:
            #     self.start_convert(path_file,".avi")
            # case 226:
            #     self.start_convert(path_file,".mpeg")
            # case 238:
            #     self.start_convert(path_file,".mp4")


# ffmpeg.input(file_path_in).output(file_path_out, codec= "alac").run()
# ffmpeg.input(file_path_in).output(file_path_out, codec= "aac").run()

    def start_convert_alac(self,path_file):
        ffmpeg.input(path_file).output(path_file+"_alac_", codec="alac").run()
        self.lab_message.add_line("Конвертация завершена")



    def start_convert(self,path_file,format):
        if format:
            new_file = os.path.splitext(path_file)[0] + format
            ffmpeg.input(path_file).output(new_file).run()
        else:
            self.lab_message.add_line("В конвертации не нуждается")
        self.lab_message.add_line("Конвертация завершена")



    def is_convert(self):
        self.tuple_checkbox_button = (self.mp3,self.wav,self.aac,
                                      self.alac,self.m4a,self.avi,
                                      self.mpeg,self.mp4,)
        for butt in self.tuple_checkbox_button:
            if butt.state == "down":
                 return butt.uid


# https://www.youtube.com/watch?v=E6WwcL8L7iQ
# https://www.youtube.com/watch?v=V1aQnkGpdAw&pp=ugUEEgJydQ%3D%3D



    def get_object_youtube(self):
        url_video = self.input_ref.text
        print("url_video",url_video)
        if self.get_one_video(url_video):
            self.install_data_one_video()

        # elif self.get_playlist_video(url_video):
        #     self.install_data_playlist_video()

    def install_data_one_video(self):
        self.lab_message.add_line(f"[color=#32CD32]Получаю название.[/color]")
        self.youtube_title.text = self.OBJ_YouTube.title
        self.lab_message.add_line(f"[color=#32CD32]Получение картинки.[/color]")
        self.OBJ_img_thumb = self.OBJ_YouTube.thumbnail_url
        img = AsyncImage(source=self.OBJ_img_thumb, fit_mode="contain")
        self.carusel.clear_widgets()
        self.carusel.add_widget(img)


    # def install_data_playlist_video(self):
    #     lst_url = self.objYouTube.video_urls  # Все ссылки в плейлисте
    #     for stream_file in lst_url:
    #         download_file(stream_file, save_path, count)



    def get_playlist_video(self,url_video):
        try:
            self.OBJ_YouTube = Playlist(url_video, )
            return True
        except RegexMatchError:
            print(f'"{url_video}" Не является ссылкой на YouTube.')
            return False
        except VideoUnavailable:
            print(f'Video {url_video} is unavaialable, skipping.')
            return False

    def get_one_video(self,url_video):
        try:
            self.lab_message.add_line(f"[color=#32CD32]Создаю объект YouTube.[/color]")
            self.OBJ_YouTube = YouTube(url_video, )
            self.lab_message.add_line(f"[color=#32CD32]Объект YouTube создан.[/color]")
            return True
        except RegexMatchError:
            self.lab_message.add_line(f'"{url_video}" Не является ссылкой на YouTube.')
            return False
        except VideoUnavailable:
            print(f'Video {url_video} is unavaialable, skipping.')
            return False


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


