"""
XPdf: A very fast pdf text & images extraction class, that uses the xpdf c++ library.

    Author: Iliass Benali

    licence: GPL v3.0

xpdf (c++):
----------
    @Copyright 2021 Glyph & Cog, LLC

    version: 4.03 windows.
"""
import os
import re
import subprocess
import sys
from pdftextract.utils import cfg, TableMiner

class XPdf:
    """A convenient wrapper of the xpdf c++ library.
    
    Provide very fast text & also images extraction methods.
    It also has (beta) support for tables extraction.

    Parameters:
    -----
    @pdf_file (str): path to the pdf file

    @mode (str): change the extraction mode when using bracket, if table trys to extract the tables

        >>pdf = Xpdf(mode='table')
        >>pdf[1] -> will get the seconde page while trying to parse tables from it

    @encoding (str): encoding of the pdf file, [default: UTF-8]

    """
    def __init__(self, pdf_file:str, mode="text", encoding="UTF-8"):
        self.pdf_file = pdf_file
        self.enc = encoding
        assert mode in {"text", "table"}, "Mode needs to be one of: 'text', 'table'"
        self.mode = mode

    def _run_cmd(self, cmd:list) -> subprocess.CompletedProcess:
        """excute the args in cmd
            @cmd: a list of [script path, *args]
        returns: a process of subprocess"""
        assert isinstance(cmd, list), "cmd needs to be a list of args"
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _get_out(self, proc) -> str:
        """decodes the output of the called process to str"""
        return proc.stdout.decode(self.enc)

    def _check_err(self, proc):
        """check if theres an error based on return code"""
        err = proc.returncode
        if not err:
            return
        if err in cfg.ERR:
            raise TypeError(cfg.ERR[err])
        else:
            raise Exception(err)

    def split_pages(self, pdf_text=str, lines_too=False) -> dict:
        """split extracted text into individual pages

        Parameters:
        -----------
        @pdf_text: pdf plain text extracted by to_text method

        @lines_too: if true split each page into lines

        Returns:
        -------
        a dict where keys are numbers of pages (start:1) and keys are list of lines if as_lines else strings
        """
        eop, eol = cfg.EOP, cfg.EOL
        assert isinstance(pdf_text, str) and eop in pdf_text, "pdf_text needs to be a string that has been converted by this class"
        pages = [page for page in pdf_text.split(eop) if page]
        if lines_too:
            pages = {i:[line for line in page.split(eol)] for i,page in enumerate(pages, 1)}
        else:
            pages = {i:page for i,page in enumerate(pages, 1)}
        return pages

    def to_text(self, out_fname:str="", return_str=True, just_one:int=0, start:int=None, stop:int=None,
            keep_layout=True, table=False, simple=False, **kws):
        """
        Extract plain text from a pdf file.

        Parameters:
        ----------
        @out_fname <path>: a .txt where the extracted text will be saved, if left empty uses the pdf_file path.

        @return_str: if True return the text.
            N.B: if the out_fname is specified return_str is True the text will be writing to the file and not returned!

        @just_one <page_num>: if not 0 will extract from the page==just_one.

        @start: the first of page to convert

        @stop: the last page to convert

        @keep_layout: Maintain (as best as possible) the original physical layout of the text

        @simple: trys to maintai horizontal spacing, but it will only work properly with a single column of text.

        @table: trys to keep the rows and columns aligned (at the expense of inserting extra whitespace) 

        @kws: other possible keywords arguments:

            @omit_pn (bool): if True will try to omit the page number at the bottom
                lineprinter: if True the page is broken into a grid, and characters are placed into that grid then
                            will attempt to extract the text based on spacing
            
            @raw (bool):  if True Keep the text in content stream order
            
            @clip (bool): if true Text which is hidden because of clipping is removed before doing
                      layout, and then added back in
            
            margin+[l|r|t|b] (int): specify the margin in (marginl:left, marginr:right, ..t:top, ..b:bottom) in points
                                if text in that margin will be ignored | e.g marginb:10 = ignore text in 10points from bottom
            
            @opw, @upw (int): owner, user pdf password respectivly
        
        Returns:
        --------
            if return_str: will return the extracted text 
            else: will return None & instead write it to a '.txt' file   
        """
        pdf_file = os.path.abspath(self.pdf_file)
        script = cfg.this_path("xpdf", "pdftotext.exe")
        if out_fname:
            return_str = False
        if keep_layout:
            simple = not simple
        if just_one:
            start, stop = just_one, just_one
        if kws.get("omit_pn", False) and "marginb" not in kws:
            del kws['omit_pn']
            kws['marginb'] = 50
        args = {
            "f":start,
            "l":stop,
            "layout":keep_layout,
            "simple2":simple,
            "table":table,
            "enc":self.enc,
        }
        args.update(kws)
        args_sep = "\t"

        args = cfg.make_args(args, args_sep)
        cmd = script + args_sep.join([args, pdf_file])
        if out_fname:
            out_fname = os.path.abspath(out_fname)
            cmd += args_sep + out_fname
        if return_str:
            cmd += args_sep + "-"      
        cmd = cmd.split(args_sep)

        proc = self._run_cmd(cmd)
        out = self._get_out(proc)
        self._check_err(proc)
        if return_str:
            return out

    @property
    def info(self) -> dict:
        """Get information on the pdf file and return it as a dictionary where keys are:

        Title, Creator, Producer, CreationDate, ModDate, Tagged, Form, 
        Pages, Encrypted, Page size, File size, Optimized, PDF version
        """
        script = cfg.this_path("xpdf", "pdfinfo.exe")
        cmd = [script, self.pdf_file]
        res = self._run_cmd(cmd)
        infos = [line.strip('\r') for line in res.stdout.decode().split("\n") if line]
        pdf_infos = {}
        for line in infos:
            k, v = re.split(r":", line, maxsplit=1)
            k, v = k.strip(), v.strip()
            if v.isdigit():
                v = int(v)
            pdf_infos[k] = v
        return pdf_infos

    @property
    def table(self):
        """returns XPdf object with 'table' mode"""
        return XPdf(self.pdf_file, mode="table")

    def get_imgs(self, outdir:str="pdf_img", just_one:int=0, start:int=0, jpg=True, mkdir=True,
                raw=False, summary=False, **kws):
        """
        Extract images for each page in pdf_file and output them into a directory.

        Parameters:
        ----------
        @outdir: as 'directory/root-name' where the extracted images will be saved as "outdir-nn.xx",
                where nn is the image number and  xx  is  the image type (.ppm, .pgm, .pbm, .jpg).
                WARNING: Any  rotation,  clipping,  color inversion, etc is ignored.

        @just_one: if not 0 will only get images from page == just_one.

        @start: the first page to be converted [start_index=1]

        @stop: the last page to be converted

        @jpg: Normally, all images are written as PBM (for monochrome images),
                PGM (for grayscale images), or PPM  (for  color  images)  files.
                With  this option images in DCT format are saved as JPEG files
                WARNING: Inline images are always saved in PBM/PGM/PPM format!

        @mkdir: if outdir doesn't exist create it.

        @raw: Write all images in PDF-native formats maybe usefull as input to a tool that generates PDF files.

        @summary: Write a one-line summary to stdout for each image -> [fname, page_num, W & H, resolution, color, bits per component]

        @kws: other keywords args:
                opw, upw: owner, user pdf password

        Returns:
        --------
        None, output image files to the outdir
        """
        script = cfg.this_path("xpdf", "pdfimages.exe")
        pdf_file = os.path.abspath(self.pdf_file)
        outdir = os.path.abspath(outdir)
        dirname = os.path.dirname(outdir)
        if not os.path.exists(dirname) and mkdir:
            os.mkdir(dirname)
        if just_one:
            start, stop = just_one, just_one
        args = {
            "f":start,
            "l":stop,
            "j":jpg,
            "raw":raw,
            "list":summary
        }
        args.update(kws)
        args_sep = '\t'
        args = cfg.make_args(args)
        cmd = script + args_sep.join([args, pdf_file, outdir])
        cmd = cmd.split(args_sep)
        proc = self._run_cmd(cmd)
        self._check_err(proc)
        if summary:
            out = self._get_out(proc)
            print(out)

    def __len__(self):
        return self.info['Pages']

    def __getitem__(self, page_ind):
        mode = self.mode
        opt = {
                "text":{},
                "table":{"table":True, "lineprinter":True}
                }
        kws = opt[mode]
        if type(page_ind) is int:
            item = self.to_text(just_one=page_ind+1, **kws)
        else:
            cvt = lambda x: x + 1 if type(x) is int else 0
            item = self.to_text(start=cvt(page_ind.start), 
                                stop=cvt(page_ind.stop) - 1, **kws)
        return item if mode == "text" else TableMiner(item).mine()


if __name__ == "__main__":
    file_path = sys.argv[1] # get the file path
    pdf = XPdf(file_path) # initializing the class
    npages = pdf.info['Pages']
    print("[INFO]", "Extracting text from {!r} that has {} pages ..".format(file_path, npages))
    cfg.timeit() # start the timer
    txt = pdf.to_text() # extrating the texts
    t = cfg.timeit() # end timer
    print("[DONE]", "Text extracted in {} second!".format(t))
    print("Text:", "-"*20, sep="\n")
    print(txt) # display the text string
