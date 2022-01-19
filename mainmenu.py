# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import gi, fileframework, os, stat, conf

import dropdown

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from gi.repository.GdkPixbuf import Pixbuf


class MainMenu(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.parent = parent
        new_open_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label("V-Notes!")
        new_open_buttons.pack_start(label, True, True, 5)

        button = Gtk.Button()
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="tab-new-symbolic"), Gtk.IconSize.BUTTON),
                              True, True, 5)
        button_box.set_center_widget(Gtk.Label("New Note"))
        button.add(button_box)
        button.connect("clicked", self.on_create_new)
        new_open_buttons.pack_start(button, True, True, 5)

        button = Gtk.Button()
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(
            Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="document-open-symbolic"), Gtk.IconSize.BUTTON), True, True, 5)
        button_box.set_center_widget(Gtk.Label("Open Note"))
        button.add(button_box)
        button.connect("clicked", self.on_open_note)
        new_open_buttons.pack_start(button, True, True, 5)

        # initialize and add NoteBrowser to the main menu
        # self.pack_start(dropdown.NoteBrowser(self.parent), True, True, 5)

        new_open_buttons.set_valign(Gtk.Align.CENTER)
        new_open_buttons.set_halign(Gtk.Align.CENTER)
        self.pack_start(new_open_buttons, True, True, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def on_create_new(self, *args, **kwargs):
        self.parent.create_tab()

    def on_open_note(self, filename, *args, **kwargs):
        if type(filename) is Gtk.Button:
            filename = filename.get_children()[0].get_center_widget().get_text()
            if filename == "Open Note":
                filename = None

        text, filename = fileframework.openfile(filename, folder=self.parent.conf.get_default_folder())

        if filename is None:
            return False
        self.parent.create_tab(text=text, filename=filename)
