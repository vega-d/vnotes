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

        button = Gtk.ModelButton(label="Preferences")
        button.connect("clicked", parent.parent.on_settings)
        vbox.pack_start(button, True, True, 5)

        button = Gtk.ModelButton(label="About")
        button.connect("clicked", parent.parent.on_about)
        vbox.pack_start(button, True, True, 5)

        vbox.show_all()
        self.add(vbox)
        self.set_position(Gtk.PositionType.BOTTOM)


class NoteBrowser(Gtk.ScrolledWindow):
    def __init__(self, parent):
        super(NoteBrowser, self).__init__()
        self.set_size_request(100, 450)
        self.parent = parent
        # initialize the filesystem treestore
        from gi.repository.GdkPixbuf import Pixbuf
        fileSystemTreeStore = Gtk.TreeStore(str, Pixbuf, str)
        # populate the tree store
        self.populateFileSystemTreeStore(fileSystemTreeStore, parent.conf.get_default_folder())
        # initialize the TreeView
        self.fileSystemTreeView = Gtk.TreeView(fileSystemTreeStore)

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
        self.fileSystemTreeView.append_column(treeViewCol)

        self.fileSystemTreeView.connect("row-expanded", self.onRowExpanded)
        self.fileSystemTreeView.connect("row-collapsed", self.onRowCollapsed)
        self.fileSystemTreeView.connect("row-activated", self.onRowActivated)

        self.fileSystemTreeView.set_activate_on_single_click(True)
        self.fileSystemTreeView.set_enable_tree_lines(True)

        scrollView = Gtk.ScrolledWindow()
        scrollView.add(self.fileSystemTreeView)
        self.add(scrollView)

    def populateFileSystemTreeStore(self, treeStore, path, parent=None):
        itemCounter = 0
        # iterate over the items in the path
        import os
        try:
            fileslist = os.listdir(path)

            # filter out all dotfiles
            fileslist = list(filter(lambda x: x[0]!='.', fileslist))
        except FileNotFoundError as e:
            print("Was unable to load in Notes folder!", e)
            dialog = Gtk.MessageDialog(transient_for=self.parent, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Unable to access preferred Notes folder, please change it in the Settings menu!")

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                dialog.destroy()
            return

        def sorting_key(path):
            get_mod_time = 0
            try:
                get_mod_time = os.path.getmtime(path)
            except Exception as e:
                print("W: Could not access", path)
            return get_mod_time

        fileslist = [os.path.join(path, f) for f in fileslist]  # add path to each file
        fileslist.sort(key=sorting_key)
        fileslist.reverse()
        for item in fileslist:
            # Get the absolute path of the item
            itemFullname = item
            item = item.split("/")[-1]
            # Extract metadata from the item
            try:
                itemMetaData = os.stat(itemFullname)
            except FileNotFoundError as e:
                print("W: could not access", itemFullname)
                next(iter(fileslist))
            # Determine if the item is a folder
            import stat
            itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
            # Append the item to the TreeStore
            currentIter = treeStore.append(parent, [item, None, itemFullname])
            # add dummy if current item was a folder
            if itemIsFolder:
                treeStore.append(currentIter, [None, None, None])
            # increment the item counter
            itemCounter += 1
        # add the dummy node back if nothing was inserted before
        if itemCounter < 1: treeStore.append(parent, [None, None, None])

    def onRowExpanded(self, treeView, treeIter, treePath):
        # get the associated model
        treeStore = treeView.get_model()
        # get the full path of the position
        newPath = treeStore.get_value(treeIter, 2)
        # populate the subtree on current position
        self.populateFileSystemTreeStore(treeStore, newPath, treeIter)
        # remove the first child (dummy node)
        treeStore.remove(treeStore.iter_children(treeIter))

    def onRowCollapsed(self, treeView, treeIter, treePath):
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

    def onRowActivated(self, treeView, treePath, treeViewCommon):
        model = treeView.get_model()
        path = treePath.to_string()
        print(path)
        iter = model.get_iter(path)
        filename = model.get_value(iter, 2)

        import os, stat
        itemMetaData = os.stat(filename)
        # Determine if the item is a folder
        itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
        if itemIsFolder:
            treeItem = model.iter_children(iter)
            if treeItem:
                is_unfolded = bool(model.get_value(treeItem, 2))
                if is_unfolded:
                    self.onRowCollapsed(treeView, iter, treePath)
                    # treeView.(treePath)
                else:
                    self.onRowExpanded(treeView, iter, treePath)
                    treeView.expand_to_path(treePath)
        else:
            notebook = self.get_parent().get_child2()
            notebook.get_nth_page(0).on_open_note(filename)

    def update(self):
        return False ## honestly I don't know how this can even remotely work
        TreeStore = self.fileSystemTreeView.get_model()

        def clean(TreeStore, TreePath, TreeIter):
            with TreeStore.iter_parent(TreeIter) as parent:
                if parent is not None:
                    TreeIter = parent
            TreeStore.remove(TreeIter)
            return False
        TreeStore.foreach(clean)
        # self.populateFileSystemTreeStore(TreeStore, self.parent.conf.get_default_folder(), None)
