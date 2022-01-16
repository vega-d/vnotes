# Copyright (C) 2022 Vega
# This program is free software, You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import json, os
from xdg import xdg_config_home
configfolder = xdg_config_home().__str__()
documentsfolder = os.path.join(os.path.expanduser("~"), "Documents")


class confblob:
    def __init__(self):

        self.default_folder = None
        self.additional_test_info = "configuration"
        self.update_current()

    def get_default_folder(self):
        return self.default_folder

    def set_default_folder(self, path):
        self.default_folder = path
        return self.update_current()

    def update_current(self):
        try:
            with open((configfolder + "/vnotes_conf.json"), "r+") as conffile:
                current_json = json.dumps(self.__dict__)
                current_from_file_json = "".join(conffile.readlines())
                if current_json == current_from_file_json:
                    return True
                else:
                    current_from_file = json.loads(current_from_file_json)
                    current = self.__dict__
                    for setting in current.keys():
                        # loading in from the file
                        if current[setting] is None:
                            self.__setattr__(setting, current_from_file[setting])
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
                    file.write("""{"default_folder": \"""" + documentsfolder + """\", "additional_test_info": "configuration"}""")
                return self.update_current()
            print("E: Could not save current settings!", e)
            return False
