# All gem related functions go here
import time
import datetime
import tabula
import csv
from xlwt import Workbook, easyxf, Font
from xlrd import open_workbook
from xlutils.copy import copy
import os
from os import listdir
from os.path import isfile, join
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

def process_pdf_to_xls(request):
    dirname = os.getcwd()
    mediapath = os.path.join(dirname, "media/")
    outputpath = os.path.join(dirname, "media/output/")
    attachmentpath = os.path.join(dirname, "media/attachments/")
    rownum = 1
    bidnum = bidend = ttlqty = item =  officer = address = location = organisation = pincode = 'N/A'

    onlyfiles = [f for f in listdir(attachmentpath) if isfile(join(attachmentpath, f))]


    rb = open_workbook(mediapath + 'GeM Bid Format.xls', formatting_info=True)
    wb = copy(rb)
    sheet1 = wb.get_sheet(0)


    for file in onlyfiles:
        if file[-4:] == '.pdf':
            rownum += 1
            newfile = file
            print('Extracting data from ' + newfile + '...')

            path = attachmentpath + file

            tabula.io.convert_into(path, pages = "all", output_format='csv', output_path= mediapath + 'result.csv')

            with open(mediapath + 'result.csv') as csvfile:
                rows = []
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    rows.append(row)
                    

                j=0
                for keyword in rows:
                    for key in keyword:
                        try:
                            if key == 'Bid End Date/Time':
                                bidend = keyword[1]
                            elif key == 'Total Quantity':
                                ttlqty = keyword[1]
                            elif key == 'Item Category':
                                item = keyword[1]
                            elif key == 'Consignee/Reporting\nOfficer':
                                newkeyword = rows[rows.index(keyword)+1]
                                officer = newkeyword[1]
                                address = newkeyword[2]
                                pincode = address[:6]

                            elif key == 'Organisation Name':
                                organisation = keyword[1]

                            elif key == 'Consignee/Reporting':
                                newkeyword = rows[rows.index(keyword)+2]
                                officer = newkeyword[1]
                                address = newkeyword[2]
                                pincode = address[:6]
                                j = 3
                                
                                
                                while rows[rows.index(keyword)+j]:
                                    newkeyword = rows[rows.index(keyword)+j]
                                    if newkeyword[0] == '':
                                        officer += newkeyword[1]
                                        address += newkeyword[2]
                                        pincode = address[:6]
                                    else:
                                        break
                                    j += 1
                        except IndexError:
                            break




            fp = open(path, 'rb')

            parser = PDFParser(fp)
            doc = PDFDocument(parser)
            parser.set_document(doc)
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            laparams.char_margin = 1.0
            laparams.word_margin = 1.0
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            extracted_text = ''

            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
                layout = device.get_result()
                for lt_obj in layout:
                    if isinstance(lt_obj, LTTextBox):
                        extracted_text += lt_obj.get_text()

            extracted_text = extracted_text.split()
            

            for i in extracted_text:
                if i == 'Dated:':
                    bidnum = extracted_text[extracted_text.index(i)-1]
                    dated = extracted_text[extracted_text.index(i)+1]
                elif i == 'Consignees/Reporting':
                    newkeyword = extracted_text[extracted_text.index(i)+3]
                    if newkeyword == 'Quantity':
                        newkeyword = extracted_text[extracted_text.index(i)+4]
                        if newkeyword == 'S.No.':
                            startpoint = extracted_text.index(i)+8
                if i == 'Address':
                    if extracted_text[extracted_text.index(i)+1] == 'Quantity':
                        if extracted_text[extracted_text.index(i)+2] == 'Delivery':
                            endpoint = extracted_text.index(i)

            if officer == 'N/A':
                officer = ''
                for i in extracted_text[startpoint:endpoint]:
                    officer += i + ' '

            

            if pincode == '245101':       
                location = 'Ghazibad' 
            elif pincode == '110075':
                location = 'South West Delhi'
            elif pincode == '110078':
                location = 'West Delhi'
            elif pincode == '110007':
                location = 'North Delhi'
            elif pincode == '110052':
                location = 'North West Delhi'
            elif pincode == '211011':
                location = 'Allahabad'
            elif pincode == '245101':
                location = 'Ghaziabad'
            elif pincode == '110001' or '110055':
                location = 'Central Delhi'
            else:
                location = 'N/A'


            print(f'Info added [SNO.= {rownum-1}]')
            sheet1.write(rownum, 0, rownum - 1)
            sheet1.write(rownum, 1, bidnum)
            sheet1.write(rownum, 2, bidend)
            sheet1.write(rownum, 3, ttlqty)
            sheet1.write(rownum, 4, item)
            sheet1.write(rownum, 5, officer)
            sheet1.write(rownum, 6, address)
            sheet1.write(rownum, 7, datetime.date.today().strftime('%d-%m-%Y'))
            sheet1.write(rownum, 8, location)
            sheet1.write(rownum, 10, organisation)

            bidnum = bidend = ttlqty = item =  officer = address = location = organisation = pincode = 'N/A'


    wb.save(outputpath + 'Bid' + '.xls')
    print()
    print('File created at ' + outputpath + 'Bid.xls')