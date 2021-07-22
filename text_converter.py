#!/usr/bin/env python
# -*- encoding: UTF8 -*-

import re
import uuid

protocol_re = r"http|https|ftp"
username_password_re = r"[a-zA-Z0-9\.\-]+(?:\:[a-zA-Z0-9\.&amp;%\$\-]+)*@"
ip_re = r"(?:25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\." \
        r"(?:25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\." \
        r"(?:25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\." \
        r"(?:25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])"
addr_re = r"(?:[a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(?:com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2})"
port_re = r"\:[0-9]+"
page_re = r"(?:/(?:$|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*"
url_re = fr"(?:{protocol_re})\://(?:{username_password_re})?(?:{ip_re}|localhost|{addr_re})(?:{port_re})?(?:{page_re})[/]?"

uuid_re = r"[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}"
preserved_block_re = uuid_re


class TextConverter(object):
    def __init__(self):
        # each regex defines 1 group: text block to be preserved from conversion
        self.blocks_to_preserve = list()
        # dict: { search_regex : replacement | (replacement, repeat count) }
        self.regex_replacements = dict()

    def convert(self, text, filename):
        preserved_blocks = dict()
        for expr in self.blocks_to_preserve:
            blocks_found  = re.findall(re.compile("("+expr+")",re.MULTILINE), text)
            for block in blocks_found:
                assert len(block)==2, f"incorrect expr {expr}\nresults in {len(block)} blocks"
                tmp_hash = str(uuid.uuid4())
                new_text = block[0].replace(block[1], tmp_hash, 1)
                text = text.replace(block[0], new_text, 1) # replace code block with a hash - to fill it in later
                preserved_blocks[tmp_hash] = block[1]

        # search for any of the simpler replacements in the dictionary regex_replacements
        for s_reg, r_reg_x in self.regex_replacements.items():
            r_reg, n = (r_reg_x[0], r_reg_x[1]) if isinstance(r_reg_x, tuple) else (r_reg_x, 1)
            for i in range(n):
                text = re.sub(re.compile(s_reg,re.MULTILINE),r_reg,text)

        # search for unhandled tags and state them
        for unhandled_tag in re.finditer(r"\[\[/([\s\S ]*?)\]\]", text):
            print("Found an unhandled tag: {} in {}: {}".format(unhandled_tag.group(1), filename, unhandled_tag.group(0)))

        # now we substitute back our code blocks
        for tmp_hash, code in preserved_blocks.items():
            text = text.replace(tmp_hash, code, 1)
        return text


