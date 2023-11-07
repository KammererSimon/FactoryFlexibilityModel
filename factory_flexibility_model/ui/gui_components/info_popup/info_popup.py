from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

def show_info_popup(app, text: str):
    """
    This function creates an overlay popup that displays the user a handed over text message.
    The user can only confirm by clicking OK, which closes the popup.

    :param app: ffm.gui - object
    :param text: [String] A text, that is being displayed to the user.
    :return: None
    """
    # create popup
    btn_ok = MDRaisedButton(text="OK")
    app.popup = MDDialog(title="Warning", buttons=[btn_ok], text=text)
    btn_ok.bind(on_release=app.popup.dismiss)
    app.popup.open()
