from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from ore.flags.forms import FlagForm
from ore.flags.models import Flag
from ore.projects.models import Project


class FlagView(FormView):
    template_name = 'repo/flag.html'
    form_class = FlagForm

    def get_form_kwargs(self):
        kwargs = super(FlagView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FlagView, self).get_context_data(**kwargs)
        context['content'] = self._get_content()
        return context

    def form_valid(self, form):
        flag_type = form.cleaned_data['flag_type']
        extra_comments = form.cleaned_data['extra_comments']
        flagger = self.request.user
        content = self._get_content()

        flag = Flag.create_flag(content, flag_type, flagger, extra_comments)
        if flag:
            messages.success(self.request, "You have successfully flagged the content.")
        else:
            messages.warning(self.request, "You have already flagged this content.")

        return redirect(self._get_redirect_path())

    # Returns the content to be flagged
    def _get_content(self):
        pass

    # Where to redirect the user if successful
    def _get_redirect_path(self):
        return self._get_content()

    def get(self, request, *args, **kwargs):
        # Check to see if the user has already flagged this content
        if Flag.flagged(self._get_content(), flagger=request.user):
            return self.content_already_flagged(request, *args, **kwargs)

        return super(FlagView, self).get(request, *args, **kwargs)

    def content_already_flagged(self, request, *args, **kwargs):
        messages.warning(request, "You have already flagged this content.")
        return redirect(self._get_content())

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(FlagView, self).dispatch(request, *args, **kwargs)


class ProjectsFlagView(FlagView):
    def _get_content(self):
        self.namespace = self.kwargs['namespace']
        self.project = self.kwargs['project']
        return get_object_or_404(Project.objects.as_user(self.request.user), name=self.project, namespace__name=self.namespace)


class VersionsFlagView(FlagView):
    # todo once versions are complete
    pass
