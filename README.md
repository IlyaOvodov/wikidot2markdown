# Wikikdot to Markdown Convertor

Command line convertor from [Wikidot syntax](http://www.wikidot.com/doc:quick-reference) to
[Markdown syntax](http://daringfireball.net/projects/markdown/syntax).

Most format features are translated to standard Markdown. Some specific nonstandard
format features are converted to [Obsidian](https://obsidian.md/) markdown extensions.   

Inspired by https://github.com/vLj2/wikidot-to-markdown.

## Usage
To convert a single file:

    python3 convert.py --input|-i INPUT_FILE [--output|-o OUTPUT_DIR] [--overwrite|-w]

To convert all files in an input directory: 

    python3 convert.py --input|-i INPUT_DIRECTORY [--mask|-m MASK] [--output|-o OUTPUT_DIR] [--overwrite|-w]

Arguments:

`--input INPUT` or `-i INPUT`: path to file or directory to be converted. If it contains spaces,
it should be included in quotes: `-i "C:\My documents\some wikidot file.txt"`. Required.

If `INPUT` is file, this file will be converted and placed to `OUTPUT_DIR`.
If `INPUT` is directory, all files in this directory and all its subdirectories, that fits `MASK`,
will be converted and placed to `OUTPUT_DIR`.

The converted file(s) has the same name(s) as input file(s) and ".md" extension. 

`--output OUTPUT_DIR` or `-o OUTPUT_DIR`: directory where converted file will be placed.
Optional. Default is "output" subdirectory. If directory does not exist, it is created.

`--mask MASK` or `-m MASK`: mask to select files to convert. Is used only if `INPUT` is directory.
Optional. Default is ".txt".

`--overwrite` or `-w`: allows rewriting existing output file. If not specified,
and the output file already exists, program stops with error.

Be aware of that while input directory is searched recursively, output files are placed in
`OUTPUT_DIR` without subdirectories, that can cause conflicts.

## Supported Format Features

The following features can be converted:

- ### headers of up to 4 levels

- plain formatting of **bold**, *italic*, ***bold italic***, <u>underlined</u>, ~~strikethrough~~, `monospace`, <sup>super-</sup> and <sub>sub-</sub> script text.

- newlines are preserved like in Wikidot:
  
Some text  
new line in the same paragraph

New paragraph

- simple hyperlinks (like https://github.com/IlyaOvodov/wikidot2markdown) and hyperlinks with text
[like this](https://github.com/IlyaOvodov/wikidot2markdown)

- links to other documents like [[README]] or [[README | read me]]

  NB: it uses Wikiref syntax used by Obsidian.

- anchors and links to anchors. Anchors are not standard Markdown features and here they 
are implemented in [Obsidian](https:://obsidian.md)'s manner like <sup>^myanchor</sup> at the end of paragraph.

- inline `code`

- code blocks, including language specification:
```Python
def f(a):
    return a+1
```

- math formulae: inline ($\alpha=1$) and block formulae, including tags:

$$ \tag{eq1}
|x| = 123
$$

- references to equations ([[^eq1 | 1]])

NB: equation auto-numbering is not supported. All equation tags are converted to anchors 
  named as eq<original tag>.

- pictures defined by URL:
  
  ![|](https://upload.wikimedia.org/wikipedia/commons/a/af/DBSCAN-Illustration.svg)

- pictures from local file:

![[sample.jpg]]

  NB: it uses Wikiref syntax used by Obsidian.

- tables:

| Head1 | Head2 | Head2 |
| --- | --- | --- |
| X | 0 |   |
| ~~X~~ | ~~X~~ | ~~X~~ |
| 0 |   | 0  |

NB: Wikidot allows table row to have more cells than header. In Markdown extra cells are not displayed.
This situation is not handled in any way during conversion.