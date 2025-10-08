import wx
import pyperclip
import re

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
        super().__init__(None, title="MAC Formatierer", size=(300, 250))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label="Wähle ein Format zum Kopieren:")
        vbox.Add(label, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=10)

        buttons = [
            (mac_in, mac_in),
            (mac_out[0], mac_out[0]),
            (mac_out[1], mac_out[1]),
            (mac_out[2], mac_out[2]),
            ("Exit", None)
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
    mac_in = read_clipboard()
    if not mac_in:
        app = wx.App(False)
        wx.MessageBox("Keine gültige MAC-Adresse in der Zwischenablage gefunden.", "Fehler", wx.OK | wx.ICON_ERROR)
        return

    mac_out = create_mac(mac_in)
    app = wx.App(False)
    MacFormatter(mac_in, mac_out)
    app.MainLoop()

if __name__ == "__main__":
    main()