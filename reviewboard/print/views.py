from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here. This is the print view
class PrintView(TemplateView):
    template_name = 'reviews/print.html'
