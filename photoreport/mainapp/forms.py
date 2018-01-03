from django import forms
import json
from zipfile import ZipFile
import xlrd
from .models import InputFile,InputXls



class InputExcelForm(forms.ModelForm):
    xls_file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                'label': 'Select Input .xls File (no spaces in the file name)',
                'class': u'btn btn-primary btn-xl page-scroll',
                'placeholder': u'Enter Your .xls File',
                'accept': "application/xls"
            }
        )
    )
    class Meta:
        model = InputXls
        fields = (
            'xls_file',
        )
    def clean_xls_file(self):
	xls_file=self.cleaned_data['xls_file']
	return xls_file


class InputForm(forms.ModelForm):
    zip_file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                'label': 'Select Input Zip File (no spaces in the file name)',
                'class': u'btn btn-primary btn-xl page-scroll',
                'placeholder': u'Enter Your Zip File',
                'accept': "application/zip"
            }
        )
    )
    data = forms.HiddenInput()
    class Meta:
        model = InputFile
        fields = (
           'zip_file',
       )

    def clean_zip_file(self):
        myfile = self.cleaned_data['zip_file']
        archive = ZipFile(myfile, 'r')
        photos = archive.namelist()
	file_size=0
        for photo in photos:
	    file_size=file_size+1
	    #if file_size>499:
		#raise forms.ValidationError(
		 #   "ZIP FILE MUST HAVE LESS THAN 500 PHOTOS!!!"
		#)
            # check if folders/photos name have spaces
            if len(photo.split()) > 1 or photo.strip() != photo:
                raise forms.ValidationError(
                    "ZIPPED FOLDERS OR PHOTO NAMES MUST NOT CONTAIN SPACES!!!"
                )
        valid_extensions = [
            '.png', '.jpg', '.JPG', '.gif', '.bmp', '.jpeg', '.JPEG'
        ]
        valid_files = [
            i for i in photos if '.' +
            i.split('.')[-1] in valid_extensions
        ]
	num_photos=len(valid_files)
 	if num_photos>499:
 	    raise forms.ValidationError(
                "ZIP FILE MUST HAVE LESS THAN 500 PHOTOS!!!"
            )
        if not valid_files:
            raise forms.ValidationError(
                "Image not found in zip."
            )
        return myfile


class TempFileForm(forms.Form):
    temp_file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                'label': 'Select Temp File',
                'class': u'btn btn-primary btn-xl page-scroll',
                'placeholder': u'Enter Your Temp File',
                'accept': "application/json"
            }
        )
    )
    data = forms.HiddenInput()

    def clean_temp_file(self):
        temp_file = self.cleaned_data['temp_file']
        input_file_id = self.parse_data(temp_file)
        if not input_file_id:
            raise forms.ValidationError(
                "Corrupted temp file."
            )
        else:
            self.data = input_file_id
        return temp_file

    def parse_data(self, temp_file):
        contents = temp_file.read().decode('utf-8')
        data = json.loads(contents)
        try:
            input_file_id = data.get('id')
        except:
            input_file_id = None
        return input_file_id

    def save(self, *args, **kwargs):
        return self.data
