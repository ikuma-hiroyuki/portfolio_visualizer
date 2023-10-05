from django.views.generic import TemplateView
from future_backtest import forms


class BacktestView(TemplateView):
    template_name = 'backtest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dropdown'
        context['form'] = forms.BacktestSettingsForm()
        return context

    def post(self, request, *args, **kwargs):
        form = forms.BacktestSettingsForm(request.POST)
        if form.is_valid():
            context = self.get_context_data(**kwargs)
            context['choice'] = form.cleaned_data['time_period']
            print(context['choice'])
            return self.render_to_response(context)
        else:
            return self.render_to_response(self.get_context_data(**kwargs))
