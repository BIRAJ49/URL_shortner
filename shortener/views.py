from io import BytesIO

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import RegisterForm, ShortURLForm
from .models import ShortURL


def register(request):
    if request.user.is_authenticated:
        return redirect('shortener:list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shortener:list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


class OwnerQuerySetMixin(LoginRequiredMixin):
    model = ShortURL

    def get_queryset(self):
        return ShortURL.objects.filter(owner=self.request.user)


class ShortURLListView(OwnerQuerySetMixin, ListView):
    template_name = 'shortener/url_list.html'
    context_object_name = 'urls'


class ShortURLDetailView(OwnerQuerySetMixin, DetailView):
    template_name = 'shortener/url_detail.html'
    context_object_name = 'url'


class ShortURLCreateView(LoginRequiredMixin, CreateView):
    model = ShortURL
    form_class = ShortURLForm
    template_name = 'shortener/url_form.html'
    success_url = reverse_lazy('shortener:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ShortURLUpdateView(OwnerQuerySetMixin, UpdateView):
    form_class = ShortURLForm
    template_name = 'shortener/url_form.html'
    success_url = reverse_lazy('shortener:list')


class ShortURLDeleteView(OwnerQuerySetMixin, DeleteView):
    template_name = 'shortener/url_confirm_delete.html'
    success_url = reverse_lazy('shortener:list')


def redirect_short_url(request, key):
    short_url = get_object_or_404(ShortURL, key=key)
    if short_url.is_expired():
        return render(request, 'shortener/expired.html', {'url': short_url}, status=410)

    ShortURL.objects.filter(pk=short_url.pk).update(click_count=F('click_count') + 1)
    return redirect(short_url.long_url)


@login_required
def qr_code(request, pk):
    short_url = get_object_or_404(ShortURL, pk=pk, owner=request.user)
    import qrcode

    absolute_url = request.build_absolute_uri(short_url.get_short_path())
    image = qrcode.make(absolute_url)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')
