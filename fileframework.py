from copy import copy

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


def listfiles():
    return ["recent file 1.md", " recent file 2.md"]


def savebuffer(filename, buffer):
    if filename[-3:] != ".md":
        filename += ".md"

    # print("gotta save", filename, buffer)
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
    dialog.set_current_name(filename)
    filter = Gtk.FileFilter()
    filter.add_pattern(".md")
    filter.set_name(".md notes")
    dialog.add_filter(filter)

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


def openfile(filename=None, open_dialog=True):
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
        filter.add_pattern(".md")
        filter.set_name(".md notes")
        # dialog.add_filter(filter)

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
            return openfile(filename=None)
        else:
            return None, None

    text = "".join(file_to_open.readlines())
    # print([text])
    return text, filename


def mdformat(textbuffer, iters=False):
    text = textbuffer.get_text(
        textbuffer.get_iter_at_line(0),
        textbuffer.get_iter_at_line(textbuffer.get_line_count()),
        False)
    # processing B O L D
    all_bold_points = []
    tmp = copy(text)
    while tmp.find("**") > -1:
        point = tmp.find("**")
        if point > -1:
            tmp = tmp[(point + 2):]
            if all_bold_points:
                point += all_bold_points[-1]
                if len(all_bold_points) % 2:
                    point += 4
                else:
                    point += 2
            all_bold_points.append(point)
    if len(all_bold_points) % 2 != 0:
        all_bold_points.pop(-1)

    # processing I T A L I C
    all_italic_points = []
    tmp = copy(text).replace("__", "xx")
    while tmp.find("_") > -1:
        point = tmp.find("_")
        if point > -1:
            tmp = tmp[(point + 1):]
            if all_italic_points:
                point += all_italic_points[-1]
                if len(all_italic_points) % 2:
                    point += 2
                else:
                    point += 1
            all_italic_points.append(point)
    if len(all_italic_points) % 2 != 0:
        all_italic_points.pop(-1)
    # print(all_italic_points)

    # processing U N D E R L I N E
    all_underline_points = []
    tmp = copy(text)
    while tmp.find("__") > -1:
        point = tmp.find("__")
        if point > -1:
            tmp = tmp[(point + 2):]
            if all_underline_points:
                point += all_underline_points[-1]
                if len(all_underline_points) % 2:
                    point += 4
                else:
                    point += 2
            all_underline_points.append(point)
    if len(all_underline_points) % 2 != 0:
        all_underline_points.pop(-1)
    # print(all_underline_points)

    if iters:
        all_bold_points = [textbuffer.get_iter_at_offset(i) for i in all_bold_points]
        all_italic_points = [textbuffer.get_iter_at_offset(i) for i in all_italic_points]
        all_underline_points = [textbuffer.get_iter_at_offset(i) for i in all_underline_points]

    # transforming into pairs
    tmp = []
    for i in range(len(all_bold_points)):
        if i % 2 == 1:
            tmp[-1].append(all_bold_points[i])
        else:
            tmp.append([all_bold_points[i]])
    all_bold_points = tmp

    tmp = []
    for i in range(len(all_italic_points)):
        if i % 2 == 1:
            tmp[-1].append(all_italic_points[i])
        else:
            tmp.append([all_italic_points[i]])
    all_italic_points = tmp

    tmp = []
    for i in range(len(all_underline_points)):
        if i % 2 == 1:
            tmp[-1].append(all_underline_points[i])
        else:
            tmp.append([all_underline_points[i]])
    all_underline_points = tmp
    return all_bold_points, all_italic_points, all_underline_points


def ismd(selected):
    pass
