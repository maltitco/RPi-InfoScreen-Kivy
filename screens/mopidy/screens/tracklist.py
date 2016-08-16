from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.utils import Utils


class TracklistScreen(BaseListScreen):

    def __init__(self, ws,  **kwargs):
        super(TracklistScreen, self).__init__(ws, **kwargs)
        self.current_item = 0
        for name, value in kwargs.items():
            if name == 'main_screen':
                self.main_screen = value

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
        # The change event is only triggered if items are appended,
        # inserted, removed, poped, sliced, sorted, etc., but not if the items'
        # identities remain unchanged.
        # To manually dispatch the change event:
        self.adapter.data.prop.dispatch(self.adapter.data.obj())

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

    def next_item(self):
        if len(self.adapter.data) == self.current_item:
            self.current_item = 0
        else:
            self.current_item = min(
                self.current_item + 1, len(self.adapter.data) - 1)
            view = self.ids.list_view.adapter.get_view(
                self.current_item)
            view.select()
            Utils.speak_text(Utils.convert_text(view.text))
            self.select_current_item()

    def prev_item(self):
        if self.current_item == 0:
            self.current_item = len(self.adapter.data)
        else:
            self.current_item = max(0, self.current_item - 1)
            view = self.ids.list_view.adapter.get_view(
                self.current_item)
            view.select()
            Utils.speak_text(Utils.convert_text(view.text))
            self.select_current_item()

    def change_selection(self):
        item = self.ids.list_view.adapter.get_view(self.current_item)
        item.trigger_action(duration=0)

    def track_playback_started(self, tl_track):
        self.current_item = 0
        self.main_screen.go_to_screen('Odtwarzacz')
        # while not found and item_index < len(self.adapter.data):
        #    if tl_track['tlid'] == self.adapter.data[item_index]['tlid']:
        #        found = True
        # if found:
        # True ez abisatzeko
        # view = self.adapter.get_view(item_index)
        # self.adapter.handle_selection(item, True)
        # self.adapter.handle_selection(view)
