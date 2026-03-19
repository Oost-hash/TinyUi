from .components.tabs.tab_component import TabComponent
from .components.tabs.tab_model import TabSpec
from .components.tabs.tab_viewmodel import TabViewModel
from .frameless_window import FramelessWindow
from .tabs.home_tab.home_tab_view import HomeTabView
from .tabs.home_tab.home_tab_viewmodel import HomeTabViewModel
from .tabs.settings_tab.settings_tab_view import SettingsTabView
from .tabs.settings_tab.settings_tab_viewmodel import SettingsTabViewModel


class MainWindow(FramelessWindow):
    def __init__(self, state):
        super().__init__(title="App", minimizable=True)

        tab_vm = TabViewModel(app_state=state)
        tab_vm.register(TabSpec(
            id="home",
            name="Home",
            view_class=HomeTabView,
            viewmodel_class=HomeTabViewModel,
            order=0,
        ))
        tab_vm.register(TabSpec(
            id="settings",
            name="Settings",
            view_class=SettingsTabView,
            viewmodel_class=SettingsTabViewModel,
            order=1,
        ))
        tab_vm.build()

        # TabViewModel → AppState (mirror)
        tab_vm.tab_activated.connect(
            lambda new_id, _: state.set_active_tab(new_id)
        )
        tab_vm.tab_activated.connect(
            lambda new_id, _: state.set_title(
                tab_vm.model.get_spec(new_id).name
            )
        )

        # AppState title → TitleBar
        state.titleChanged.connect(lambda: self.title_bar.set_title(state.title))

        self.set_content(TabComponent(tab_vm))
