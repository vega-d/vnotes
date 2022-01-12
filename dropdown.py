# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


class Popover(Gtk.Popover):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        button = Gtk.ModelButton(label="Item 1")
        vbox.pack_start(button, True, True, 10)

        button = Gtk.ModelButton(label="About")
        button.connect("clicked", parent.parent.on_about)
        vbox.pack_start(button, True, True, 10)

        vbox.show_all()
        self.add(vbox)
        self.set_position(Gtk.PositionType.BOTTOM)

