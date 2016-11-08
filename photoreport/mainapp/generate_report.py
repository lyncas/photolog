from docx import Document
from docx.shared import Pt
from docx.shared import Inches
#import docx.enum.style import WD_STYLE_TYPE 
import os
from django.conf import settings


class DocumentGenerator(object):

    def create(self, project):
        document = Document()
        obj_style = document.styles['Normal']
	#obj_charstyle = obj_style.add_style('CaptionStyle', WD_STYLE_TYPE.CHARACTER)
	obj_font = obj_style.font
	obj_font.size = Pt(12)
	obj_font.name = 'Tahoma'
	#paragraph.style = document.styles['Normal']

        #document.add_heading(project.name, 0)
	img_idx = 1
        for image in project.sorted_images:
            img_txt = str(img_idx) + ". " + image.caption
            document.add_paragraph(img_txt, document.styles['Normal'])

            img_full_url = os.path.join(
                settings.MEDIA_ROOT, image.image.url.split('/media/')[1]
            )
            #img_width = image.image.width  #todo if images are too small throw bug? 
            document.add_picture(img_full_url, width=Inches(5.0))#5.25 inches is other size
            #document.add_paragraph(" ")#add line break            

            img_idx += 1
            if img_idx % 2:#add two images and then page break
                document.add_page_break()
            else:
		document.add_paragraph(" ") #add line break 
        # document.save(file_name)
        return document
