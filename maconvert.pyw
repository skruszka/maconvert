import wx
import pyperclip
import re
import gettext
import locale
import os

def setup_translation():
    locale.setlocale(locale.LC_ALL, '')
    
    lang_tuple = locale.getlocale()
    language_code = lang_tuple[0].split('_')[0] if lang_tuple and lang_tuple[0] else 'en'

    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')

    try:
        translation = gettext.translation('messages', locales_dir, languages=[language_code])
        translation.install()
        _ = translation.gettext
    except FileNotFoundError:
        translation = gettext.translation('messages', locales_dir, languages=['en'])
        translation.install()
        _ = translation.gettext

    return _
def read_clipboard():
    clipboard_in = pyperclip.paste().strip()
    mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})$|^([0-9a-fA-F]{12})$"
    if re.match(mac_regex, clipboard_in):
        mac_in = re.sub(r"[.:-]", "", clipboard_in)
        return mac_in.lower()
    return None

def create_mac(mac_in):
    mac_posix = ":".join(mac_in[i:i+2] for i in range(0, 12, 2))
    mac_nt = "-".join(mac_in[i:i+2] for i in range(0, 12, 2)).upper()
    mac_cisco = ".".join([mac_in[0:4], mac_in[4:8], mac_in[8:12]])
    return [mac_posix, mac_nt, mac_cisco]

class MacFormatter(wx.Frame):
    def __init__(self, mac_in, mac_out):
        super().__init__(None, title=_("msgid_title"), size=(400, 250))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label=_("msgid_format"))
        vbox.Add(label, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=10)

        buttons = [
            (mac_in, mac_in),
            (mac_out[0], mac_out[0]),
            (mac_out[1], mac_out[1]),
            (mac_out[2], mac_out[2]),
            (_("msgid_exit"), None)
        ]

        for label, value in buttons:
            btn = wx.Button(panel, label=label)
            vbox.Add(btn, flag=wx.ALL | wx.EXPAND, border=5)
            if value:
                btn.Bind(wx.EVT_BUTTON, lambda evt, val=value: self.copy_and_exit(val))
            else:
                btn.Bind(wx.EVT_BUTTON, lambda evt: self.Close())

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def copy_and_exit(self, value):
        pyperclip.copy(value)
        self.Close()

def main():
    _ = setup_translation()

    mac_in = read_clipboard()
    if not mac_in:
        app = wx.App(False)
        wx.MessageBox(_("msgid_notvalid"), _("msgid_error"), wx.OK | wx.ICON_ERROR)
        return

    mac_out = create_mac(mac_in)
    app = wx.App(False)
    MacFormatter(mac_in, mac_out)
    app.MainLoop()

if __name__ == "__main__":
    main()