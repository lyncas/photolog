from django import forms
from django.shortcuts import render, get_object_or_404
import json
from zipfile import ZipFile
import xlrd
from .models import InputFile,InputXls,AdditionalZipFile



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
        for photo in photos:
            # check if folders/photos name have space cloud computing environments including Amazon EC2, Microsoft Azure, and Google Compute Engine, said a software developer blogging as Python Swees
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

class InputAdditionalZipForm(forms.ModelForm):
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
    data = forms.MultipleHiddenInput()
    class Meta:
        model = AdditionalZipFile
        fields = (
           'zip_file','input_id'
       )
    #input_id=""
    #def set_input_id(self,value):
     #   self.input_id=value
      #  return self.input_id

    def clean_zip_file(self):
        myfile = self.cleaned_data['zip_file']
        archive = ZipFile(myfile, 'r')
        photos = archive.namelist()
        for photo in photos:
            # check if folders/photos name have space cloud computing environments including Amazon EC2, Microsoft Azure, and Google Compute Engine, said a software developer blogging as Python Swees
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
        
        input_id=""
        for key, value in self.data.items():
            if key == 'csrfmiddlewaretoken':
                continue
            elif key == 'input_id':
                input_id=value[0]
        

        input_file = get_object_or_404(InputFile, id=int(input_id))
        current_num_photos = int(input_file.project.images.count())
        max_photos = 499-current_num_photos
	
 	if num_photos>max_photos:
 	    raise forms.ValidationError(
                "ZIP FILE MUST HAVE "+max_photos+" OR FEWER PHOTOS!!!!"
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
