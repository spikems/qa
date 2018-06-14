#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


from os.path import join, dirname, abspath
import os
import logging
import xlrd
import sys
import numpy as np
import xlsxwriter
from optparse import OptionParser




class XLSDeal():
    """
    Dump data from definite columns in a xls/xlsx file.

    """
    def __init__(self):
        pass
   
    def toXlsFile(self, lText, fname):
        workbook = xlsxwriter.Workbook(fname, {'strings_to_urls': False})
        sheet = workbook.add_worksheet('predict')
 
        
        iRow = 0
        for line in lText:
            lItems = line.split('\t')
            for iCol in range(len(lItems)):
                sheet.write(iRow, iCol, lItems[iCol].decode('utf-8'))
            iRow = iRow + 1
    
        workbook.close()

    def XlsToList(self, fname, islower = False):

        xl_workbook = xlrd.open_workbook(fname, encoding_override="utf-8")
        xl_sheet = xl_workbook.sheet_by_index(0)
        lRows = []
        # all values, iterating through rows and columns
        num_cols = xl_sheet.ncols   # Number of columns
        for row_idx in range(0, xl_sheet.nrows):    # Iterate through rows
            arow = ''
            for col in range(xl_sheet.ncols): 
                val = xl_sheet.cell_value(row_idx, col)
                if type(val) == unicode:
                    val = val.encode('utf-8')
                if type(val) == str:
                    val = val.replace('\r','').replace('\n','').replace('\t','')
                    if islower:
                        val = val.lower()
                if type(val) == float or type(val) == int:
                    val = str(int(val)).lower()
                if col == 0:
                    arow = val
                else:
                    arow = '%s\t%s' % (arow, val)
            lRows.append(arow)
        return lRows


if __name__=='__main__':
    XLSDeal().toXlsFile(['你好\t中国', '世界\t你好'], 'test')
 #   print (XLSDeal().XlsToList('test.xlsx'))
    print XLSDeal().XlsToList('test.xlsx')[0]
