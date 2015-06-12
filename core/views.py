# -*- coding: utf-8 -*-

import os
import random
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from core.models import Pasty
from core.models import Source
from core.sync import sync_rss_source


def home(request):
    data = {}
    return render(request, 'core/home.html', data)


def one(request):
    pasties = Pasty.objects.all()

    ret = []

    for p in pasties:
        for i in range(p.votes):
            ret.append(p)

    pasty = random.choice(ret)

    data = {
        "pasty": pasty
    }

    return render(request, 'core/pasty.html', data)


def sources(request):
    sources = Source.objects.all()

    data = {
        'sources': sources
    }

    return render(request, 'core/sync.html', data)


def sync(request):
    sources_id = request.POST.getlist('source')

    if sources_id:
        for src_id in sources_id:
            source = Source.objects.get(pk=src_id)
            sync_rss_source(source)

    return HttpResponseRedirect(reverse('sources'))



