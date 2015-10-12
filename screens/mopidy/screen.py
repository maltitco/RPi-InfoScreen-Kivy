from functools import partial
import json
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
import mopidy
import os
from threading import Thread
import sys
from ws4py.client.threadedclient import WebSocketClient
from screens.mopidy.screens.now_playing_screen import NowPlayingMainScreen
from screens.mopidy.screens.search_screen import SearchScreen
from screens.mopidy.screens.tracklist import TracklistScreen
from screens.mopidy.utils import Utils
from mopidy.audio import PlaybackState

sys.path.append(os.path.dirname(os.path.abspath(__file__)))



class MopidyWebSocketClient(WebSocketClient):



    def opened(self):
        Clock.schedule_once(self.main_listener.on_connected, -1)

    def closed(self, code, reason=None):
        Clock.schedule_once(self.main_listener.on_disconnected, -1)
        print "Closed down", code, reason

    def received_message(self, m):
        message = json.loads(str(m))
        print message
        if 'event' in message:
            self.handle_event(message)
        else:
            if 'id' in message:
                self.handle_id(message)
        if len(m) == 175:
            self.close(reason='Bye bye')

    def handle_event(self, message):
        if message['event'] == "track_playback_started":
            Clock.schedule_once(partial(self.listener.track_playback_started, message['tl_track']), 0.2)
        elif message['event'] == "track_playback_paused":
            Clock.schedule_once(partial(self.listener.track_playback_paused, message['tl_track'], message['time_position']), 0.2)
        elif message['event'] == "track_playback_resumed":
            Clock.schedule_once(partial(self.listener.track_playback_resumed, message['tl_track'], message['time_position']), 0.2)
        elif message['event'] == "track_playback_ended":
            Clock.schedule_once(partial(self.listener.track_playback_ended, message['tl_track'], message['time_position']), -1)
        elif message['event'] == "seeked":
            Clock.schedule_once(partial(self.listener.seeked, message['time_position']), -1)
        elif message['event'] == "tracklist_changed":
            self.send(Utils.get_message(Utils.id_tracklist_loaded, 'core.tracklist.get_tl_tracks'))

    def handle_id(self, message):
        if message['id'] == Utils.id_cover_loaded:
            Clock.schedule_once(partial(self.listener.on_cover_loaded, message['result']), -1)
        elif message['id'] == Utils.id_tracklist_loaded:
            Clock.schedule_once(partial(self.listener.tracklist_changed, message['result']), -1)
        elif message['id'] == Utils.id_current_track_loaded:
            self.listener.current_tl_track = message['result']
            Clock.schedule_once(partial(self.listener.track_playback_started, message['result']), -1)
            self.send(Utils.get_message(Utils.id_current_time_position_loaded, 'core.playback.get_time_position'))
        elif message['id'] == Utils.id_current_time_position_loaded:
            Clock.schedule_once(partial(self.listener.seeked, message['result']), -1)
            self.time_position = message['result']
            self.send(Utils.get_message(Utils.id_current_status_loaded, 'core.playback.get_state'))
        elif message['id'] == Utils.id_current_status_loaded:
            print message['result']
            if message['result'] == PlaybackState.PAUSED:
                print "paudes"
                Clock.schedule_once(partial(self.listener.track_playback_paused, self.listener.current_tl_track, self.time_position), 0.2)
            elif message['result'] == PlaybackState.STOPPED:
                Clock.schedule_once(partial(self.listener.track_playback_ended, self.listener.current_tl_track, self.time_position), 0.2)
            else:
                print "play"
                Clock.schedule_once(partial(self.listener.track_playback_resumed, self.listener.current_tl_track, self.time_position), 0.2)

        elif message['id'] == Utils.id_search_result:
            Clock.schedule_once(partial(self.listener.result_loaded, message['result'], message['id']), -1)

