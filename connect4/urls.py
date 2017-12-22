from django.conf.urls import url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url = 'games/', permanent=False)),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^games/$', views.games, name='games'),
    url(r'^games/(?P<game>\w+)/$', views.game),
    url(r'^games/(?P<game>\w+)/coins/$', views.coins, name='coins')
]
