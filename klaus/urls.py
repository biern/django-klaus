# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from klaus import views


# TODO: These regexps are probably not going to cover all the cases
repo = r'(?P<repo>[\w\.\-_]+)'
rev = r'(?P<rev>[\w\.\-_]+)'
path = r'(?P<path>.+)'


urlpatterns = patterns(
    '',

    url(r'^$',
        views.repo_list, name=views.RepoListView.view_name),

    url(r'^' + repo + '/$',
        views.history, name=views.HistoryView.view_name),

    url(r'^' + repo + '/tree/' + rev + '/$',
        views.history, name=views.HistoryView.view_name),
    url(r'^' + repo + '/tree/' + rev + '/' + path + '/$',
        views.history, name=views.HistoryView.view_name),

    url(r'^' + repo + '/blob/' + rev + '/$',
        views.blob, name=views.BlobView.view_name),
    url(r'^' + repo + '/blob/' + rev + '/' + path + '/$',
        views.blob, name=views.BlobView.view_name),

    url(r'^' + repo + '/raw/' + rev + '/$',
        views.raw, name=views.RawView.view_name),
    url(r'^' + repo + '/raw/' + rev + '/' + path + '/$',
        views.raw, name=views.RawView.view_name),

    url(r'^' + repo + '/commit/' + rev + '/$',
        views.commit, name=views.CommitView.view_name)
)
