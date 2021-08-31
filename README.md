# furigana4epub

A Python script to add/remove furigana for Japanese epub books. Using Mecab and Unidic.

 ある日の放課後だった。

<p>ある<ruby>日<rp>(</rp><rt>ひ</rt><rp>)</rp></ruby>の<ruby>放課<rp>(</rp><rt>ほうか</rt><rp>)</rp>後<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>だった。</p>

Should work with Python3.6 or higher, but only tested with Python 3.7.5


## Install
`pip install furigana4epub`

If you want to use [the full version of UniDic](https://github.com/polm/unidic-py#unidic-py), read [this article](https://github.com/polm/fugashi#installing-a-dictionary).
## Usage
To add furigana:\
`furigana4epub target.epub`

To remove furigana:\
`furigana4epub -d target.epub`

```
furigana4epub -h
usage: furigana4epub [-h] [-e EXTENSION] [-r] [-d] [-b] [-p]
                        paths [paths ...]

A Python script to add/remove furigana for Japanese epub books. Using Mecab and Unidic.

positional arguments:
  paths                 Paths of Japanese epub books

optional arguments:
  -h, --help            show this help message and exit
  -e EXTENSION, --extension EXTENSION
                        File extension to filter by(default:.epub)
  -r, --recursive       Search through subfolders
  -d, --remove          remove furigana from epub file
  -b, --blod            Covert <ruby> dot to html <b> tag before adding
                        furigana
  -p, --rp              Do not add ruby <rp> tag to provide fall-back
                        parentheses for browsers that do not support display
                        of ruby annotations
```
## A note for Kindle
If you are using [Calibre](https://calibre-ebook.com) for ebook conversion, choose azw3(KF8) output format.\
Calibre's mobi output format wouldn't support `<ruby>` tag.

## Credits
This script is inspired by [WebNovelCrawler](https://github.com/tongyuantongyu/WebNovelCrawler), [pinyin2epub](https://github.com/shotazc/pinyin2epub)  ,have some codes from them.