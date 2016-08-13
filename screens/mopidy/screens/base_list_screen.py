from kivy.adapters.listadapter import ListAdapter
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.listview import ListItemLabel
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.utils import Utils


class MopidyListItem(ButtonBehavior, ListItemLabel):

    def deselect(self, *args):
        self.is_selected = False

    def select(self, *args):
        self.is_selected = True

class BaseListScreen(BaseScreen):

    def __init__(self, ws,  **kwargs):
        super(BaseListScreen, self).__init__(ws, **kwargs)
        args_converter = lambda row_index, x: {'text': Utils.get_title_string(x), 'size_hint_y': None,
            'height': 45}
        self.adapter = ListAdapter(
            data=[], cls=MopidyListItem, args_converter=args_converter)
        self.adapter.selection_mode = 'single'
        self.ids.list_view.adapter = self.adapter
        self.adapter.bind(on_selection_change=self.on_selection_change)
