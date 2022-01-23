# V-Notes, Note taking app using Python and GTK framework.
#     Copyright (C) 2022  Vega
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi, sys, mainmenu, editor, dropdown
from gi.repository import GLib

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
import settingsmenu, conf


class Main(Gtk.ApplicationWindow):
    def __init__(self, application, title="Main Window"):
        super().__init__(title="Hello World")

        self.parent = application
        self.conf = conf.confblob()
        self.set_size_request(500, 500)
        # This will be in the windows group and have the "win" prefix
        max_action = Gio.SimpleAction.new_stateful(
            "maximize", None, GLib.Variant.new_boolean(False)
        )
        max_action.connect("change-state", self.on_maximize_toggle)
        self.add_action(max_action)

        # Keep it in sync with the actual state
        self.connect(
            "notify::is-maximized",
            lambda obj, pspec: max_action.set_state(
                GLib.Variant.new_boolean(obj.props.is_maximized)
            ),
        )
        # setup header bar
        self.header_bar_init()

        # setup tabs
        self.notebook = Gtk.Notebook()
        self.notebook.popup_enable()

        newicon = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="accessories-dictionary-symbolic"), Gtk.IconSize.BUTTON)
        self.notebook.append_page(mainmenu.MainMenu(self), newicon)
        self.show_all()
        # self.create_tab()

        self.panes = Gtk.Paned()
        self.panes.pack1(dropdown.NoteBrowser(self), True, False)
        self.panes.pack2(self.notebook, True, False)
        self.add(self.panes)

        self.show_all()

    def on_maximize_toggle(self, action, value):
        action.set_state(value)
        if value.get_boolean():
            self.maximize()
        else:
            self.unmaximize()

    def header_bar_init(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "V-Notes"
        self.set_titlebar(hb)

        button = Gtk.MenuButton(popover=dropdown.Popover(parent=self))
        button.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="pan-down-symbolic"), Gtk.IconSize.BUTTON))
        button.connect("clicked", self.on_dropdown_click)
        hb.pack_end(button)

        self.save_button = Gtk.Button(label="Save")
        self.save_button.connect("clicked", self.on_save_click)
        hb.pack_end(self.save_button)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        button = Gtk.Button()
        button.connect("clicked", self.on_left_pane_changed)
        button.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="go-previous-symbolic"), Gtk.IconSize.BUTTON))
        box.add(button)

        button = Gtk.Button()
        button.connect("clicked", lambda x:self.create_tab())
        button.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="tab-new-symbolic"), Gtk.IconSize.BUTTON))
        box.add(button)

        hb.pack_start(box)

    def on_left_pane_changed(self, button):
        pane = self.panes.get_child1()
        is_visible = pane.get_visible()
        pane.set_visible(not is_visible)
        if is_visible:
            button.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="go-next-symbolic"), Gtk.IconSize.BUTTON))
        else:
            button.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="go-previous-symbolic"), Gtk.IconSize.BUTTON))

    def create_tab(self, text=None, filename=None, *args):
        tab_number = self.notebook.get_n_pages()
        if text and filename:
            from copy import copy
            path = copy(filename)
            filename = filename.split("/")[-1]
            tab_name = filename
        else:
            tab_name = "New Note " + str(tab_number)
            path = None

        page = editor.Editor(self, tab_number=tab_number, text=text, filename=filename, path=path)
        page.set_border_width(1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        hbox.set_center_widget(Gtk.Label(label=tab_name))

        tab_button = Gtk.Button()
        tab_button.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="window-close-symbolic"), Gtk.IconSize.BUTTON))
        tab_button.connect("clicked", page.close)
        tab_button.props.relief = Gtk.ReliefStyle.NONE
        hbox.pack_end(tab_button, True, True, 3)

        hbox.show_all()

        self.notebook.append_page(page, hbox)
        self.show_all()
        self.notebook.set_current_page(tab_number)
        # page.on_text_change()

    def on_dropdown_click(self, *args, **kwargs):
        pass

    def on_save_click(self, *args, **kwargs):
        current_page = self.notebook.get_current_page()
        current_editor = self.notebook.get_nth_page(current_page)
        if type(current_editor) is not mainmenu.MainMenu:
            filename = self.notebook.get_tab_label(current_editor).get_center_widget().get_text()
            current_editor.save(filename)


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.example.vnotes", **kwargs)
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        action = Gio.SimpleAction(name="about")
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction(name="quit")
        action.connect("activate", self.on_quit)
        self.add_action(action)
        self.do_activate()

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = Main(application=self)

        self.window.present()
        self.window.show()

    def on_about(self, action=None, param=None):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.set_authors(["Vega D"])
        about_dialog.set_copyright("©2022, Vega")
        about_dialog.set_logo_icon_name("preferences-desktop-keyboard-shortcuts-symbolic")
        about_dialog.set_version("0.5-beta")
        with open("../LICENSE.txt", "r") as license:
            about_dialog.set_license("".join(license.readlines()))
        about_dialog.present()

    def on_settings(self, *args):
        dialog = Gtk.Dialog(
            transient_for=self.window,
            flags=0,
            # message_type=Gtk.MessageType.INFO,
            # buttons=Gtk.ButtonsType.NONE,
            title="Preferences",
        )
        settings = settingsmenu.Settings(self.window)
        box = dialog.get_content_area()
        box.set_border_width(10)
        box.add(settings)
        dialog.run()
        dialog.destroy()

    def on_quit(self, action, param):
        self.quit()


# win = Main()
# win.connect("destroy", Gtk.main_quit)
# win.show_all()
# Gtk.main()

if __name__ == "__main__":
    app = Application()
    GLib.set_application_name("V-Notes")
    app.run(sys.argv)
    Gtk.main()
