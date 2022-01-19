# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from gi.repository import Gtk, Gio
import conf


class Settings(Gtk.Box):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.set_size_request(300, 300)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        mini_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        mini_box.pack_start(Gtk.Label("Preferred folder for Notes:"), True, False, 10)

        mini_mini_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        chooserbutton = Gtk.Button(label="Change")
        chooserbutton.connect("clicked", self.on_preferred_folder_set)
        mini_mini_box.pack_end(chooserbutton, True, False, 0)

        currentfolder = parent.conf.get_default_folder()
        self.entry_folder_current = Gtk.Entry()
        self.entry_folder_current.set_text(currentfolder if currentfolder else "None")
        self.entry_folder_current.set_sensitive(False)
        self.entry_folder_current.set_width_chars(20)
        mini_mini_box.pack_end(self.entry_folder_current, True, False, 0)
        mini_box.pack_start(mini_mini_box, False, False, 0)

        box.pack_start(mini_box, False, True, 10)

        mini_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        mini_box.pack_end(self.entry_folder_current, True, False, 0)
        mini_box.pack_start(Gtk.Label("Save in real-time:"), True, False, 10)

        autosaveswitch = Gtk.Switch()
        autosaveswitch.set_active(parent.conf.get_autosave())
        autosaveswitch.connect("state_set", self.on_autosave_set)
        mini_box.pack_end(autosaveswitch, True, False, 0)

        box.pack_start(mini_box, False, True, 10)

        # self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        self.pack_start(box, True, True, 10)
        self.show_all()

    def on_preferred_folder_set(self, *args):
        dialog = Gtk.FileChooserDialog(
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK
            ),
            transient_for=self.parent
        )
        try:
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.parent.conf.set_default_folder(dialog.get_filename())
                self.entry_folder_current.set_text(dialog.get_filename())
            if response == Gtk.ResponseType.CANCEL:
                print("I: User selected cancel on setting a preferred folder.")
            else:
                pass
            dialog.destroy()
        except Exception as e:
            print("E: unable to select preferred folder,", e)
            return

    def on_autosave_set(self, switch, state):
        self.parent.conf.set_autosave(state)


class FileChooserButton(Gtk.FileChooserButton):
    def __init__(self):
        self.wild_copy = self
        self.set_current_name("lol1")
        super().__init__()
