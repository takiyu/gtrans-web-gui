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
* [x] Windows Python 3.6
* [x] Windows PowerShell Python 3.6
* [ ] Mac OS Python 2.x
* [ ] Mac OS Python 3.x

## Usage ##
```bash
$ python python/gtransweb_gui.py [-h] [-s SRC_LANG] [-t TGT_LANG]
                                 [-c {copy,select,findbuf}] [-b BUF_TIME]

# Example for Linux
$ python python/gtransweb_gui.py

# Example for Windows
$ python python/gtransweb_gui.py -c copy -b 0
```

## Arguments ##
```
  -h, --help                        Show the help message and exit.
  -s SRC_LANG, --src_lang SRC_LANG  Source language.  {default: auto]
  -t TGT_LANG, --tgt_lang TGT_LANG  Target language.  [default: ja]
  -c {copy,select,findbuf}, --clip_mode {copy,select,findbuf}
                                    Clipboard mode for translation trigger.
                                    'select' is valid on only Linux.
                                    [default on Linux: select,
                                     Others          : copy]
  -b BUF_TIME, --buf_time BUF_TIME  Buffering time for clipboard.
                                    [default on Linux: 1000 (for select mode),
                                     Others          : 0]
```

## Keyboard Shortcuts ##
* ESC            : Hide the window and wait for clipboard action.
* Enter (+ CTRL) : Start to translate the text in the text box.

## Screenshot ##
<img src="https://raw.githubusercontent.com/takiyu/gtrans-web-gui/master/screenshots/1.png">

## TODO ##
* [ ] Support for Mac OS X. Clipboard behavior is something wrong.
* [ ] Additional GUI, such as language selection, save settings and so on.

## Others ##
This plugin is tested on few environments.

I hope your pull requests!
