# furigana4epub

A Python script for adding furigana to Japanese epub books using Mecab and Unidic.

Should work with Python3.6 or higher, but only tested with Python 3.7.5

This script is inspired by [WebNovelCrawler](https://github.com/tongyuantongyu/WebNovelCrawler) ,and using some codes from it.

#### Install
`git clone https://github.com/Mumumu4/furigana4epub.git`

install python required packages:

`pip install -r requirements.txt -v`\
or\
`pip install lxml beautifulsoup4 fugashi unidic_lite`

#### Usage
`python3 furigana4epub.py target.epub`

```
python3 furigana4epub.py -h
usage: furigana4epub.py [-h] [-e EXTENSION] [-r] [-d] [-p] [-q]
                        paths [paths ...]

This script is written for adding furigana to Japanese epub books.

positional arguments:
  paths                 Paths of Japanese epub books

optional arguments:
  -h, --help            show this help message and exit
  -e EXTENSION, --extension EXTENSION
                        File extension to filter by(default:.epub)
  -r, --recursive       Search through subfolders
  -d, --em              Covert <ruby> dot to html <em> tag before adding
                        furigana
  -p, --rp              Do not add ruby <rp> tag to provide fall-back
                        parentheses for browsers that do not support display
                        of ruby annotations
  -q, --quiet           Be quiet
```