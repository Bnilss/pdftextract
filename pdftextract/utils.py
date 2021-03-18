import os
import re
import csv
import sys
from time import time

class Config:
    """General configuration class with some usefull methods!"""
    EOL = "\r\n" # end of line char
    EOP = "\x0c" # end of page char
    # a dict of xpdf errors codes and their messages
    ERR = {1:"Error in opening the PDF file: {}",
            2:"Error in opening the OUTPUT file: {}",
            3:"Error related to PDF permession",
            99:"There seems to be an unknown error"}
    TIME = 0

    @staticmethod
    def check_platf():
        """check the platform"""
        platf = sys.platform
        if platf.startswith("win"):
            pass
        else:
            warn = """This plataform is not currently supported, check 'support.txt' file for
            information on how to run this class on other platforms."""
            print(warn)

    @staticmethod
    def timeit() -> float:
        """time a step"""
        st_time = Config.TIME
        if st_time:
            t = time() - st_time
            Config.TIME = 0
            return round(t, 4)
        Config.TIME = time()
        return st_time

    @staticmethod
    def this_path(*args, dir=None) -> str:
        """convert to path from this directory regardless from where the script is called"""
        if dir is None:
            dir = __file__
        dirname = os.path.dirname(dir)
        path = os.path.join(dirname, *args)
        return path

    @staticmethod
    def make_args(args:dict, sep="\t") -> str:
        """make a string of args to be splited and passed to subprocess"""
        cmd = ""
        for name, val in args.items():
            if isinstance(val, bool) and val:
                cmd += "{}-{}".format(sep, name)
            else:
                if val:
                    cmd += "{0}-{1}{0}{2}".format(sep, name, val)
        return cmd

    @staticmethod
    def dir_like(from_, other) -> str:
        """give the dirname if from_ to other"""
        from_ = os.path.dirname(from_)
        return os.path.join(from_, other)

class TableView(dict):
    """class that provides a formated view of table data
    
    Parameters:
    -----------
    @table (dict): a dictionary with 2 keys: headers(1D list of headers) & data(2D list)"""
    def __init__(self, table:dict):
        super().__init__(table)
        assert "headers" in table and "data" in table, "headers & data should be the only keys in table"
        self.table = table
        self.headers = table['headers']
        self.data = table['data']
        self.value = [self.headers] + self.data
        self.ncol = len(self.headers)
        self.nrow = len(self.data)
    
    def to_csv(self, fname:str, sep=","):
        """write the table to a csv file"""
        with open(fname, "w") as f:
            wr = csv.writer(f, delimiter=sep)
            wr.writerow(self['headers'])
            for row in self['data']:
                wr.writerow(row)

    def to_dict(self) -> dict:
        """convert the table back to dict"""
        return dict(self)

    def __repr__(self):
        return f"TableView [headers:{self.ncol}, data:{self.nrow}]"

    def __str__(self):
        tab = self.format_tab(self)
        return tab

    @staticmethod
    def format_tab(table) -> str:
        """format a dict to table
        
        Parameters:
        -----------
        @table (dict): has to have 2 keys: headers(1D list of headers) & data(2D list)
        
        Returns:
        --------
        a formated table (str)"""
        head, dt = table["headers"] ,table['data']
        concat = [head] + dt
        fmt_rows = []
        max_spaces = []
        temp = " | ".join("{{:^{}}}" for _ in range(len(head)))
        for col in zip(*concat):
            max_space = max(map(len, col))
            max_spaces.append(max_space)
        for i, row in enumerate(concat):
            sub_temp = temp.format(*max_spaces)
            fmt_row = sub_temp.format(*row)
            fmt_rows.append(fmt_row)
            if not i:
                sep = "_" * len(fmt_row)
                fmt_rows.append(sep)
        fmt_tab = "\n".join(fmt_rows)
        return fmt_tab


class Tables(list):
    """a list like object that has a txt attribute"""
    def __init__(self, tables:list, txt:str=""):
        super().__init__(tables)
        self.tables = tables
        self.txt = txt

    def __getitem__(self, ind) -> TableView:
        return super().__getitem__(ind)


class TableMiner:
    """Trys to parse tables from raw text extracted by the main class (XPdf)
    
    Parameters:
    -----------
    @text (str): text extracted from pdf by XPdf"""
    def __init__(self, text:str):
        self.text = text
        self.tables = []
        self.ntab = 0

    def mine(self, start_0=False, patience=0, space=3) -> Tables:
        """'Mine' the text string to get the tables in it
        
        Parameters:
        -----------
        @start_0: if true strat the first column at start of the line [default: False]
        
        @patience: how many line to wait before extracting the table [default:0]

        @space: space between words to be consider as a table [default: 3]
        
        Returns:
        --------
        A list of TableViews(dict) classes that have headers and data keys"""
        tables = self.detect_tables(self.text, patience, space)
        self.ntab = len(tables)
        for table in tables.values():
            table = self.parse_table(table, start_0, space)
            if table.nrow > 0:
                self.tables.append(table)
        return Tables(self.tables, self.text)

    @staticmethod
    def detect_tables(txt:str, patience:int=0, space:int=3):
        """trys to detect tables in text file"""
        txts = txt.splitlines(False)
        tables = {}
        table = []
        found = False
        ind = 0
        for txt in (txts):
            if not re.sub(r"[^a-z0-9]+", "", txt, flags=re.I):
                continue
            if not found and table and ind > patience:
                tables[len(tables)] = table
                table = []
                ind = 0
            m = re.search(r".+?[ ]{" + str(space) + r",}[a-z0-9]", txt, flags=re.M|re.I)
            if m:
                found = True
                table.append(txt)
                ind = 0
            else:
                found = False
                ind += 1
        return tables

    @staticmethod
    def parse_table(table:list, start_0:int=False, space:int=3):
        headers = [head for head in re.split('[ ]{' + str(space) + ',}', table[0]) if head.strip()]
        split_pts = [match(header, table[0]) for header in headers]
        if start_0 :
            split_pts[0] = 0
        fmt_table = []
        for row in table[1:]:
            fmt_row = []
            for i in range(0, len(split_pts) - 1):
                st, ed = split_pts[i], split_pts[i+1]
                col = row[st:ed].strip()
                fmt_row.append(col)
            if len(split_pts) > 1:
                fmt_row.append(row[ed:].strip())
                fmt_table.append(fmt_row)
        return TableView({"headers":headers, "data":fmt_table})

    @staticmethod
    def format(table):
        return TableView.format_tab(table)


def match(pat, string):
    l = len(pat)
    for i in range(len(string)):
        sub_str = string[i:i+l]
        if sub_str == pat:
            return i


cfg = Config()
cfg.check_platf()