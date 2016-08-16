from kivy.uix.screenmanager import Screen

__author__ = 'araczkowski'


class BaseScreen(Screen):

    def __init__(self, ws,  **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.ws = ws

    def tracklist_changed(self, tracklist):
        pass

    def track_playback_started(self, tl_track):
        pass

    def track_playback_resumed(self, tl_track, time_position):
        pass

    def track_playback_paused(self, tl_track, time_position):
        pass

    def track_playback_ended(self, tl_track, time_position):
        pass

    def stream_title_changed(self, title):
        pass

    def seeked(self, time_position):
        pass

    def cover_loaded(self, cover):
        pass

    def result_loaded(self, result, id):
        pass

    def playlists_loaded(self, result):
        pass
