# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from copy import copy
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


def flaware_path(filename):
    try:
        import os
        if filename in os.listdir("/app/bin"):
            filename = "/app/bin/" + filename
        else:
            raise Exception
    except Exception as e:
        print("W: Hmm, it appears to be the app is running outside of Flatpak.")
        print("W: Please consider using flatpak instead.")
    return filename


def savebuffer(filename, buffer, folder=None):
    if filename[-4:] != ".txt":
        filename += ".txt"
    import os
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        dialog = Gtk.FileChooserDialog(
            title="Please choose where to save",
            action=Gtk.FileChooserAction.SAVE,
            create_folders=True,
            do_overwrite_confirmation=True
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )

        filter = Gtk.FileFilter()
        filter.add_pattern(".txt")
        filter.set_name(".txt notes")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.add_pattern(".md")
        filter.set_name(".md notes")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.add_pattern(".*")
        filter.set_name("All files")
        dialog.add_filter(filter)

        dialog.set_current_name(filename)
        if folder:
            dialog.set_current_folder(folder)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            dialog.destroy()
        else:
            dialog.destroy()
            return False

    text_to_be_saved = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

    try:
        with open(path, 'w') as output:
            output.write(text_to_be_saved)
    except Exception as e:
        print("E: Could not save note:", e)
        return False
    return True


def openfile(filename=None, open_dialog=True, folder=None):
    if filename is None and open_dialog:
        dialog = Gtk.FileChooserDialog(
            title="Please choose what note to open",
            action=Gtk.FileChooserAction.OPEN,
            create_folders=True
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        filter = Gtk.FileFilter()
        filter.add_pattern(".txt")
        filter.set_name(".txt notes")
        if folder:
            dialog.set_current_folder(folder)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            dialog.destroy()
        else:
            dialog.destroy()
            return None, None

    try:
        file_to_open = open(filename, "r")
    except Exception as e:
        file_to_open = None
        print("E: Could not open file", filename)
        if open_dialog:
            return openfile(filename=None, folder=folder)
        else:
            return None, None

    text = "".join(file_to_open.readlines())
    return text, filename


def mdformat(textbuffer, kind, iters=False):
    text = textbuffer.get_text(
        textbuffer.get_iter_at_line(0),
        textbuffer.get_iter_at_line(textbuffer.get_line_count()),
        False)

    point_functions = {"bold": get_points_bold,
                       "italic": get_points_italic,
                       "underline": get_points_underline,
                       "header1": get_points_header1}

    points = point_functions[kind](text)

    # converting to iters
    if iters:
        points = [textbuffer.get_iter_at_offset(i) for i in points]

    # transforming into pairs
    tmp = []
    for i in range(len(points)):
        if i % 2 == 1:
            tmp[-1].append(points[i])
        else:
            tmp.append([points[i]])
    point_pairs = tmp

    return point_pairs


def get_points_generic(text, key):
    key_length = len(key)
    all_points = []
    tmp = copy(text)
    while tmp.find(key) > -1:
        point = tmp.find(key)
        if point > -1:
            tmp = tmp[(point + key_length):]
            if all_points:
                point += all_points[-1]
                if len(all_points) % 2:
                    point += (key_length * 2)
                else:
                    point += key_length
            all_points.append(point)
    if len(all_points) % 2 != 0:
        all_points.pop(-1)
    return all_points


def get_points_bold(text):
    return get_points_generic(text, "**")


def get_points_italic(text):
    text = text.replace("__", "xx")
    return get_points_generic(text, "_")


def get_points_underline(text):
    return get_points_generic(text, "__")


def get_points_header1(text):
    # print([text])
    return []
