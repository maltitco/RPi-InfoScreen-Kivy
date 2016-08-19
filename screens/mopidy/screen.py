#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import partial
import json
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
import os
from threading import Thread
import sys
from ws4py.client.threadedclient import WebSocketClient

from screens.mopidy.screens.library_screen import LibraryScreen
from screens.mopidy.screens.now_playing_screen import NowPlayingMainScreen
# from screens.mopidy.screens.playlists_screen import PlayListsScreen
# from screens.mopidy.screens.search_screen import SearchScreen
# from screens.mopidy.screens.tracklist import TracklistScreen
from screens.mopidy.utils import Utils
from mopidy.audio import PlaybackState

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
url = u'rstation:/home/pi/mopidy-rstation/media'


class MopidyWebSocketClient(WebSocketClient):

    # def __init__(self, ws_url, protocols):
    #     super(MopidyWebSocketClient, self).__init__(ws_url, protocols)

    def opened(self):
        Clock.schedule_once(self.main_listener.on_connected, -1)

    def closed(self, code, reason=None):
        Clock.schedule_once(self.main_listener.on_disconnected, -1)
        print("Closed down", code, reason)

    def received_message(self, m):
        message = json.loads(str(m))
        if 'event' in message:
            self.handle_event(message)
        else:
            if 'id' in message:
                self.handle_id(message)
        if len(m) == 175:
            self.close(reason='Bye bye')

    def handle_event(self, message):
        if message['event'] == "handleRemoteCommand":
            self.handle_remote_command(message['cmd'])
        if message['event'] == "track_playback_started":
            Clock.schedule_once(
                partial(
                    self.listener.track_playback_started,
                    message['tl_track']), 0.2)
        elif message['event'] == "track_playback_paused":
            Clock.schedule_once(
                partial(
                    self.listener.track_playback_paused,
                    message['tl_track'],
                    message['time_position']), 0.2)
        elif message['event'] == "track_playback_resumed":
            Clock.schedule_once(
                partial(
                    self.listener.track_playback_resumed,
                    message['tl_track'],
                    message['time_position']), 0.2)
        elif message['event'] == "track_playback_ended":
            Clock.schedule_once(
                partial(
                    self.listener.track_playback_ended,
                    message['tl_track'],
                    message['time_position']), -1)
        elif message['event'] == "seeked":
            Clock.schedule_once(
                partial(self.listener.seeked, message['time_position']), -1)
        elif message['event'] == "tracklist_changed":
            self.send(
                Utils.get_message(
                    Utils.id_tracklist_loaded, 'core.tracklist.get_tl_tracks'))
        elif message['event'] == "volume_changed":
            vol = message['volume']
            self.listener.current_voulme = vol

    def handle_remote_command(self, cmd):
        screen = self.listener.ids.screen_manager.get_screen(
            self.listener.ids.screen_manager.current)
        if cmd == 'fl_plus':
            Utils.backlight_up()
        if cmd == 'fl_minus':
            Utils.backlight_down()
        if cmd == 'eq':
            if Utils.lang == 'pl':
                Utils.lang = 'en'
            else:
                Utils.lang = 'pl'
        if cmd == 'ch_minus':
            screen.change_selection()
        if cmd == 'ch_plus':
            self.listener.go_to_screen('Biblioteka')
            screen = self.listener.ids.screen_manager.get_screen(
                self.listener.ids.screen_manager.current)
            screen.current_item = 0
            screen.current_uri = None
            screen.current_dir = [None, url]
            self.send(Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': None}))
            Utils.speak('CHP')
        if cmd == 'ch':
            self.listener.go_to_screen('Odtwarzacz')
            Utils.speak('CH')
        if cmd == 'vol_up':
            vol = min(int(self.listener.current_voulme) + 10, 100)
            self.send(
                Utils.get_message(
                    Utils.id_volume, 'core.mixer.set_volume', {'volume': vol}))
            Utils.speak('VOL', val=vol)
        if cmd == 'vol_down':
            vol = max(int(self.listener.current_voulme) - 10, 0)
            self.send(Utils.get_message(
                Utils.id_volume, 'core.mixer.set_volume', {'volume': vol}))
            Utils.speak('VOL', val=vol)
        if cmd == 'num8':
            Utils.speak('RADIO_DIR')
            self.listener.go_to_screen('Biblioteka')
            uri = url + '/Radia'
            screen = self.listener.ids.screen_manager.get_screen('Biblioteka')
            screen.current_uri = uri
            screen.current_item = 0
            screen.current_dir = [None, url, uri]
            self.send(Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

        if cmd == 'num7':
            Utils.speak('AUDIOBOOKS_DIR')
            self.listener.go_to_screen('Biblioteka')
            uri = url + '/Audiobuki'
            screen = self.listener.ids.screen_manager.get_screen('Biblioteka')
            screen.current_uri = uri
            screen.current_item = 0
            screen.current_dir = [None, url, uri]
            self.send(Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

        if cmd == 'num9':
            Utils.speak('MUSIC_DIR')
            self.listener.go_to_screen('Biblioteka')
            screen = self.listener.ids.screen_manager.get_screen('Biblioteka')
            uri = url + '/Muzyka'
            screen.current_uri = uri
            screen.current_item = 0
            screen.current_dir = [None, url, uri]
            self.send(Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

        if cmd == 'play_pause':
            screen = self.listener.ids.screen_manager.get_screen('Odtwarzacz')
            if screen.playing:
                Utils.speak('PAUSE')
                self.send(Utils.get_message(0, 'core.playback.pause'))
            else:
                Utils.speak('PLAY')
                self.send(Utils.get_message(0, 'core.playback.play'))
        if cmd == 'next':
            screen.next_item()
            # if screen.name == 'Odtwarzacz':
            #     Utils.speak('NEXT')
            #     self.send(Utils.get_message(0, 'core.playback.next'))

        if cmd == 'prev':
            screen.prev_item()
            # if screen.name == 'Odtwarzacz':
            #     Utils.speak('PREV')
            #     self.send(Utils.get_message(0, 'core.playback.previous'))

    def handle_id(self, message):
        try:
            if message['id'] == Utils.id_cover_loaded:
                Clock.schedule_once(
                    partial(
                        self.listener.on_cover_loaded, message['result']), -1)
            elif message['id'] == Utils.id_tracklist_loaded:
                Clock.schedule_once(
                    partial(
                        self.listener.tracklist_changed,
                        message['result']), -1)
            elif message['id'] == Utils.id_current_track_loaded:
                self.listener.current_tl_track = message['result']
                Clock.schedule_once(
                    partial(
                        self.listener.track_playback_started,
                        message['result']), -1)
                self.send(
                    Utils.get_message(
                        Utils.id_current_time_position_loaded,
                        'core.playback.get_time_position'))
            elif message['id'] == Utils.id_current_time_position_loaded:
                Clock.schedule_once(
                    partial(self.listener.seeked, message['result']), -1)
                self.time_position = message['result']
                self.send(
                    Utils.get_message(
                        Utils.id_current_status_loaded,
                        'core.playback.get_state'))
            elif message['id'] == Utils.id_current_status_loaded:
                if message['result'] == PlaybackState.PAUSED:
                    Clock.schedule_once(
                        partial(
                            self.listener.track_playback_paused,
                            self.listener.current_tl_track,
                            self.time_position), 0.2)
                elif message['result'] == PlaybackState.STOPPED:
                    Clock.schedule_once(
                        partial(
                            self.listener.track_playback_ended,
                            self.listener.current_tl_track,
                            self.time_position), 0.2)
                else:
                    Clock.schedule_once(
                        partial(
                            self.listener.track_playback_resumed,
                            self.listener.current_tl_track,
                            self.time_position), 0.2)

            elif message['id'] == Utils.id_search_result or \
                    message['id'] == Utils.id_browse_loaded:
                Clock.schedule_once(
                    partial(
                        self.listener.result_loaded,
                        message['result'], message['id']), -1)
            elif message['id'] == Utils.id_playlists_loaded:
                Clock.schedule_once(
                    partial(
                        self.listener.playlists_loaded, message['result']), -1)
        except Exception as e:
            print(str(e))


class MopidyConnectedScreen(Widget):

    def __init__(self, ws, **kwargs):
        super(MopidyConnectedScreen, self).__init__(**kwargs)
        self.ws = ws
        self.main_screen = self
        self.current_tl_track = None
        # self.ids.previous_screen.on_touch_up = self.previous_screen
        self.ids.next_screen.on_touch_up = self.next_screen
        self.ids.screen_manager.add_widget(
            NowPlayingMainScreen(self.ws, name="Odtwarzacz"))
        # self.ids.screen_manager.add_widget(
        #     TracklistScreen(
        #         self.ws, main_screen=self.main_screen, name="Lista"))
        self.ids.screen_manager.add_widget(
            LibraryScreen(
                self.ws, main_screen=self.main_screen, name="Biblioteka"))
        # self.ids.screen_manager.add_widget(
        #     SearchScreen(self.ws, name="Search"))
        # self.ids.screen_manager.add_widget(
        #     PlayListsScreen(self.ws, name="Playlists"))

        self.current_screen_x = self.ids.current_screen.x
        # self.previous_screen_x = self.ids.previous_screen.x
        self.next_screen_x = self.ids.next_screen.text
        self.current_voulme = 50

        self.ids.image_background.source = os.path.dirname(
            os.path.abspath(
                __file__)) + "/../mopidy/screens/images/background.png"

        # self.screen_change_direction = 0
        # self.change_screen(1)
        # self.change_screen(-1)
        self.ids.current_screen.text = \
            "[b][color=ff3333]Odtwarzacz[/color][/b]"
        # self.ids.previous_screen.text = self.ids.screen_manager.previous()
        self.ids.next_screen.text = self.ids.screen_manager.next()

    def start_data(self):
        self.ws.send(
            Utils.get_message(
                Utils.id_tracklist_loaded, 'core.tracklist.get_tl_tracks'))
        self.ws.send(
            Utils.get_message(
                Utils.id_current_track_loaded,
                'core.playback.get_current_tl_track'))
        self.ws.send(
            Utils.get_message(
                Utils.id_playlists_loaded, 'core.playlists.as_list'))
        self.ws.send(
            Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': None}))
        self.ws.send(
            Utils.get_message(
                Utils.id_volume, "core.mixer.get_volume"))

    # def previous_screen(self, event):
    #     if self.ids.previous_screen.collide_point(*event.pos):
    #         self.change_screen(-1)

    def next_screen(self, event):
        if self.ids.next_screen.collide_point(*event.pos):
            self.change_screen(1)

    def change_screen(self, direction):
        self.screen_change_direction = direction
        if direction == -1:
            self.ids.screen_manager.transition.direction = 'right'
            name = self.ids.screen_manager.previous()
        else:
            self.ids.screen_manager.transition.direction = 'left'
            name = self.ids.screen_manager.next()
        self.ids.screen_manager.current = name
        self.ids.current_screen.text = "[b][color=ff3333]" \
            + name + "[/color][/b]"
        # self.ids.previous_screen.text = self.ids.screen_manager.previous()
        self.ids.next_screen.text = self.ids.screen_manager.next()

    def go_to_screen(self, screen_name):
        self.ids.screen_manager.current = screen_name
        self.ids.current_screen.text = "[b][color=ff3333]" \
            + screen_name + "[/color][/b]"
        # self.ids.previous_screen.text = \
        #     self.ids.screen_manager.previous()
        self.ids.next_screen.text = \
            self.ids.screen_manager.next()
        screen = self.ids.screen_manager.get_screen(
            self.ids.screen_manager.current)
        screen.current_item = 0

    def load_cover(self, tl_track):
        if tl_track is not None:
            try:
                params = {'uris': [tl_track['track']['uri']]}
                self.ws.send(
                    Utils.get_message(
                        Utils.id_cover_loaded,
                        'core.library.get_images', params))
            except Exception as e:
                print(str(e))

    def on_cover_loaded(self, result, td):
        current_track = ''
        try:
            current_track = self.current_tl_track['track']['name']
        except Exception:
            pass
        if len(current_track) > 0:
            fname = url.replace('rstation:', '') + '/Ulubione/covers/' \
                + self.current_tl_track['track']['name'] \
                + '.png'
        else:
            fname = "none"
        if os.path.isfile(fname):
            self.ids.image_background.source = fname
            for screen in self.ids.screen_manager.screens:
                screen.cover_loaded(fname)
        else:
            try:
                if self.current_tl_track['track']['uri'] in result:
                    i = result[self.current_tl_track['track']['uri']][0]['uri']
                    self.ids.image_background.source = i
                    for screen in self.ids.screen_manager.screens:
                        screen.cover_loaded(i)
            except Exception:
                fname = url.replace('rstation:', '') + '/Ulubione/covers/' \
                    + 'splash.png'
                if os.path.isfile(fname):
                    self.ids.image_background.source = fname
                flogo = url.replace('rstation:', '') + '/Ulubione/covers/' \
                    + 'logo.png'
                if os.path.isfile(flogo):
                    for screen in self.ids.screen_manager.screens:
                        screen.cover_loaded(flogo)

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
        if tl_track is not None:
            try:
                Utils.speak('PLAYING', val=tl_track['track']['name'])
            except Exception as e:
                print(str(e))

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

    def playlists_loaded(self, result, td):
        for screen in self.ids.screen_manager.screens:
            screen.playlists_loaded(result)


class NotConnectedScreen(Label):

    def __init__(self, ip, port, main, **kwargs):
        super(NotConnectedScreen, self).__init__(**kwargs)
        self.text = "Łączenie z serwerem...\n---> " \
            + str(ip) + ':' + str(port) + ' <---\n'
        # 'próba połączenia ' + str(main.tries_to_connect)
        self.main = main

    def on_touch_up(self, touch):
        print('Connection on touch...')
        self.main.tries_to_connect = 0
        self.main.connect(0)


class MopidyScreen(Screen):

    def __init__(self, **kwargs):
        super(MopidyScreen, self).__init__(**kwargs)
        self.ip = kwargs["params"]["ip"]
        self.port = kwargs["params"]["port"]
        self.tries_to_connect = 0
        self.ws_url = 'ws://'+self.ip+':'+str(self.port)+'/mopidy/ws'
        self.not_connected_widget = NotConnectedScreen(
            self.ip, self.port, self)
        self.on_disconnected(0)
        self.connect(0)

    def connect(self, dt):
        # check if we already have a connection
        if self.tries_to_connect == -1:
            # return False to disable the Clock.schedule
            return False

        self.tries_to_connect += 1
        t = Thread(target=self.start_websocket)
        t.start()

    def start_websocket(self):
        try:
            self.ws = MopidyWebSocketClient(
                self.ws_url, protocols=['http-only'])
            self.ws.main_listener = self
            self.ws.connect()
            self.ws.run_forever()
        except Exception as e:
            print(str(e))
            self.on_disconnected

    def on_connected(self, dt):
        try:
            self.tries_to_connect = -1
            self.clear_widgets()
            self.connected_widget = MopidyConnectedScreen(self.ws)
            self.ws.listener = self.connected_widget
            self.add_widget(self.connected_widget)
            self.connected_widget.start_data()
        except Exception as e:
            print(str(e))
            self.on_disconnected

    def on_disconnected(self, dt):
        self.tries_to_connect = 0
        self.clear_widgets()
        self.add_widget(self.not_connected_widget)
        Clock.schedule_interval(self.connect, 25)

    def on_stop(self):
        self.ws.close()
