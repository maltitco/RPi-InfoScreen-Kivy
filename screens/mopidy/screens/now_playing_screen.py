from kivy.clock import Clock
import os
from screens.mopidy.utils import Utils
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.screens.base_list_screen import BaseListScreen


class NowPlayingMainScreen(BaseListScreen):
    def __init__(self, ws,  **kwargs):
        super(NowPlayingMainScreen, self).__init__(ws, **kwargs)
        self.ids.slider.on_touch_up = self.on_slider
        self.timer = None
        self.playing = False
        self.has_duration = False
        self.ids.screen_manager.add_widget(NowPlayingScreenSong(
            ws, name="NowPlaying"))
        self.ids.play_pause_button.source = os.path.dirname(
            os.path.abspath(__file__)) + "/images/ic_play_arrow.png"
        self.ids.next_button.source = os.path.dirname(os.path.abspath(
            __file__)) + "/images/ic_skip_next.png"
        self.ids.previous_button.source = os.path.dirname(
            os.path.abspath(__file__)) + "/images/ic_skip_previous.png"
        self.ids.previous_button.on_touch_up = self.previous
        self.ids.play_pause_button.on_touch_up = self.play_pause
        self.ids.next_button.on_touch_up = self.next
        self.do_init(True)

    def stream_title_changed(self, title):
        self.ids.screen_manager.current_screen.stream_title_changed(title)

    def track_playback_started(self, tl_track):
        if tl_track is not None:
            self.set_playing(True)
            # Load the data in the next screen
            # self.ids.screen_manager.get_screen(
            #     self.ids.screen_manager.next()
            #     ).track_playback_started(tl_track)
            # self.ids.screen_manager.transition.direction = 'left'
            #
            # # Move to the next screen
            # self.ids.screen_manager.current = self.ids.screen_manager.next()

            if 'length' in tl_track['track']:
                self.has_duration = True
                duration = int(tl_track['track']['length']/1000)
            else:
                self.has_duration = False
                duration = 0
            self.ids.slider.max = duration
            self.ids.slider.value = 0
            self.ids.duration.text = Utils.format_time_to_string(duration)
            if self.timer is None and self.has_duration:
                self.timer = Clock.schedule_interval(self.update, 0.1)
        else:
            self.track_playback_ended(None, 0)

    def track_playback_resumed(self, tl_track, time_position):
        self.set_playing(True)
        self.ids.slider.value = time_position/1000
        self.ids.current_pos.text = Utils.format_time_to_string(
            time_position/1000)
        if self.timer is None and self.has_duration:
            self.timer = Clock.schedule_interval(self.update, 0.1)

    def track_playback_paused(self, tl_track, time_position):
        self.set_playing(False)
        if self.timer is not None:
            Clock.unschedule(self.timer)
        self.timer = None
        self.ids.slider.value = time_position/1000
        self.ids.current_pos.text = Utils.format_time_to_string(
            time_position/1000)

    def track_playback_ended(self, tl_track, time_position):
        self.set_playing(False)
        if self.timer is not None:
            Clock.unschedule(self.timer)
        self.timer = None
        self.ids.slider.value = 0
        self.ids.current_pos.text = Utils.format_time_to_string(0)
        self.ids.duration.text = Utils.format_time_to_string(0)

    def seeked(self, time_position):
        self.ids.slider.value = time_position/1000
        self.ids.current_pos.text = Utils.format_time_to_string(
            time_position/1000)

    def on_slider(self, event):
        if self.ids.slider.collide_point(*event.pos):
            params = {'time_position': int(self.ids.slider.value*1000)}
            self.ws.send(Utils.get_message(0, 'core.playback.seek', params))

    def next(self, event):
        if self.ids.next_button.collide_point(*event.pos):
            self.ws.send(Utils.get_message(0, 'core.playback.next'))

    def previous(self, event):
        if self.ids.previous_button.collide_point(*event.pos):
            self.ws.send(Utils.get_message(0, 'core.playback.previous'))

    def play_pause(self, event):
        if self.ids.play_pause_button.collide_point(*event.pos):
            if self.playing:
                self.ws.send(Utils.get_message(0, 'core.playback.pause'))
            else:
                self.ws.send(Utils.get_message(0, 'core.playback.play'))

    def update(self, dt):
        self.ids.slider.value += 0.1
        self.ids.current_pos.text = Utils.format_time_to_string(
            int(self.ids.slider.value))

    def cover_loaded(self, cover):
        self.ids.screen_manager.current_screen.cover_loaded(cover)

    def set_playing(self, playing):
        self.playing = playing
        if self.playing:
            self.ids.play_pause_button.source = os.path.dirname(
                os.path.abspath(__file__)) + "/images/ic_pause.png"
        else:
            self.ids.play_pause_button.source = os.path.dirname(
                os.path.abspath(__file__)) + "/images/ic_play_arrow.png"

    # List
    def do_init(self, full=False):
        self.current_item = 0
        self.clear_list_item_selection()
        # view = self.adapter.get_view(self.current_item)
        # if view is not None:
        #     self.adapter.select_item_view(view)

    def change_selection(self):
        self.on_selection_change(self.ids.list_view.adapter)

    def on_selection_change(self, adapter):
        if len(adapter.selection) > 0:
            data = adapter.data[adapter.selection[0].index]
            tlid = data['tlid']
            self.ws.send(Utils.get_message(
                0, 'core.playback.play', {'tlid': tlid}))
            name = data['track']['name']
            Utils.speak('PLAY_URI', val=name)

    def tracklist_changed(self, tracklist):
        self.adapter.data = tracklist
        self.do_init(False)

    def next_item(self):
        self.clear_list_item_selection()
        if len(self.adapter.data) == self.current_item + 1:
            self.current_item = 0
        else:
            self.current_item = self.current_item + 1
        view = self.adapter.get_view(self.current_item)
        if view is not None:
            self.adapter.select_item_view(view)
            Utils.speak_text(Utils.convert_text(view.text))
            # scrolling
            selected_index = self.adapter.selection[0].index
            if selected_index > 4:
                self.ids.list_view.scroll_to(selected_index - 4)
            else:
                self.ids.list_view.scroll_to(0)

    def prev_item(self):
        self.clear_list_item_selection()
        if self.current_item == 0:
            self.current_item = len(self.adapter.data) - 1
        else:
            self.current_item = self.current_item - 1
        view = self.adapter.get_view(self.current_item)
        if view is not None:
            self.adapter.select_item_view(view)
            Utils.speak_text(Utils.convert_text(view.text))
            # scrolling
            selected_index = self.adapter.selection[0].index
            if selected_index > 4:
                self.ids.list_view.scroll_to(selected_index - 4)
            else:
                self.ids.list_view.scroll_to(0)


class NowPlayingScreenSong(BaseScreen):
    def __init__(self, ws,  **kwargs):
        super(NowPlayingScreenSong, self).__init__(ws, **kwargs)

    def track_playback_started(self, tl_track):
        try:
            self.ids.title.text = Utils.get_title_string(tl_track)
            self.ids.album.text = Utils.get_album_string(tl_track)
            self.ids.artist.text = Utils.get_artist_string(tl_track)
        except Exception as e:
            print(str(e))

    def cover_loaded(self, cover):
        self.ids.image.source = cover

    def stream_title_changed(self, title):
        self.ids.title.text = title
