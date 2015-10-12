
from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.utils import Utils


class SearchScreen(BaseListScreen):

    def __init__(self, ws,  **kwargs):
        super(SearchScreen, self).__init__(ws, **kwargs)
        self.ids.search_input.bind(on_text_validate=self.on_search)

    def on_search(self, input):
        self.ws.send(Utils.get_message(Utils.id_search_result, "core.library.search", {'track': [input.text]}))

    def result_loaded(self, result, id):
        if id == Utils.id_search_result:
            #self.adapter.data = result[0]
            print result
