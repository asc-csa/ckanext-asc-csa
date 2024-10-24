# This class represents a PDF document, which can be re-used for any project.
# Open Data Portal
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, PageBreak
import traceback 

# Constants
CSA_LOGO = 'csa-asc_logo.svg_.png'


# This class defines a PDF document, which supports HTML tags.
# To create the a PDF document, you need to:
#
# 1. Instanciate a PDF document. e.g: pdf_doc = pdf_document('2024 Statistical Report', 'en')
# 2. Create the header. e.g: pdf_doc.createHeader()
# 3. For each chapter:
#       3.1 Add a chapter title. e.g: pdf_doc.addChapter('Scope')
#       3.2 Add each paragraph of the chapter. e.g: pdf_doc.addParagraph('This document is the ...')
#       3.3 Add the images at the appropriate place in the document e.g: pdf_doc.addImage('abc.png', 'System Overview')
# 4. You can add page break between chapter. e.g: pdf_doc.addPageBreak()
# 5. Add the footer. e.g: pdf_doc.createFooter('Please contact the CSA for any question.')
# 6. Saves the PDF document. e.g: pdf_doc.save()
#
# @author Emiline Filion - Canadian Space Agency
#
class pdf_document:
    
    # Default constructor.
    # Params:
    #     title: Document main title (str)
    #     language: 'en' or 'fr' (str)
    def __init__(self, title, language):
        
        # Set properties
        self.title = title
        self.language = language
        self.nb_images = 0
        
        # Set the filename
        day = str(datetime.now().day)
        month = str(datetime.now().month)
        year = str(datetime.now().year)
        self.filename = title + '-' + language + '-' + year + '-' + month + '-' + day + '.pdf'

        # Create the PDF template
        self.pdf_document = SimpleDocTemplate(self.filename, pagesize=letter, rightMargin=1*inch, leftMargin=1*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
        self.styles = getSampleStyleSheet()
        self.document_content = []
        self.title_spacer = Spacer(1, 0.02*inch)


    # Creates the document header at the top
    def createHeader(self):
        
        self.document_content.append(Image(CSA_LOGO, 40, 40, hAlign="LEFT"))
        self.document_content.append(self.title_spacer)
        self.document_content.append(Paragraph("<p>&nbsp;</p><p>&nbsp;</p>", self.styles["Normal"]))
        self.document_content.append(Paragraph("<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>", self.styles["Normal"]))
        self.document_content.append(Paragraph(self.title, self.styles['Title']))
        self.document_content.append(self.title_spacer)
        self.document_content.append(Paragraph("<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>", self.styles["Normal"]))
        self.addSeparationBlock()
    
    
    # Adds a chapter title to the PDF document.
    # Params:
    #     chapter_title: paragraph title (str)
    def addChapter(self, chapter_title):
        
        self.document_content.append(Paragraph("<b><u>" + chapter_title + "</u></b>", self.styles["Normal"]))
        #self.document_content.append(self.title_spacer)
        self.document_content.append(Paragraph("<p>&nbsp;</p>", self.styles["Normal"]))
    
    
    # Adds an paragraph to the PDF document.
    # Params:
    #     content: paragraph content (str)
    def addParagraph(self, content):
        
        self.document_content.append(Paragraph("<p>" + content + "</p>", self.styles["Normal"]))
    
    
    # Adds an image (figure) to the PDF document.
    # Params:
    #     image_file_name: full path and filename of the image to add (str)
    #     image_title: title that shows up below the image (str)
    def addImage(self, image_file_name, image_title):
        
        self.nb_images = self.nb_images + 1
        self.document_content.append(Image(image_file_name,width=4*inch,height=4*inch,kind='proportional'))
        self.styles['Heading5'].alignment = 1
        self.document_content.append(Paragraph("Figure " + str(self.nb_images) + " - " + image_title, self.styles['Heading5']))
    
    
    # Adds an empty line to the PDF document.
    def addEmptyLine(self):
        
        self.document_content.append(Paragraph("<p>&nbsp;</p>", self.styles["Normal"]))
    
    
    # Adds a separation block to the PDF document, which consists of 3 empty lines.
    def addSeparationBlock(self):
        
        self.document_content.append(Paragraph("<p>&nbsp;</p>", self.styles["Normal"]))
        self.document_content.append(self.title_spacer)
        self.document_content.append(Paragraph("<p>&nbsp;</p><p>&nbsp;</p>", self.styles["Normal"]))

    
    # Adds a page break to the PDF document. This is useful to separate two chapters.
    def addPageBreak(self):
        
        self.document_content.append(PageBreak())
    
    
    # Creates the document footer
    # Params:
    #     end_note: content of the footer (str)
    def createFooter(self, end_note):
        
        self.document_content.append(self.title_spacer)
        self.document_content.append(Paragraph(self.title, self.styles['Normal']))
        self.document_content.append(end_note)
        self.document_content.append(self.title_spacer)    
    
    
    # Saves the PDF document to disk
    def save(self):
        
        # Save the PDF document
        try:
            self.pdf_document.build(self.document_content)
            print("PDF report saved to disk: " + self.filename + "\n")  
        except:
            print("ERROR: Unable to save the PDF report to disk: " + self.filename + "\n") 
            #traceback.print_exc() 
