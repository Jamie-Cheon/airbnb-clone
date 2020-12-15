import random
from django.core.management import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from lists.models import List
from users import models as user_models
from rooms import models as room_models

NAME = "lists"


class Command(BaseCommand):

    help = f"This command creates fake {NAME}"

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help=f"How many {NAME} do you want to create")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        all_rooms = room_models.Room.objects.all()

        seeder.add_entity(List, number, {
            "user": lambda x: random.choice(all_users),

        })

        created = seeder.execute()
        cleaned = flatten(list(created.values()))

        for pk in cleaned:
            list_model = List.objects.get(pk=pk)
            to_add = all_rooms[random.randint(0, 5):random.randint(6, 30)]

            list_model.rooms.add(*to_add)

        self.stdout.write(self.style.SUCCESS(f"{number} {NAME} created!"))
