# PdfTextract
A very fast and efficient python PDF text & images extractor that uses the xpdf c++ library.

## Features

- Several times fatser then any python based pdf text extractor
- very easy and simple to use
- Extract text while maintaining original document layout
- Trys to automaticaly extract tables if they exist (still in beta)
- No local server setup required
- No dependencies needed

## Instalation

Install via PyPi:
```python
pip install pdftextract
```
or via github:
1. first clone the repo:
```python
git clone https://github.com/Bnilss/pdftextract.git
```
2. then run
```python
python setup.py install
```

## Usage

1. **Importing the package**
```python
from pdftextract import XPdf

file_path = "examples/pubmed_example.pdf"
pdf = XPdf(file_path)
```

2. **Get the PDF meta-data**
```python
print(pdf.info) # this will return a dict of pdf metadata (author, size, pages..)
# to get the number of pages for example
print(pdf.info['Pages'])
```

3. **Extracting text from all pages in a PDF and return it as string**
```python
txt = pdf.to_text()
print(txt)
```

4. **Extracting a single page only, to get the 3rd page for example**
```python
# we can extrat using the previous method (start_index=1)
txt = pdf.to_text(just_one=3)
# or use the bracket notation (start_index=0)
txt = pdf[2]
```

5. **Extracting text from a single page (page 7) and saving it to .txt file**
```python
pdf.to_text("page7.txt", just_one=7)
```

6. **Extracting text from page 1 to 5**
```python
txt = pdf.to_text(start=1, end=5)
# or
txt = pdf[:5]
```

7. **Extract tables**
```python
pdf = XPdf("examples/table_sample.pdf")
txt = pdf.to_text(table=True)
# the use a regex or something to parse the text ..
# or try automatic paring (still in beta)
tables = pdf.table[:]
print(len(tables)) # 3
print(tables[0]) # print formated content of table 1
#Number of Coils | Number of Paperclips
#______________________________________
#       5        |       3, 5, 4
#      10        |       7, 8, 6
#      15        |      11, 10, 12
#      20        |      15, 13, 14
table1_data = tables[0].data # will return all rows in table except headers
```

## OS support
by default the package support windows.

to use it in linux or mac:
1. download xpdf files for [linux](https://dl.xpdfreader.com/xpdf-tools-linux-4.03.tar.gz) or [mac](https://dl.xpdfreader.com/xpdf-tools-mac-4.03.tar.gz)
2. extract the files in got to os version (32/64 bit)
3. copy these files: pdftotext, pdfinfo, pdfimages
4. Got to the packages-directory/pdftextract/xpdf
5. past the file in that directory


## Credits
- [xpdf c++](https://www.xpdfreader.com/) by Derek Noonburg

## License
```pdftextract``` is licensed under the GNU General Public License (GPL), version 3.