class MopidyConnectedScreen(Widget):

    def __init__(self, ws, **kwargs):
        super(MopidyConnectedScreen, self).__init__(**kwargs)
        self.ws = ws
        self.current_tl_track = None
        self.ids.previous_screen.on_touch_up = self.previous_screen
        self.ids.next_screen.on_touch_up = self.next_screen
        self.ids.screen_manager.add_widget(NowPlayingMainScreen(self.ws, name="Now Playing"))
        self.ids.screen_manager.add_widget(TracklistScreen(self.ws, name="Tracklist"))
        self.ids.screen_manager.add_widget(SearchScreen(self.ws, name="Search"))
        self.change_screen(1)

    def start_data(self):
        self.ws.send(Utils.get_message(Utils.id_tracklist_loaded, 'core.tracklist.get_tl_tracks'))
        self.ws.send(Utils.get_message(Utils.id_current_track_loaded, 'core.playback.get_current_tl_track'))

    def previous_screen(self, event):
        if self.ids.previous_screen.collide_point(*event.pos):
            self.change_screen(-1)

    def next_screen(self, event):
        if self.ids.next_screen.collide_point(*event.pos):
            self.change_screen(1)

    def change_screen(self, direction):
        if direction == -1:
            self.ids.screen_manager.transition.direction = 'right'
            name = self.ids.screen_manager.previous()
        else:
            self.ids.screen_manager.transition.direction = 'left'
            name = self.ids.screen_manager.next()
        self.ids.screen_manager.current = name
        self.ids.current_screen.text = "[b][color=ff3333]" + name + "[/color][/b]"
        self.ids.previous_screen.text = self.ids.screen_manager.previous()
        self.ids.next_screen.text = self.ids.screen_manager.next()

    def load_cover(self, tl_track):
        if tl_track is not None:
            params = {'uris': [tl_track['track']['uri']]}
            self.ws.send(Utils.get_message(Utils.id_cover_loaded, 'core.library.get_images', params))

    def on_cover_loaded(self, result, td):
        try:
            if self.current_tl_track['track']['uri'] in result:
                image = result[self.current_tl_track['track']['uri']][0]['uri']
                self.ids.image_background.source = image
                for screen in self.ids.screen_manager.screens:
                    screen.cover_loaded(image)
        except Exception:
            print "Cover not found"

    def stream_title_changed(self, title, td):
        for screen in self.ids.screen_manager.screens:
            screen.stream_title_changed(title)

    def tracklist_changed(self, tracklist, td):
        for screen in self.ids.screen_manager.screens:
            screen.tracklist_changed(tracklist)

    def track_playback_started(self, tl_track, td):
        self.current_tl_track = tl_track
        self.load_cover(tl_track)
        for screen in self.ids.screen_manager.screens:
            screen.track_playback_started(tl_track)

    def track_playback_resumed(self, tl_track, time_position, td):
        for screen in self.ids.screen_manager.screens:
            screen.track_playback_resumed(tl_track, time_position)

    def track_playback_paused(self, tl_track, time_position, td):
        for screen in self.ids.screen_manager.screens:
            screen.track_playback_paused(tl_track, time_position)

    def track_playback_ended(self, tl_track, time_position, td):
        self.current_tl_track = None
        for screen in self.ids.screen_manager.screens:
            screen.track_playback_ended(tl_track, time_position)

    def seeked(self, time_position, td):
        for screen in self.ids.screen_manager.screens:
            screen.seeked(time_position)

    def result_loaded(self, result, id, td):
        for screen in self.ids.screen_manager.screens:
            screen.result_loaded(result, id)

class NotConnectedScreen(Label):

     def __init__(self, ip, port, main, **kwargs):
        super(NotConnectedScreen, self).__init__(**kwargs)
        self.text = "Could not connect to mopidy.\nCurrent config:\nIP: "+ip+"\nPort: "+str(port)
        self.main = main

     def on_touch_up(self, touch):
         self.main.connect()


class MopidyScreen(Screen):

    def __init__(self, **kwargs):
        super(MopidyScreen, self).__init__(**kwargs)
        self.ip = kwargs["params"]["ip"]
        self.port = kwargs["params"]["port"]
        self.ws_url = 'ws://'+self.ip+':'+str(self.port)+'/mopidy/ws'
        self.not_connected_widget = NotConnectedScreen(self.ip, self.port, self)
        self.on_disconnected(0)
        self.connect()

    def connect(self):
        t = Thread(target=self.start_websocket)
        t.start()

    def start_websocket(self):
        self.ws = MopidyWebSocketClient(self.ws_url, protocols=['http-only'])
        self.ws.main_listener = self
        self.ws.connect()
        self.ws.run_forever()

    def on_connected(self, dt):
        self.clear_widgets()
        self.connected_widget = MopidyConnectedScreen(self.ws)
        self.ws.listener = self.connected_widget
        self.add_widget(self.connected_widget)
        self.connected_widget.start_data()

    def on_disconnected(self, dt):
        self.clear_widgets()
        self.add_widget(self.not_connected_widget)

    def on_stop(self):
        self.ws.close()




