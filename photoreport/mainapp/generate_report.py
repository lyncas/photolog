from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.shared import Inches
import os
from django.conf import settings


class DocumentGenerator(object):

    def create(self, project):
        document = Document()
        obj_style = document.styles['Normal']
        obj_font = obj_style.font
        obj_font.size = Pt(12)
        obj_font.name = 'Tahoma'

        img_idx = 1
        for image in project.sorted_images:
            if len(image.caption) > 5: #no caption if less than 5 characters in caption
	    	img_txt = str(img_idx) + ". " + image.caption
            	document.add_paragraph(img_txt, document.styles['Normal'])
		
            	img_full_url = os.path.join(
                	settings.MEDIA_ROOT, image.image.url.split('/media/')[1]
            	)
            	#img_width = image.image.width  #todo if images are vertical handle differently
            	document.add_picture(img_full_url, width=Inches(4.8))
            	last_paragraph = document.paragraphs[-1]  # grab the last paragraph
            	last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER  # center the content of the last paragraph
            	img_idx += 1
            	if img_idx % 2:#add two images and then page break
                	document.add_page_break()
            	else:
                	document.add_paragraph(" ") #add line break
        return document
