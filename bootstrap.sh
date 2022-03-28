#!/bin/bash
echo "bootstrapping all required files for the flatpak."
required_files=("src/main.py" "src/mainmenu.py" "src/conf.py" "src/dropdown.py"\
 "src/editor.py" "src/fileframework.py" "src/settingsmenu.py" "src/run.sh"\
 "io.github.vegad.vnotes.desktop" "io.github.vegad.vnotes.appdata.xml" "icons/icon.svg"\
 "icons/icon_48.png" "icons/icon_128.png" "LICENSE.txt" "io.github.vegad.vnotes.yml")
gitlink="https://raw.githubusercontent.com/vega-d/vnotes/master/"
mkdir "src"
for file in "${required_files[@]}"
do
  rm "$file"
  current_link="${gitlink}""${file}"
  curl "$current_link" > "$file"
done
echo "finished the download of all required files for the flatpak."

