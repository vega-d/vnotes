# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import json, os, subprocess

configfolder = os.environ.get("XDG_CONFIG_HOME")

try:
    documentsfolder = subprocess.check_output(["xdg-user-dir", "DOCUMENTS"], universal_newlines=True).strip()
except:
    documentsfolder = os.path.join(os.path.expanduser("~"), "Documents")

print("config folder is:", configfolder)

class confblob:
    def __init__(self):

        self.default_folder = None
        self.autosave = None
        self.debug = None
        self.update_current()

    def get_default_folder(self):
        return self.default_folder

    def set_default_folder(self, path):
        self.default_folder = path
        return self.update_current()

    def get_autosave(self):
        return self.autosave if self.autosave else False

    def set_autosave(self, autosave):
        self.autosave = autosave
        return self.update_current()

    def get_debug(self):
        return self.debug

    def set_debug(self, debug):
        if debug is None:
            self.debug = not self.debug
        else:
            self.debug = debug
        return self.update_current()

    def update_current(self):
        try:
            with open((configfolder + "/vnotes_conf.json"), "r+") as conffile:
                current_json = json.dumps(self.__dict__)
                current_from_file_json = "".join(conffile.readlines())
                # print(current_json, current_from_file_json)
                print("I: Loaded in this config:", current_from_file_json)
                if current_json == current_from_file_json:
                    return True
                else:
                    current_from_file = json.loads(current_from_file_json)
                    current = self.__dict__

                    for setting in current.keys():
                        # loading in from the file
                        if current[setting] is None:
                            self.__setattr__(setting, current_from_file[setting])
                    # print([current_from_file, current])
                    # after we finished making sure all changes from the conf file are applied
                    # we can safely write to the conf file
                    current = self.__dict__
                    current_json = json.dumps(current)
                    conffile.seek(0)
                    conffile.truncate()
                    conffile.writelines(current_json)

                    return True
        except Exception as e:
            if type(e) == FileNotFoundError:
                print("looks like conf file doesn't exist, creating one!")  # TODO: create first time setup
                with open((configfolder + "/vnotes_conf.json"), "a+") as file:
                    file.write(
                        """{"default_folder": \"""" + documentsfolder + """\", "autosave": "false", "debug": "false"}""")
                return self.update_current()
            print("E: Could not save current settings!", e)
            return False
