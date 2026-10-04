import ffmpeg
import os,sys


###############    Exceptions   #################
from pytubefix.exceptions import VideoUnavailable
from pytubefix.exceptions import RegexMatchError
# pytubefix.exceptions.AgeRestrictedError
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




Builder.load_file("00_ParsingYouTube.kv")


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
    OBJ_YouTube = None
    OBJ_img_thumb = None
    tuple_checkbox_button = None


    def save_one_sound_button(self):
        print("UID: ",self.is_convert())

        try:
            path_load_file = self.OBJ_YouTube.streams.get_audio_only().download(DIR_MUSIC, )
            print(path_load_file)
        except AttributeError:
            url_video = self.input_ref.text
            print(f'"{url_video}" Не является ссылкой на YouTube.')
        else:
            check_button = self.is_convert()
            self.choice_convert_for_audio(check_button,path_load_file)



    def choice_convert_for_audio(self, uid_check_button,path_file):
        match uid_check_button:
            case 154:
                self.start_convert(path_file,".mp3")
            case 170:
                self.start_convert(path_file,".wav")
            case 186:
                self.start_convert(path_file,".aac")
            case 202:
                self.start_convert_alac(path_file)
            case 218:
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
        print("Conversion completed")


    def start_convert(self,path_file,format):
        if format:
            new_file = os.path.splitext(path_file)[0] + format
            ffmpeg.input(path_file).output(new_file).run()
        else:
            print("В конвертации не нуждается")
        print("Conversion completed")


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
        self.youtube_title.text = self.OBJ_YouTube.title
        print(self.OBJ_YouTube.title)
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
            self.OBJ_YouTube = YouTube(url_video, )
            return True
        except RegexMatchError:
            print(f'"{url_video}" Не является ссылкой на YouTube.')
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


