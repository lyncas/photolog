import os
import tempfile
import zipfile
import shutil
from lxml import etree
from get_info_excel import *
from branches import *
from people import *
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings

updated_xml_content = ''
data_list = []


def make_client_insured_info(excel_fname):
    """
    Get updated info from excel file.
    :return:
    """
    global data_list
    data_lists = read_from_excel(excel_fname)
    data_list = data_lists[0]


def get_word_xml(docx_filename):
    """
    Get xml content from source docx file by treating the document as a zip file
    :param docx_filename:
    :return:
    """
    global zip
    zip = zipfile.ZipFile(docx_filename)
    xml_content = zip.read('word/document.xml')
    return xml_content


def get_footer2_xml(docx_filename):
    """
    Get xml content from word/footer2.xml.
    :param docx_filename:
    :return:
    """
    zip = zipfile.ZipFile(docx_filename)
    xml_content = zip.read('word/footer2.xml')
    return xml_content


def get_footer1_xml(docx_filename):
    """
    Get xml content from word/footer1.xml
    :param docx_filename:
    :return:
    """
    zip = zipfile.ZipFile(docx_filename)
    xml_content = zip.read('word/footer1.xml')
    return xml_content

def get_header1_xml(docx_filename):
    """
    Get xml string from xml file.
    :param xml_string:
    :return:
    """
    zip = zipfile.ZipFile(docx_filename)
    xml_content = zip.read('word/header1.xml')
    return xml_content

def get_header2_xml(docx_filename):
    """
    Get xml string from xml file.
    :param xml_string:
    :return:
    """
    zip = zipfile.ZipFile(docx_filename)
    xml_content = zip.read('word/header2.xml')
    return xml_content

def get_xml_tree(xml_string):
    """
    Get xml string from xml file.
    :param xml_string:
    :return:
    """
    return etree.fromstring(xml_string)


def get_xml_string(xml_tree):
    """
    Get xml tree string from xml content.
    :param xml_tree:
    :return:
    """
    return etree.tostring(xml_tree, pretty_print=True)


def iter_text(xml_tree):
    """Iterator to go through xml tree's text nodes"""
    for node in xml_tree.iter(tag=etree.Element):
        if _check_element_is(node, 't'):
            #print node.text #DEBUGGING 
            yield (node)


def _check_element_is(element, type_char):
    """
    Check tagname <w:t> in xmltree.
    :param element:
    :param type_char:
    :return:
    """
    word_schema = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    return element.tag == '{%s}%s' % (word_schema, type_char)

def format_date(date, form):
    """shift format of date to two formats"""
    if date== u'':
	return ' '
    elif form == 'short':
        return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
    else:
        return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')

def get_footer_date():
    date=datetime.date.today()
    return date.strftime("%B XX, %Y")

