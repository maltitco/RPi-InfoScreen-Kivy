from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.utils import Utils


class MopidyListItem(ListItemButton):
    def deselect(self, *args):
        self.is_selected = False
        self.background_color = [0, 0, 0, 0]

    def select(self, *args):
        self.is_selected = True
        self.background_color = [255, 0, 0, 0.6]


class BaseListScreen(BaseScreen):
    def __init__(self, ws,  **kwargs):
        super(BaseListScreen, self).__init__(ws, **kwargs)
        self.adapter = ListAdapter(
            data=[],
            cls=MopidyListItem,
            args_converter=self.args_converter)
        self.adapter.selection_mode = 'single'
        self.adapter.selection_limit = 1
        self.ids.list_view.adapter = self.adapter
        self.adapter.bind(on_selection_change=self.on_selection_change)

    def args_converter(self, row_index, x):
        return {'text': Utils.get_title_string(x),
                'size_hint_y': None,
                'height': 45}

    def clear_list_item_selection(self):
        if len(self.adapter.selection) > 0:
            view = self.adapter.selection[0]
            self.adapter.deselect_item_view(view)