class WikidotToMarkdown(TextConverter):
    def __init__(self):
        # each regex defines 1 group: text block to be preserved from conversion
        self.blocks_to_preserve = [
            '^\[\[code(?: +type="(?:[\S]+)")?\]\]([\s\S]*?)^\[\[/code\]\]\r?$',  # code
            r'\[\[\$ *([\S\t ]*?) *\$\]\]',  # math [[$ ... $]]
            r'^\[\[math(?: *\w*)\]\]([\s\S]*?)^\[\[/math\]\]\r?$',  # math [[math]]/n.../n[[/math]]
        ]


        self.regex_replacements = {
            r'^\+ (.*?\w.*?)$': r"# \1",  # headings + -> #
            r'^\+\+ (.*?\w.*?)$': r"## \1",
            r'^\+\+\+ (.*?\w.*?)$': r"### \1",
            r'^\+\+\+\+ (.*?\w.*?)$': r"#### \1",

            r'([^:])//(.*?\S.*?)//': r'\1*\2*',  # italics //...// -> _..._
            r'__(.*?\w.*?)__': r'<u>\1</u>',  # underlining __...__ -> <u>...</u>
            r'--(.*?\w.*?)--': r'~~\1~~',  # strikeout __...__ -> <u>...</u>
            r'{{(.*?\S.*?)}}': r'`\1`',  # inline monospaced text {{...}} -> `...`
            r'\^\^(.*?\S.*?)\^\^': r'<sup>\1</sup>',  # ^^...^^ -> <sup>...</sup>
            r',,(.*?\S.*?),,': r'<sub>\1</sub>',  # ,,...,, -> <sub>...</sub>

            r'^\[\[collapsible *show *= *"(.*?)".*?\]\]': r'<details style="display: inline;"><summary>\1</summary>',
            r'^\[\[/collapsible\]\]': '</details>',

            r'(?<=\S)(?: *)(\r?)$(?!\s+?$)': r"  \1",  # newline

            r'^\[\[code(?: +type="([\S]+)")?\]\](' + preserved_block_re + ')\[\[/code\]\]\s*?$': r'```\1\2```',
            # [[code type="..."]] ... [[/code]]

            r'\[\[\$ *([\S\t ]*?) *\$\]\]': r'$\1$',  # inline math [[$ ... $]] -> $...$
            r'^\[\[math\]\](' + preserved_block_re + ')\[\[/math\]\]\s*?$': r'$$\1$$',
            # math [[math]]/n.../n[[/math]] -> $$/n.../n$$
            r'^\[\[math(?: +(?:eq?)?(\w+) *)]\](' + preserved_block_re + ')\[\[/math\]\]\s*?$': r'^eq\1\n$$ \\tag {eq\1}\2$$',
            # math [[math]]/n.../n[[/math]] -> $$/n.../n$$
            r'\[\[eref(?: +(?:eq?)?(\w+) *)\]\]': r'[[#^eq\1 | \1]]',

            r'\[\*?(' + url_re + r') ([^\]]*)\]': r'[\2](\1)',  # [*http://url desc] -> [desc](url)
            r'\[\[(?:=|<|>|f<|f>)?image (' + url_re + r')(?: alt="(?P<alt>[^\]]*)"| (?:width|height)="(?P<wh>[0-9]*)px"| [a-z]*=".*?")*\]\]': r"![\g<alt>|\g<wh>](\1)",
            # [[...image http://url alt="desc"]] -> ![desc](url)
            r'\[\[(?:=|<|>|f<|f>)?image ([\w\%\.\-]*)(?: alt="(?P<alt>[^\]]*)"| (?:width|height)="(?P<wh>[0-9]*)px"| [a-z]*=".*?")*\]\]': r"![[\1|\g<wh>]]",
            # [[...image file.png alt="desc"]] -> ![[file.png|size]]

            r'\[\[\[(?P<page>[\w\%\.\-\ ]+)?(?:#(?P<anc>[\w\%\.\-]+))(?P<desc> *\| *.*?)?\]\]\]': r'[[\g<page>#^\g<anc>\g<desc>]]', ## ref [[[page#anc | desc]]] -> [[page#^anc | desc]]
            r'\[\[\[(?P<page>[\w\%\.\-\ ]+)(?P<desc> *\| *.*?)?\]\]\]': r'[[\g<page>\g<desc>]]',  ## ref [[[page | desc]]] -> [[page | desc]]
            r'\[\[\[(?P<page>[\w\%\.\-\ ]+)?(?:#(?P<anc>[\w\%\.\-]+))(?P<desc> *.*?)?\]\]\]': r'[[\g<page>#^\g<anc> |\g<desc>]]',
            ## ref [[[page#anc desc]]] -> [[page#^anc | desc]]
            r'\[\[\[(?P<page>[\w\%\.\-\ ]+)(?P<desc> *.*?)?\]\]\]': r'[[\g<page> |\g<desc>]]',
            ## ref [[[page desc]]] -> [[page | desc]]

            r'\[#(?P<anc>[\w\%\.\-]+) *\]': r'[[#^\g<anc>]]',                            ## ref [#anc]      -> [[#^anc]]
            r'\[#(?P<anc>[\w\%\.\-]+) *(?P<desc>\S.*?)?\]': r'[[#^\g<anc> | \g<desc>]]', ## ref [#anc desc] -> [[#^anc | desc]]
            # this must go after [[[page#anc | desc]]] -> ...
            r'^(#+ .*)\[\[# ([\w\%\.\-]+)\]\]([\s\S]*?)(?: *)(\r?)$': r'\1\3 ^\2\4',  # Anchor at header #...[[# anc]]... -> # ...... ^anc
            r'^(.*)\[\[# ([\w\%\.\-]+)\]\]([\s\S]*?)(?: *)(\r?)$(?=\s+?$)': r'\1\3 ^\2\4',  # Anchor to end of paragraph ...[[# anc]]... -> ...... ^anc

            # tables (up to 20 cols)
            r'^(\|\|.+?)\|\|': (r'\1|', 20),  # || ... || -> || ... |
            r'^\|\|(.+?)\|(.+?)(?: *)(\r?)$': r'|\1|\2\3',  # || ... |  -> | ... |
            r'^([^\|].*?)$\n^(\|.+?\|.+)(\r?)$': r'\1\n\2\3\n@fgsdfgtrgfgcbjkrhdscjdkerui4mds@\2\3',  # copy header line
            r'^(@fgsdfgtrgfgcbjkrhdscjdkerui4mds@(\| --- )*)\|.*?\|': (r'\1| --- |', 20),
            # replace copied to | --- | ...
            r'^(.*\S.*?)(?: *)(\r?)$\n(^\|.+$\n^@fgsdfgtrgfgcbjkrhdscjdkerui4mds@(\|( --- \|)+.*?)$)': r'\1\2\n\2\n\3',
            # insert newline before tables
            r'^@fgsdfgtrgfgcbjkrhdscjdkerui4mds@(\|( --- \|)+.*?)$': r'\1',  # remove marker

        }
