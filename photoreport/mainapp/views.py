import StringIO

from django.views.generic import FormView, View
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404
# from PIL import Image as PImage
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO
from PIL import Image as PImage
from zipfile import ZipFile,ZipInfo
import json
from docx import Document
from .generate_report import DocumentGenerator
from .forms import InputForm, TempFileForm, InputExcelForm
from .models import InputFile, Image, InputXls
from templateV2 import *
from get_info_excel import read_from_excel
from people import *
from branches import *
#from django.contrib.auth.mixins import LoginRequiredMixin

class LandingInputFileCreateView(FormView):
    """Module for landing page and accepting input zip file of photos."""
    form_class = InputForm
    template_name = 'landing.html'

    def get_success_url(self, *args, **kwargs):
        input_id = str(self.obj.id)
        return reverse_lazy('preview', kwargs={'input_id': input_id})

    def form_valid(self, form):
        result = form.save()
        self.obj = result
        return super(LandingInputFileCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(LandingInputFileCreateView, self).get_context_data(
            **kwargs)
        return context


class TempFileResumeView(FormView):
    """Module for accepting tempfile to resume project."""
    template_name = 'tempfile.html'
    form_class = TempFileForm

    def get_success_url(self, *args, **kwargs):
        input_id = str(self.input_file_id)
        return reverse_lazy('preview', kwargs={'input_id': input_id})

    def form_valid(self, form):
        self.input_file_id = form.save()
        return super(TempFileResumeView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TempFileResumeView, self).get_context_data(
            **kwargs)
        return context


class UploadFileView(FormView):
    """Module for landing page and accepting input zip file of photos."""
    form_class = InputExcelForm
    template_name = 'template.html'
    def get_success_url(self, *args, **kwargs):
        input_id = str(self.obj.id)
        return reverse_lazy('download', kwargs={'input_id': input_id})

    def form_valid(self, form):
        result = form.save()
        self.obj = result
        return super(UploadFileView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UploadFileView, self).get_context_data(
            **kwargs)
        return context


class DownloadDocView(View):
    template_name='download.html'
    styles=['standard','letter']
    def get_context_data(self, **kwargs):
        context = {}
	path=get_object_or_404(InputXls, id=int(self.kwargs.get('input_id'))).get_xls().path
	
	data_lists=read_from_excel(path)
	data_list=data_lists[0]
	print(data_list)
	eng = data_list['PROJMGR']
	context['state']=states[data_list['INSURED INFORMATION/ST']]
	context['name']=engineers[eng]["Name"]
	context['job_number']=data_list['FILENO.']
	context['client']=data_list['CLIENT INFORMATION/CLIENT']
	context['insured']=data_list['INSURED INFORMATION/INSURED']
	context['descrpt']=data_list['DESCRIPTION']
	context['styles']=self.styles
        return context    

    def get(self, request, *args, **kwargs):
        input_id = self.kwargs.get('input_id')
        input_file = get_object_or_404(InputXls, id=int(input_id))
        download_file = request.GET.get('download', False)
	style=request.GET.get('style',self.styles[0])

	if download_file:
	    file_xls=input_file.get_xls()
	    #print file_xls.path
            file_name =gen_docx(file_xls.path,style)
	    doc=Document(file_name)

	    f = BytesIO()
            doc.save(f)
            length = f.tell()
            f.seek(0)
            res = HttpResponse(
                f.getvalue(),
                content_type='application/vnd.openxmlformats' +
                '-officedocument.wordprocessingml.document'
            )
            res['Content-Disposition'] = 'attachment; filename=' + \
                file_name
            res['Content-Length'] = length
	    os.remove(file_name)
	    
            return res
	return render(request, self.template_name, self.get_context_data())


class PhotoPreview(View):
    template_name = 'preview.html'

    def get_context_data(self, **kwargs):
        context = {}
        input_id = self.kwargs.get('input_id')
        input_file = get_object_or_404(InputFile, id=int(input_id))

        # create new project if not created
        project = input_file.create_project()

        final_images = project.sorted_images
        context['images'] = final_images
        context['first_img'] = final_images[0]
        context['project'] = project

        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = dict(request.POST)
        for key, value in data.items():
            if key == 'csrfmiddlewaretoken':
                continue
            elif key == 'project':
                project_name = value[0]
                input_id = self.kwargs.get('input_id')
                input_file = get_object_or_404(InputFile, id=int(input_id))
                input_file.project.name = project_name
                input_file.project.save()
                continue
            elif key.startswith('caption_'):
                img_id = key.split('_')[1]
                img = Image.objects.get(id=int(img_id))
                img.caption = value[0]
                rotate_angle = 0
                rotate_key = 'rotate_' + img_id

                rotate_angle = data.get(rotate_key, ['0'])
                rotate_angle = int(rotate_angle[0])

                if rotate_angle in[90, 180, 270]:
                    image = PImage.open(img.image.path)
                    image = image.rotate(rotate_angle, expand=True)
                    try:
                        image.save(img.image.path)
                    except:
                        pass
                img.save()

        return HttpResponseRedirect(
            reverse_lazy('success', kwargs={'pk': input_file.id})
        )


class ReportGenView(View):
    template_name = 'success.html'

    def get_context_data(self, **kwargs):
        context = {}
        return context

    def get(self, request, *args, **kwargs):
        input_id = self.kwargs.get('pk')
        input_file = get_object_or_404(InputFile, id=int(input_id))
        project = input_file.create_project()

        generate_report = request.GET.get('generate', False)
        download_tempfile = request.GET.get('tempfile', False)
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        if generate_report:
            gen = DocumentGenerator()
            file_name = project.name.replace(' ', '_') + '_' + today_date + '_PhotoLog.docx'
            document = gen.create(project)

            f = BytesIO()
            document.save(f)
            length = f.tell()
            f.seek(0)
            response = HttpResponse(
                f.getvalue(),
                content_type='application/vnd.openxmlformats' +
                '-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename=' + \
                file_name
            response['Content-Length'] = length
            return response
        if download_tempfile:
            content = {
                "id": input_file.id
            }
            file_content = json.dumps(content)
            res = HttpResponse(file_content)
            file_name = project.name.replace(' ', '_') + '_' + today_date + '_PhotoLog.json'
            res['Content-Disposition'] = 'attachment; filename=' + file_name
            return res
        return render(request, self.template_name, self.get_context_data())