def update_xml_content(xml_tree):
    """
    Modify the document content.
    :param xml_tree:
    :return:
    """
    global updated_xml_content
    #commonly used variables. 
    eng = data_list['PROJMGR']
    insured_name_array = data_list['INSURED INFORMATION/INSURED'].split("/") #take out backslash
    insured_name = insured_name_array[0]
    insured_city = data_list['INSURED INFORMATION/CITY']
    insured_state = states[data_list['INSURED INFORMATION/ST']]#transform state
    insured_zip = data_list['INSURED INFORMATION/ZIPCODE']
    insured_addr = data_list['INSURED INFORMATION/LOSS LOCATION']

    client_suite = data_list['CLIENT INFORMATION/STE']
    client_addr = data_list['CLIENT INFORMATION/ADDRESS 1']
    if len(client_suite) > 1:
        client_addr = client_addr + ", " + client_suite    
    client_city = data_list['CLIENT INFORMATION/CITY']
    client_state = states[data_list['CLIENT INFORMATION/ST']] #transform to full state name
    client_zip = data_list['CLIENT INFORMATION/ZIPCODE']
    
    for node in iter_text(xml_tree):
        if node.text =='#ENGINEER_NAME':
	    try:
                node.text = engineers[eng]["Name"]
	    except:
		node.text = "ERROR ENGINEER NAME NOT FOUND"
        elif node.text =='#ENG_TITLE':
	    try:
                node.text = engineers[eng]["Title"]
	    except:
		node.text = "ERROR TITLE NOT FOUND"
        elif node.text =='#LIC_NUM':
	    try:
                node.text = engineers[eng][data_list['INSURED INFORMATION/ST']] #stays in abbreviated form
	    except:
		node.text = "ERROR LICENSE NOT FOUND"        
        elif node.text == '#CLIENT':
            node.text = data_list['CLIENT INFORMATION/CLIENT'].upper()
	elif node.text == '#client':
	    node.text = data_list['CLIENT INFORMATION/CLIENT']
        elif node.text == '#CLIENT_NAME':
            node.text = data_list['CLIENT INFORMATION/CLIENT']
        elif node.text == '#CLIENT_ADDRESS':
            node.text = client_addr.upper()
	elif node.text == '#client_address':
            node.text = client_addr
        elif node.text == '#CLIENT_CITY_ST_ZIP':
            node.text = client_city.upper() + ", " + client_state.upper() + " " + client_zip.upper()
	elif node.text == '#client_city_st_zip':
            node.text = client_city + ", " + client_state + " " + client_zip
        elif node.text == '#CONTACT_NAME':
            node.text = data_list['CLIENT INFORMATION/CONTACTFIRST NAME'] + ' ' + data_list['CLIENT INFORMATION/CONTACTLAST NAME']
        elif node.text == '#CONTACT_PHONE':
            node.text = data_list['CLIENT INFORMATION/PHONE #'].upper()
	elif node.text == '#contact_phone':
            node.text = data_list['CLIENT INFORMATION/PHONE #']
        elif node.text == '#CLAIM_NUM':
            node.text = data_list['INSURED INFORMATION/CLAIM/PO #'].upper()
	elif node.text == '#claim_num':
            node.text = data_list['INSURED INFORMATION/CLAIM/PO #']
        elif node.text == '#INSURED_NAME':
            node.text = insured_name.upper()
        elif node.text == '#insured_name':
            node.text = insured_name
        elif node.text == '#LOSS_ADDRESS':
            node.text = insured_addr.upper()
	elif node.text == '#loss_address':
            node.text = insured_addr
        elif node.text == '#LOSS_CITY_ST_ZIP':
            node.text = insured_city.upper() + ', ' + insured_state.upper() + " " + insured_zip
	elif node.text == '#loss_city_st_zip':
            node.text = insured_city + ', ' + insured_state + " " + insured_zip
        elif node.text == '#LOSS_CITY_ST':
            node.text = insured_addr + ' in ' +insured_city + ', '+insured_state
        elif node.text == '#LOSS_STATE':
            node.text = insured_state
        elif node.text == '#SEX':
            node.text = data_list['CLIENT INFORMATION/'] #should update list export on database
	    if is_florida():
                print "Exported template-output-fl.docx for File # " + data_list['FILENO.']
	    else:
	        print "Exported template-output.docx for File # " + data_list['FILENO.']	
        elif node.text == '#INS_NAME':
            node.text = data_list['CLIENT INFORMATION/CONTACTFIRST NAME'].upper() + ' ' + data_list['CLIENT INFORMATION/CONTACTLAST NAME'].upper()
	elif node.text == '#ins_name':
            node.text = data_list['CLIENT INFORMATION/CONTACTFIRST NAME'] + ' ' + data_list['CLIENT INFORMATION/CONTACTLAST NAME']
        elif node.text == '#file_no':
            node.text = data_list['FILENO.']
        elif node.text == '#DOL':
            node.text = format_date(data_list['LOSSDATE'],'short')
        elif node.text == '#INSP_DATE':
            node.text = format_date(data_list['INSPDATE'], 'long')
        elif node.text == '#REC_DATE':
            node.text = format_date(data_list['''DATEREC'D'''], 'long')
        elif node.text == '#LOC':
            node.text = branchDict[data_list['BRH']]["Name"] 
        elif node.text == '#LOC_ADDR':
            node.text = branchDict[data_list['BRH']]["Address"] 
        elif node.text == '#LOC_SUITE':
            node.text = branchDict[data_list['BRH']]["Suite"] 
        elif node.text == '#LOC_CITY':
            node.text = branchDict[data_list['BRH']]["City"] 
        elif node.text == '#LOC_PHONE':
            node.text = branchDict[data_list['BRH']]["Phone"] 
        elif node.text == '#CERT':
            node.text = branchDict[data_list['BRH']]["Cert"]
        elif node.text == '#AGENCY':
            node.text = branchDict[data_list['BRH']]["Agency"]
        else:
            pass

    return xml_tree


def update_footer_xml(xml_tree):
    """
    Modify the footer infomation.
    :param xml_tree:
    :return:
    """
    for node in iter_text(xml_tree):
        if node.text == '#file_no':
            node.text = data_list['FILENO.']
	elif node.text == '#FOOTER_DATE':
	    node.text = get_footer_date()
	else:
	    pass
    return xml_tree 

def update_header_xml(xml_tree):
    """
    Modify the footer infomation.
    :param xml_tree:
    :return:
    """
    for node in iter_text(xml_tree):
	if node.text == '#SEX':
	    node.text = data_list['CLIENT INFORMATION/']
	elif node.text == '#CONTACT_NAME':
	    node.text = data_list['CLIENT INFORMATION/CONTACTFIRST NAME'] + ' ' + data_list['CLIENT INFORMATION/CONTACTLAST NAME']
	elif node.text == '#CLIENT_NAME':
            node.text = data_list['CLIENT INFORMATION/CLIENT']
	elif node.text == '#file_no':
            node.text = data_list['FILENO.']
	else:
	    pass
    return xml_tree

