#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
from pathlib import Path
import text_converter

class ConversionController(object):
    def __init__(self, args):
        self.input = Path(args.input)
        self.output_directory = Path(args.output)
        self.mask = args.mask
        self.converter = text_converter.WikidotToMarkdown()
        self.overwrite = args.overwrite
        self.output_directory.mkdir(exist_ok=True)


    def process(self):
        if self.input.is_file():
            self.convert_file(self.input)
        else:
            self.process_dir()

    def process_dir(self):
        files = list(self.input.glob('**/' + self.mask))  # list is required mo make a snapshot
        for f in files:
            self.convert_file(f)

    def __output_file(self, input_file):
        return (self.output_directory / input_file.name).with_suffix('.md')

    def convert_file(self, input_file):
        out_file = self.__output_file(input_file)
        if not self.overwrite:
            assert not out_file.is_file(),  f"file '{out_file}' already exists"
        text = input_file.read_text(encoding='utf-8')
        complete_text = self.converter.convert(text, input_file)
        out_file.write_text(complete_text, encoding='utf-8')


def main():
    """ Main function called to start the conversion."""
    parser = argparse.ArgumentParser(description='Wikidot to markdown converter')
    parser.add_argument('--input', '-i', required=True, help="input file or dir")
    parser.add_argument('--mask', '-m', default="*.txt", help="file mask for dir processing")
    parser.add_argument('--output', '-o', default="output", help="output dir")
    parser.add_argument('--overwrite', '-w', action='store_true', help="overwrite existing files")
    args = parser.parse_args()

    converter = ConversionController(args)
    converter.process()


if __name__ == '__main__':
    main()
