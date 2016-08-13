import os
from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.utils import Utils


class SearchScreen(BaseListScreen):

    def __init__(self, ws,  **kwargs):
        super(SearchScreen, self).__init__(ws, **kwargs)
        self.ids.search_input.bind(on_text_validate=self.on_search)
        self.ids.search_button.source = os.path.dirname(os.path.abspath(__file__)) + "/images/ic_search.png"
        self.ids.search_button.on_touch_up = self.on_search_button

    def on_search_button(self, event):
        if self.ids.search_button.collide_point(*event.pos):
            self.on_search(self.ids.search_input)

    def on_search(self, input):
        self.ws.send(Utils.get_message(Utils.id_search_result, "core.library.search", {'any': [input.text]}))

    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            data = []
            data.extend(adapter.data)
            data.insert(0, data.pop(adapter.selection[0].index))
            self.ws.send(Utils.get_message(0, "core.tracklist.clear"))
            self.ws.send(Utils.get_message(0, "core.tracklist.add", {"tracks": data}))
            self.ws.send(Utils.get_message(0, "core.playback.play"))
            self.adapter.selection = []

    def result_loaded(self, result, id):
        if id == Utils.id_search_result:
            if len(result) > 1:
                data = []
                for result_list in result:
                    if 'tracks' in result_list:
                        data.extend(result_list['tracks'])
                self.adapter.data = data
            else:
                self.adapter.data = []
