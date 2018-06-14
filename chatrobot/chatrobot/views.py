#encoding:utf-8
import os
import sys
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from datetime import datetime
from .QA.run import run
from .QA.qa_store import store
import json
import logging
import traceback


def answer(request):
    s_question = request.GET.get('question', '')
    # s_context = request.GET.get('context', '')
    s_answer = run(s_question)
    return HttpResponse(s_answer)

def storeqa(request):
    brandinfo = request.GET.get('brandinfo', '')
    s_question = request.GET.get('question', '')
    s_context = request.GET.get('context', '')
    s_answer = request.GET.get('answer', '')
    b_success = store(brandinfo, s_question, s_context, s_answer)
    return HttpResponse(b_success)

