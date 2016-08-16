from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.utils import Utils

__author__ = 'araczkowski'


class PlayListsScreen(BaseListScreen):

    def playlists_loaded(self, playlists):
        self.adapter.data = playlists

    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            self.ws.send(Utils.get_message(0, "core.tracklist.clear"))
            self.ws.send(Utils.get_message(
                0, "core.tracklist.add",
                {"uri": adapter.data[adapter.selection[0].index]['uri']}))
            self.ws.send(Utils.get_message(0, "core.playback.play"))
            self.adapter.selection = []
