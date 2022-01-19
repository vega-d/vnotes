# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import gi, fileframework

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


class SearchDialog(Gtk.Dialog):
    def __init__(self):
        super().__init__()
        self.add_buttons(
            Gtk.STOCK_FIND,
            Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
        )

        box = self.get_content_area()
        box.set_border_width(10)
        label = Gtk.Label(label="Insert text you want to search for:")
        box.add(label)

        self.entry = Gtk.Entry()
        box.add(self.entry)

        self.show_all()


class Editor(Gtk.Box):
    def __init__(self, parent, tab_number, text=None, filename=None, path=None):
        super().__init__()
        self.parent_notebook = parent.notebook
        self.parent = parent
        self.path = path
        self.tab_number = tab_number
        self.set_resize_mode(True)
        self.saved = True
        self.grid = Gtk.Grid()
        self.filename = filename
        self.create_textview()
        self.create_toolbar()
        self.add(self.grid)
        self.found = self.textbuffer.create_tag("found", background="yellow")
        tags_tmp = [
            self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD),
            self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC),
            self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        ]
        self.tag_mods = {
            tags_tmp[0]: "**",
            tags_tmp[1]: "_",
            tags_tmp[2]: "__"
        }
        self.tags = {
            "bold": tags_tmp[0],
            "italic": tags_tmp[1],
            "underline": tags_tmp[2],
        }
        if text:
            self.textbuffer.set_text(text)
            self.on_saved_change(True)

    def create_toolbar(self):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        button_bold = Gtk.ToolButton()
        button_bold.set_icon_name("format-text-bold-symbolic")
        toolbar.insert(button_bold, 0)

        button_italic = Gtk.ToolButton()
        button_italic.set_icon_name("format-text-italic-symbolic")
        toolbar.insert(button_italic, 1)

        button_underline = Gtk.ToolButton()
        button_underline.set_icon_name("format-text-underline-symbolic")
        toolbar.insert(button_underline, 2)

        button_bold.connect("clicked", self.on_button_clicked, "bold")
        button_italic.connect("clicked", self.on_button_clicked, "italic")
        button_underline.connect("clicked", self.on_button_clicked, "underline")

        toolbar.insert(Gtk.SeparatorToolItem(), 3)

        button_wrap = Gtk.ToolButton()
        button_wrap.set_icon_name("format-indent-less-symbolic")
        button_wrap.connect("clicked", self.on_wrap_toggled, )
        toolbar.insert(button_wrap, 11)

        toolbar.insert(Gtk.SeparatorToolItem(), 8)

        button_search = Gtk.ToolButton()
        button_search.set_icon_name("system-search-symbolic")
        button_search.connect("clicked", self.on_search_clicked)
        toolbar.insert(button_search, 11)

    def create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.connect('changed', self.on_text_change)
        scrolledwindow.add(self.textview)

    def on_text_change(self, *args, **kwargs):
        # apply new name if it's blank or default
        buffer = self.textbuffer.get_text(
            self.textbuffer.get_iter_at_line(0),
            self.textbuffer.get_iter_at_line(1),
            False)
        buffer = buffer.strip().lstrip("#").strip("_").strip("*")[:64]
        if len(buffer) and self.parent_notebook.get_tab_label(self):
            name_label = self.parent_notebook.get_tab_label(self).get_center_widget()
            current_name = name_label.get_text().rstrip(".md").rstrip(".txt")
            if current_name == ("New Note " + str(self.tab_number)) or current_name == buffer[:len(current_name)]:
                name_label.set_text(buffer + ".txt")

        # clean all formatting
        self.textbuffer.remove_all_tags(self.textbuffer.get_iter_at_line(0),
                                        self.textbuffer.get_iter_at_line(self.textbuffer.get_line_count()))

        # apply new formatting
        # tags =
        for kind in ["bold", "italic", "underline", "header1"]:
            points = fileframework.mdformat(self.textbuffer, iters=True, kind=kind)

            for i in points:
                self.textbuffer.apply_tag(self.tags[kind], i[0], i[1])

        # marking that file was changing
        if len(buffer):
            self.on_saved_change(False)

    def on_button_clicked(self, widget, tag_name):
        def bounds_calc():
            bounds = self.textbuffer.get_selection_bounds()
            if len(bounds) != 0:
                start, end = bounds
            else:
                cursor = self.textbuffer.props.cursor_position
                cursor = self.textbuffer.get_iter_at_offset(cursor)
                start = cursor.copy()
                start.set_line_offset(0)
                end = cursor.copy()
                end.set_line_offset(end.get_chars_in_line() - 1)
                bounds = start, end
            return bounds, start, end

        bounds, start, end = bounds_calc()
        mod = self.tag_mods[self.tags[tag_name]]

        self.textbuffer.insert(start, mod)
        bounds, start, end = bounds_calc()
        start, end = bounds
        self.textbuffer.insert(end, mod)
        self.on_text_change()

    def on_editable_toggled(self, widget):
        self.textview.set_editable(widget.get_active())

    def on_cursor_toggled(self, widget):
        self.textview.set_cursor_visible(widget.get_active())

    def on_wrap_toggled(self, widget):
        if self.textview.get_wrap_mode() is Gtk.WrapMode.WORD:
            mode = Gtk.WrapMode.NONE
        else:
            mode = Gtk.WrapMode.WORD
        self.textview.set_wrap_mode(mode)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

    def on_search_clicked(self, widget):
        dialog = SearchDialog()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            cursor_mark = self.textbuffer.get_insert()
            start = self.textbuffer.get_iter_at_mark(cursor_mark)
            if start.get_offset() == self.textbuffer.get_char_count():
                start = self.textbuffer.get_start_iter()

            self.search_and_mark(dialog.entry.get_text(), start)

        dialog.destroy()

    def search_and_mark(self, text, start):
        end = self.textbuffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match is not None:
            match_start, match_end = match
            self.textbuffer.apply_tag(self.tag_found, match_start, match_end)
            self.search_and_mark(text, match_end)

    def save(self, filename):
        if not self.saved:
            try:
                success = fileframework.savebuffer(filename, self.textbuffer, folder=self.filename)
                if success:
                    self.on_saved_change(True)
            except Exception as e:
                self.on_saved_change(False)
                print("E: Failed to save, ", e)

    def close(self, *args, **kwargs):
        filename = self.parent_notebook.get_tab_label(self).get_center_widget().get_text()
        if self.saved:
            self.destroy()
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self.parent,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.NONE,
                text="Save changes to note " + filename + " before closing?",
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_DISCARD, Gtk.ResponseType.ACCEPT,
                Gtk.STOCK_SAVE_AS, Gtk.ResponseType.OK
            )
            dialog.format_secondary_text("If you don't save changes made to the file will be permanently lost.")
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.save(filename)
            elif response == Gtk.ResponseType.ACCEPT:
                self.destroy()
            elif response == Gtk.ResponseType.CANCEL:
                pass
            dialog.destroy()

    def on_saved_change(self, saved):
        self.saved = saved
        if self.parent.conf.get_autosave() and self.path.split("/")[-1] == self.filename:
            import os
            if os.path.exists(self.path):
                self.save(filename=self.path)