def is_florida():
    """
    Determine if the state is florida
    :param:
    :return:
    """
    insured_state = data_list['INSURED INFORMATION/ST']
    print insured_state
    if insured_state=='FL':
	return True
    else:
	return False

def _write_and_close_docx(testDoc, xml_tree, xml_footer2_tree, xml_footer1_tree, xml_header1_tree, xml_header2_tree, outDoc):
    """
        Create a temp directory, expand the original docx zip.
        Write the modified xml to word/document.xml
        Zip it up as the new docx
    """

    tmp_dir = tempfile.mkdtemp()
    zip = zipfile.ZipFile(testDoc)
    zip.extractall(tmp_dir)
    


    # Write updated info to document.xml
    with open(os.path.join(tmp_dir, 'word/document.xml'), 'w') as f:
        xmlstr = etree.tostring(update_xml_content(xml_tree))
        f.write(xmlstr)
    # Write updated footer info to footer2.xml
    with open(os.path.join(tmp_dir, 'word/footer2.xml'), 'w') as f:
        xml_footer_str = etree.tostring(update_footer_xml(xml_footer2_tree))
        f.write(xml_footer_str)

    # Write updated footer info to footer1.xml
    with open(os.path.join(tmp_dir, 'word/footer1.xml'), 'w') as f:
        xml_footer_str = etree.tostring(update_footer_xml(xml_footer1_tree))
        f.write(xml_footer_str)
    
    # Write update header info to header2.xml
    with open(os.path.join(tmp_dir, 'word/header2.xml'), 'w') as f:
        xml_header_str = etree.tostring(update_header_xml(xml_header2_tree))
        f.write(xml_header_str)

    # Write update header info to header1.xml
    with open(os.path.join(tmp_dir, 'word/header1.xml'), 'w') as f:
        xml_header_str = etree.tostring(update_header_xml(xml_header1_tree))
        f.write(xml_header_str)

    # Get a list of all the files in the original docx zipfile
    filenames = zip.namelist()

    # Now, create the new zip file and add all the filex into the archive
    # the archive theen becomes a word docx
    with zipfile.ZipFile(outDoc, "w") as docx:
        for filename in filenames:
            docx.write(os.path.join(tmp_dir, filename), filename)

    # Clean up the temp dir
    shutil.rmtree(tmp_dir)

def gen_docx(excel_fname,style):
    # Get client info and insured info
    make_client_insured_info(excel_fname)

    if data_list['INSURED INFORMATION/ST']=='FL':
	if str(style)=='letter':
	    testDoc = 'mainapp/static/DOC-Templates/GEN-'+str(style)+'/template.docx'
	    outputDoc = 'template-output-fl-'+str(style)+'-'+data_list['PROJMGR']+'.docx'
	else:
	    testDoc = 'mainapp/static/DOC-Templates/FL-'+str(style)+'/template-'+data_list['PROJMGR']+'.docx'
	    outputDoc = 'template-output-fl-'+str(style)+'-'+data_list['PROJMGR']+'.docx'
    else:
	if str(style)=='letter':
	    testDoc = 'mainapp/static/DOC-Templates/GEN-'+str(style)+'/template.docx'
	    outputDoc = 'template-output-fl-'+str(style)+'.docx'
	else:
	    testDoc = 'mainapp/static/DOC-Templates/GEN-'+str(style)+'/template.docx'
	    outputDoc = 'template-output-fl-'+str(style)+'.docx'
    
    # Get footer2 content from test.docx
    xml_footer2_content = get_footer2_xml(testDoc)

    # Get footer1 content from test.docx
    xml_footer1_content = get_footer1_xml(testDoc)

    # Get header2 content from test.docx
    xml_header2_content = get_header2_xml(testDoc)

    # Get header1 content from test.docx
    xml_header1_content = get_header1_xml(testDoc)

    # Get doc content from test.docx
    xml_content = get_word_xml(testDoc)

    # Get xml tree for footer1.xml, footer2.xml, document.xml.
    xml_tree = get_xml_tree(xml_content)
    xml_footer2_tree = get_xml_tree(xml_footer2_content)
    xml_footer1_tree = get_xml_tree(xml_footer1_content)
    xml_header2_tree = get_xml_tree(xml_header2_content)
    xml_header1_tree = get_xml_tree(xml_header1_content)
    # Modify and save doc
    _write_and_close_docx(testDoc, xml_tree, xml_footer2_tree, xml_footer1_tree, xml_header2_tree, xml_header1_tree, outputDoc)
    return outputDoc
     
