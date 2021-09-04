# coding: utf-8
from itertools import groupby
import re

from bs4 import BeautifulSoup
from bs4.element import (NavigableString, Script, Stylesheet, Tag,
                         TemplateString)
from fugashi import Tagger

tagger = Tagger()

katakana_chart = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
hiragana_chart = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
h2k = str.maketrans(hiragana_chart, katakana_chart)
k2h = str.maketrans(katakana_chart, hiragana_chart)

white_space_re = re.compile(r'(\s+)')


class RBString(NavigableString):
    '''class for <ruby> tag'''
    pass


class RTString(NavigableString):
    '''class for <rt> tag'''
    pass


class RPString(NavigableString):
    '''class for <rp> tag'''
    pass


# strings in tag which in string_containers will not appear in bs4's get_text()
# this could be controlled by a parameter of get_text() ,see its docstring
string_containers = {
    'rp': RPString,
    'rt': RTString,
    'style': Stylesheet,
    'script': Script,
    'template': TemplateString,
}
basesoup = BeautifulSoup(
    "<b></b>", 'lxml', string_containers=string_containers)


def point_ruby_to_blod(soup):
    for ruby in soup.find_all('ruby'):
        rt = ruby.rt.string.strip()
        if rt in '・' * 100:
            rep = basesoup.new_tag('b')
            rep.string = ruby.text
            ruby.replace_with(rep)


def kata2hira(str):
    return str.translate(k2h)


def hantei(word):
    text = word.surface
    kana = word.feature.kana
    if text == kana or kana in (None, '', '*') or text in (None, '', '*'):
        return text, False, None
    hira = kata2hira(str(kana))
    if text == hira:
        return text, False, None
    else:
        return text, True, hira


def cut_end(text, hira):
    if text[-1] == hira[-1]:
        for i in range(1, min(len(hira), len(text))):
            if text[-i - 1] != hira[-i - 1]:
                yield text[:-i], hira[:-i]
                yield hira[-i:]
                break
    else:
        yield text, hira


def yomituki(sentence):
    for text, ruby, yomi in map(hantei, tagger(sentence)):
        if ruby:
            yield from cut_end(text, yomi)
        else:
            yield text


def ruby_wrap(text, yomi):
    return f'<ruby>{text}<rp>（</rp><rt>{yomi}</rt><rp>）</rp></ruby>'


def tag_wrap(name, str):
    new_tag = basesoup.new_tag(name)
    new_tag.append(str)
    return new_tag


def ruby_text(text):
    plain = ''
    if len(text) < 1:
        return plain
    yomi = yomituki(text)
    for i in yomi:
        if i in (None, ''):
            continue
        if isinstance(i, str):
            plain += i
        else:
            plain += ruby_wrap(*i)
    return plain


class RubySoup:
    def __init__(self, soup, is_ruby_rp=True) -> None:
        self.is_ruby_rp = is_ruby_rp
        self.ruby_soup(soup)

    def ruby_soup(self, soup):
        for i in soup.children:
            if i is not None and type(i) is NavigableString and i.strip():
                new_i = basesoup.new_tag('temptag')
                # mecab will ignore some whitespace,so we handle it here
                for ele in white_space_re.split(i):
                    if ele.strip():
                        for ele2 in self.ruby_navigablestring(ele):
                            new_i.append(ele2)
                    elif ele:
                        new_i.append(ele)
                i.replace_with(new_i)
                new_i.unwrap()
            elif isinstance(i, Tag) and i.name not in ('ruby', 'rt', 'rp'):
                self.ruby_soup(i)

    def ruby_navigablestring(self, navigablestring):
        string = str(navigablestring)
        yomi = yomituki(string)
        for k, g in groupby(yomi, lambda x: type(x)):
            if k is None:
                continue
            if k == str:
                yield ''.join(g)
            else:
                yield self.ruby_wraps_bs4(g)

    def ruby_wrap_bs4(self, text, yomi):
        ruby_tag = basesoup.new_tag('ruby')
        ruby_tag.append(text)
        rt_tag = tag_wrap('rt', yomi)
        if self.is_ruby_rp:
            ruby_tag.append(tag_wrap('rp', '('))
        ruby_tag.append(rt_tag)
        if self.is_ruby_rp:
            ruby_tag.append(tag_wrap('rp', ')'))
        return ruby_tag

    def ruby_wraps_bs4(self, yomis):
        ruby_tag = basesoup.new_tag("ruby")
        for text, yomi in yomis:
            ruby_tag.append(text)
            rt_tag = tag_wrap('rt', yomi)
            if self.is_ruby_rp:
                ruby_tag.append(tag_wrap('rp', '('))
            ruby_tag.append(rt_tag)
            if self.is_ruby_rp:
                ruby_tag.append(tag_wrap('rp', ')'))
        return ruby_tag
