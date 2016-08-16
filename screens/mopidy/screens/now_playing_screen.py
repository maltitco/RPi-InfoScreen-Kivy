from kivy.clock import Clock
import os
from screens.mopidy.utils import Utils
from screens.mopidy.screens.base_screen import BaseScreen
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.listview import ListItemLabel


class NowPlayingMainScreen(BaseScreen):

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

        self.adapter = ListAdapter(
            data=[], cls=MopidyListItem, args_converter=self.args_converter)
        self.adapter.selection_mode = 'single'
        self.ids.list_view.adapter = self.adapter
        self.adapter.bind(on_selection_change=self.on_selection_change)
        self.current_item = 0

    def stream_title_changed(self, title):
        self.ids.screen_manager.current_screen.stream_title_changed(title)

    def track_playback_started(self, tl_track):
        if tl_track is not None:
            self.set_playing(True)
            # Load the data in the next screen
            self.ids.screen_manager.get_screen(
                self.ids.screen_manager.next()
                ).track_playback_started(tl_track)
            self.ids.screen_manager.transition.direction = 'left'

            # Move to the next screen
            self.ids.screen_manager.current = self.ids.screen_manager.next()

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
    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            data = self.adapter.data[self.adapter.selection[0].index]
            tlid = data['tlid']
            self.ws.send(Utils.get_message(
                0, 'core.playback.play', {'tlid': tlid}))
            name = data['track']['name']
            name = name.replace("-> ", "")
            name = name.replace(" <-", "")
            Utils.speak('PLAY_URI', val=name)
        pass

    def tracklist_changed(self, tracklist):
        self.adapter.data = tracklist
        self.select_current_item()

    def select_current_item(self):
        i = 0
        data = []
        for item in self.adapter.data:
            try:
                tn = item['track']['name']
                tn = tn.replace("-> ", "")
                tn = tn.replace(" <-", "")
                item['track']['name'] = tn
                if i == self.current_item:
                    item['track']['name'] = "-> " + tn + " <-"
            except Exception:
                pass
            i += 1
            data.append(item)
        self.adapter.data = data
        self.adapter.data.prop.dispatch(self.adapter.data.obj())

    def next_item(self):
        self.current_item = min(
            self.current_item + 1, len(self.adapter.data) - 1)
        view = self.ids.list_view.adapter.get_view(
            self.current_item)
        view.select()
        Utils.speak_text(Utils.convert_text(view.text))
        self.select_current_item()

    def prev_item(self):
        self.current_item = max(0, self.current_item - 1)
        view = self.ids.list_view.adapter.get_view(
            self.current_item)
        view.select()
        Utils.speak_text(Utils.convert_text(view.text))
        self.select_current_item()

    def change_selection(self):
        item = self.ids.list_view.adapter.get_view(self.current_item)
        item.trigger_action(duration=0)

    def args_converter(self, row_index, x):
        return {'text': Utils.get_title_string(x),
                'size_hint_y': None,
                'height': 45}


class NowPlayingScreenSong(BaseScreen):

    def __init__(self, ws,  **kwargs):
        super(NowPlayingScreenSong, self).__init__(ws, **kwargs)

    def track_playback_started(self, tl_track):
        self.ids.title.text = Utils.get_title_string(tl_track)
        self.ids.album.text = Utils.get_album_string(tl_track)
        self.ids.artist.text = Utils.get_artist_string(tl_track)

    def cover_loaded(self, cover):
        self.ids.image.source = cover

    def stream_title_changed(self, title):
        self.ids.title.text = title


class MopidyListItem(ButtonBehavior, ListItemLabel):
    def deselect(self, *args):
        self.is_selected = False

    def select(self, *args):
        self.is_selected = True
