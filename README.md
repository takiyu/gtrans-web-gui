# Gtrans-Web-GUI #

GUI helper for Google Translation Website.

This application translates your copied or selected texts using Google Translation Website.

## Dependency ##
* Python (2.x or 3.x)
* Qt5 (Python binding)

## Supports ##
* [x] Linux Python 2.7
* [x] Linux Python 3.6
* [ ] Windows Python 2.x
* [ ] Windows Python 3.x
* [ ] Mac OS Python 2.x
* [ ] Mac OS Python 3.x

## Usage ##
```bash
$ python python/gtransweb_gui.py [-h] [--src_lang SRC_LANG]
                                 [--tgt_lang TGT_LANG] [--encoding ENCODING]
                                 [--clip_mode {copy,select,findbuf}]
                                 [--buf_time BUF_TIME]

# Example for Linux
$ python python/gtransweb_gui.py

#Example for Windows
$ python python/gtransweb_gui.py --clip_mode copy --buf_time 0
```

## Arguments ##
```
  -h, --help            show the help message and exit.
  --src_lang SRC_LANG   Source language.
  --tgt_lang TGT_LANG   Target language.
  --encoding ENCODING   Text encoding used in python str for input.
  --clip_mode {copy,select,findbuf}
                        Clipboard mode for translation trigger.
  --buf_time BUF_TIME   Buffering time for clipboard.
```

## Screenshot ##
<img src="https://raw.githubusercontent.com/takiyu/gtrans-web-gui/master/screenshots/1.png">

## TODO ##
* [ ] Support for Mac OS X and Windows.
* [ ] Additional GUI, such as language selection, save settings and so on.

## Others ##
This plugin is tested on few environments.

I hope your pull requests!
