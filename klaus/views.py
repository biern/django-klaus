# -*- coding: utf-8 -*-
import os
import stat

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView

from dulwich.objects import Blob

from klaus import markup, utils
from klaus.utils import parent_directory, subpaths, pygmentize, \
    force_unicode, guess_is_binary, guess_is_image
from klaus.repo import RepoManager, RepoException


class KlausContextMixin(object):
    def get_context_data(self, **ctx):
        context = super(KlausContextMixin, self).get_context_data(**ctx)
        context['KLAUS_SITE_NAME'] = getattr(
            settings, 'KLAUS_SITE_NAME', 'Klaus GIT browser')
        context['KLAUS_VERSION'] = utils.KLAUS_VERSION
        return context


class KlausTemplateView(KlausContextMixin, TemplateView):
    pass


class RepoListView(KlausTemplateView):
    """Shows a list of all repos and can be sorted by last update. """

    template_name = 'klaus/repo_list.html'
    view_name = 'repo-list'

    def get_context_data(self, **ctx):
        context = super(RepoListView, self).get_context_data(**ctx)

        if 'by-last-update' in self.request.GET:
            sort_key = lambda repo: repo.get_last_updated_at()
            reverse = True
        else:
            sort_key = lambda repo: repo.name
            reverse = False

        context['repos'] = sorted(RepoManager.all_repos(), key=sort_key,
                                  reverse=reverse)
        return context


class BaseRepoView(KlausTemplateView):
    """
    Base for all views with a repo context.

    The arguments `repo`, `rev`, `path` (see `dispatch_request`) define the
    repository, branch/commit and directory/file context, respectively --
    that is, they specify what (and in what state) is being displayed in all the
    derived views.

    For example: The 'history' view is the `git log` equivalent, i.e. if `path`
    is "/foo/bar", only commits related to "/foo/bar" are displayed, and if
    `rev` is "master", the history of the "master" branch is displayed.
    """

    view_name = None
    "required by templates"

    def get_context_data(self, **ctx):
        context = super(BaseRepoView, self).get_context_data(**ctx)

        repo = RepoManager.get_repo(self.kwargs['repo'])
        rev = self.kwargs.get('rev')
        path = self.kwargs.get('path')
        if isinstance(path, unicode):
            path = path.encode("utf-8")
	if isinstance(rev, unicode):
            rev = rev.encode("utf-8")
        
	if rev is None:
            rev = repo.get_default_branch()
            if rev is None:
                raise RepoException("Empty repository")
        try:
            commit = repo.get_commit(rev)
        except KeyError:
            raise RepoException("No such commit %r" % rev)

        try:
            blob_or_tree = repo.get_blob_or_tree(commit, path)
        except KeyError:
            raise RepoException("File not found")

        context.update({
            'view': self.view_name,
            'repo': repo,
            'rev': rev,
            'commit': commit,
            'branches': repo.get_branch_names(exclude=rev),
            'tags': repo.get_tag_names(),
            'path': path,
            'blob_or_tree': blob_or_tree,
            'subpaths': list(subpaths(path)) if path else None,
        })

        return context


class TreeViewMixin(object):
    """
    Implements the logic required for displaying the current directory in the
    sidebar

    """
    def get_context_data(self, **ctx):
        context = super(TreeViewMixin, self).get_context_data(**ctx)
        context['root_tree'] = self.listdir(
            context['repo'], context['commit'], context['path'],
            context['blob_or_tree'])
        return context

    def listdir(self, repo, commit, root_directory, blob_or_tree):
        """
        Returns a list of directories and files in the current path of the
        selected commit
        """
        root_directory = root_directory or ''
        root_directory = self.get_root_directory(
            root_directory, blob_or_tree)
        root_tree = repo.get_blob_or_tree(commit, root_directory)

        dirs, files = [], []
        for entry in root_tree.iteritems():
            name, entry = entry.path, entry.in_path(root_directory)
            if entry.mode & stat.S_IFDIR:
                dirs.append((name.lower(), name, entry.path))
            else:
                files.append((name.lower(), name, entry.path))

        files.sort()
        dirs.sort()

        if root_directory:
            dirs.insert(0, (None, '..', parent_directory(root_directory)))

        return {'dirs': dirs, 'files': files}

    def get_root_directory(self, root_directory, blob_or_tree):
        if isinstance(blob_or_tree, Blob):
            # 'path' is a file (not folder) name
            root_directory = parent_directory(root_directory)
        return root_directory


class HistoryView(TreeViewMixin, BaseRepoView):
    """
    Show commits of a branch + path, just like `git log`. With
    pagination.
    """

    template_name = 'klaus/history.html'
    view_name = 'history'

    def get_context_data(self, **ctx):
        context = super(HistoryView, self).get_context_data(**ctx)

        page = context['page'] = int(self.request.GET.get('page', 0))

        if page:
            history_length = 30
            skip = (page - 1) * 30 + 10
            if page > 7:
                context['previous_pages'] = [0, 1, 2, None] + range(page)[-3:]
            else:
                context['previous_pages'] = xrange(page)
        else:
            history_length = 10
            skip = 0

        history = context['repo'].history(
            context['rev'],
            context['path'],
            history_length + 1,
            skip
        )
        if len(history) == history_length + 1:
            # At least one more commit for next page left
            more_commits = True
            # We don't want show the additional commit on this page
            history.pop()
        else:
            more_commits = False

        context.update({
            'history': history,
            'more_commits': more_commits,
        })

        return context


class BlobViewMixin(object):
    def get_context_data(self, **ctx):
        context = super(BlobViewMixin, self).get_context_data(**ctx)
        context['filename'] = os.path.basename(context['path'])
        return context


class BlobView(BlobViewMixin, TreeViewMixin, BaseRepoView):
    """ Shows a file rendered using ``pygmentize`` """

    template_name = 'klaus/view_blob.html'
    view_name = 'blob'

    def get_context_data(self, **ctx):
        context = super(BlobView, self).get_context_data(**ctx)

        if not isinstance(context['blob_or_tree'], Blob):
            raise RepoException("Not a blob")

        binary = guess_is_binary(context['blob_or_tree'])
        too_large = sum(map(len, context['blob_or_tree'].chunked)) > 100 * 1024

        if binary:
            context.update({
                'is_markup': False,
                'is_binary': True,
                'is_image': False,
            })
            if guess_is_image(context['filename']):
                context.update({
                    'is_image': True,
                })
        elif too_large:
            context.update({
                'too_large': True,
                'is_markup': False,
                'is_binary': False,
            })
        else:
            render_markup = 'markup' not in self.request.GET
            rendered_code = pygmentize(
                force_unicode(context['blob_or_tree'].data),
                context['filename'],
                render_markup
            )
            context.update({
                'too_large': False,
                'is_markup': markup.can_render(context['filename']),
                'render_markup': render_markup,
                'rendered_code': rendered_code,
                'is_binary': False,
            })

        return context


class RawView(BlobViewMixin, BaseRepoView):
    """
    Shows a single file in raw for (as if it were a normal filesystem file
    served through a static file server)
    """
    view_name = 'raw'

    def dispatch(self, *args, **kwargs):
        context = self.get_context_data()
        return HttpResponse(context['blob_or_tree'].chunked)


class CommitView(BaseRepoView):
    template_name = 'klaus/view_commit.html'
    view_name = 'commit'


repo_list = RepoListView.as_view()
history = HistoryView.as_view()
commit = CommitView.as_view()
blob = BlobView.as_view()
raw = RawView.as_view()
