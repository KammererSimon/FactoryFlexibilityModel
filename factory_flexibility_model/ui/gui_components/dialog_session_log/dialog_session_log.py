# IMPORTS
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconLeftWidget, TwoLineIconListItem

from factory_flexibility_model.ui.utility.window_handling import close_dialog


# CLASSES
class DialogSessionLog(BoxLayout):
    pass


# FUNCTIONS
def show_session_log_dialog(app):
    """
    This function opens the dialog showing the log of the current session

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # create buttons for the dialog
    btn_close = MDFlatButton(text="Close")

    app.dialog = MDDialog(
        title=f"Session Log",
        buttons=[btn_close],
        type="custom",
        content_cls=DialogSessionLog(),
        auto_dismiss=False,
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(1000)
    app.dialog.height = dp(800)

    for event in app.session_data["log"]:
        # determine color for the event icon
        if event["type"] == "DEBUG":
            color = [0.5, 0.5, 0.5, 1]  # grey
        elif event["type"] == "INFO":
            color = [0.1, 0.8, 0.1, 1]  # green
        elif event["type"] == "ERROR":
            color = [0.8, 0.1, 0.1, 1]  # red

        # create a list item with the message of the current event
        item = TwoLineIconListItem(
            IconLeftWidget(
                icon=event["icon"], theme_icon_color="Custom", icon_color=color
            ),
            text=f"{event['type']} [{event['time']}]",
            secondary_text=f"{event['event_info']}   {event['message']}",
        )

        # add list item to the log list
        app.dialog.content_cls.ids.list_log_events.add_widget(item)

    # bind callback to button
    btn_close.bind(on_release=lambda x: close_dialog(app))
    app.dialog.open()
