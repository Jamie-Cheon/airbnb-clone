from django.views.generic import ListView
from .models import Room


class HomeView(ListView):

    """ HomeView Definition """

    model = Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = ("created",)
    template_name = "rooms/room_list.html"
    context_object_name = "rooms"


