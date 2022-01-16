# V-Notes, a GTK note-taking app.

A simple and fast note-taking app for Linux, written in Python with GTK licensed under GPLv3.

![sc1](https://i.postimg.cc/nzKycyx5/sc1.png)
![sc2](https://i.postimg.cc/9Mj32W6Z/sc2.png)


## Installation
Download `.flatpak` file from releases page and install it with either graphical software manager you have or
```commandline
flatpak install vnotes.flatpak
```


## Run from source

Install python3, and relevant dependencies if those are missing: `pygobject`, `xdg` and `stat`. 

Download source code from the repo using "Code" => "Download as Zip" button above or with this command:
```commandline 
git clone https://github.com/vega-d/vnotes
```

Run main.py:
```commandline
cd vnotes & python3 main.py
```

And the app should start right away!
