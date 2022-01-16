# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import gi, fileframework, os, stat, conf

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

        def populateFileSystemTreeStore(treeStore, path, parent=None):
            itemCounter = 0
            # iterate over the items in the path
            fileslist = os.listdir(path)
            fileslist = [os.path.join(path, f) for f in fileslist]  # add path to each file
            fileslist.sort(key=lambda x: os.path.getmtime(x))
            fileslist.reverse()
            for item in fileslist:
                # Get the absolute path of the item
                itemFullname = item
                item = item.split("/")[-1]
                # Extract metadata from the item
                itemMetaData = os.stat(itemFullname)
                # Determine if the item is a folder
                itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
                # Generate an icon from the default icon theme
                itemIcon = Gio.ThemedIcon(name=("folder-symbolic" if itemIsFolder else "empty"))
                itemIcon = Gtk.Image.new_from_gicon(itemIcon, Gtk.IconSize.BUTTON)
                itemIcon = itemIcon.get_pixbuf()

                # Append the item to the TreeStore
                currentIter = treeStore.append(parent, [item, itemIcon, itemFullname])
                # add dummy if current item was a folder
                if itemIsFolder:
                    treeStore.append(currentIter, [None, None, None])
                # increment the item counter
                itemCounter += 1
            # add the dummy node back if nothing was inserted before
            if itemCounter < 1: treeStore.append(parent, [None, None, None])

        def onRowExpanded(treeView, treeIter, treePath):
            # get the associated model
            treeStore = treeView.get_model()
            # get the full path of the position
            newPath = treeStore.get_value(treeIter, 2)
            # populate the subtree on curent position
            populateFileSystemTreeStore(treeStore, newPath, treeIter)
            # remove the first child (dummy node)
            treeStore.remove(treeStore.iter_children(treeIter))

        def onRowCollapsed(treeView, treeIter, treePath):
            # get the associated model
            treeStore = treeView.get_model()
            # get the iterator of the first child
            currentChildIter = treeStore.iter_children(treeIter)
            # loop as long as some childern exist
            while currentChildIter:
                # remove the first child
                treeStore.remove(currentChildIter)
                # refresh the iterator of the next child
                currentChildIter = treeStore.iter_children(treeIter)
            # append dummy node
            treeStore.append(treeIter, [None, None, None])

        def onRowActivated(treeView, treePath, treeViewCommon):
            model = treeView.get_model()
            path = treePath.to_string()
            iter = model.get_iter(path)
            filename = model.get_value(iter, 2)

            itemMetaData = os.stat(filename)
            # Determine if the item is a folder
            itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
            if itemIsFolder:
                unfolded = model.iter_children(iter)
                if unfolded:
                    unfolded = bool(model.get_value(unfolded, 2))
                if unfolded:
                    onRowCollapsed(treeView, iter, treePath)
                    # treeView.(treePath)
                else:
                    onRowExpanded(treeView, iter, treePath)
                    treeView.expand_to_path(treePath)
            else:
                self.on_open_note(filename)

        # initialize the filesystem treestore
        fileSystemTreeStore = Gtk.TreeStore(str, Pixbuf, str)
        # populate the tree store
        populateFileSystemTreeStore(fileSystemTreeStore, parent.conf.get_default_folder())
        # initialize the TreeView
        fileSystemTreeView = Gtk.TreeView(fileSystemTreeStore)

        # Create a TreeViewColumn
        treeViewCol = Gtk.TreeViewColumn("Notes")
        # Create a column cell to display text
        colCellText = Gtk.CellRendererText()
        # Create a column cell to display an image
        colCellImg = Gtk.CellRendererPixbuf()
        # Add the cells to the column
        treeViewCol.pack_start(colCellImg, False)
        treeViewCol.pack_start(colCellText, True)
        # Bind the text cell to column 0 of the tree's model
        treeViewCol.add_attribute(colCellText, "text", 0)
        # Bind the image cell to column 1 of the tree's model
        treeViewCol.add_attribute(colCellImg, "pixbuf", 1)
        # Append the columns to the TreeView
        fileSystemTreeView.append_column(treeViewCol)
        # add "on expand" callback
        fileSystemTreeView.connect("row-expanded", onRowExpanded)
        # add "on collapse" callback
        fileSystemTreeView.connect("row-collapsed", onRowCollapsed)
        fileSystemTreeView.connect("row-activated", onRowActivated)
        fileSystemTreeView.set_activate_on_single_click(True)
        fileSystemTreeView.set_enable_tree_lines(True)
        scrollView = Gtk.ScrolledWindow()
        scrollView.add(fileSystemTreeView)

        self.pack_start(scrollView, True, True, 5)

        # self.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), True, True, 5)

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
