import gi, fileframework

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class MainMenu(Gtk.Box):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label("V-Notes!")
        vbox.pack_start(label, True, True, 5)

        button = Gtk.Button()
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="tab-new-symbolic"), Gtk.IconSize.BUTTON), True, True, 5)
        button_box.set_center_widget(Gtk.Label("New Note"))
        button.add(button_box)
        button.connect("clicked", self.on_create_new)
        vbox.pack_start(button, True, True, 5)

        button = Gtk.Button()
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="document-open-symbolic"), Gtk.IconSize.BUTTON), True, True, 5)
        button_box.set_center_widget(Gtk.Label("Open Note"))
        button.add(button_box)
        button.connect("clicked", self.on_open_note)
        vbox.pack_start(button, True, True, 5)

        frame = Gtk.Frame()
        frame.set_label("Recent Files")
        frame.set_label_align(0.5, 0.5)

        recent_files = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        for file in fileframework.listfiles()[:4]:
            button = Gtk.Button()
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            button_box.set_center_widget(Gtk.Label(str(file)[:32]))
            button.add(button_box)
            button.props.relief = Gtk.ReliefStyle.NONE
            button.connect("clicked", self.on_open_note)
            recent_files.pack_start(button, True, True, 1)

        frame.add(recent_files)
        vbox.pack_start(frame, True, True, 5)

        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)

        self.pack_start(vbox, True, True, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def on_create_new(self, *args, **kwargs):
        self.parent.create_tab()

    def on_open_note(self, filename, *args, **kwargs):
        if type(filename) is Gtk.Button:
            filename = filename.get_children()[0].get_center_widget().get_text()
        print("Opening!", filename)
        pass # TODO: opening files