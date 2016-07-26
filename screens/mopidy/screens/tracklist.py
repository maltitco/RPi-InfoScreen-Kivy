from kivy.adapters.listadapter import ListAdapter
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.listview import ListItemLabel
from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.utils import Utils



class TracklistScreen(BaseListScreen):

    def tracklist_changed(self, tracklist):
        self.adapter.data = tracklist

    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            self.ws.send(Utils.get_message(0, 'core.playback.play', {'tlid': self.adapter.data[self.adapter.selection[0].index]['tlid']}))
        pass

    def track_playback_started(self, tl_track):
        item_index = 0
        found = False
        #while not found and item_index < len(self.adapter.data):
        #    if tl_track['tlid'] == self.adapter.data[item_index]['tlid']:
        #        found = True
        #if found:
            # True ez abisatzeko
            #view = self.adapter.get_view(item_index)
            #self.adapter.handle_selection(item, True)
            #self.adapter.handle_selection(view)

