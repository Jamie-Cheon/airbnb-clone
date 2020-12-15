import random
from django.core.management import BaseCommand
from django_seed import Seed
from datetime import datetime, timedelta
from reservations.models import Reservation
from users import models as user_models
from rooms import models as room_models

NAME = "reservations"


class Command(BaseCommand):

    help = f"This command creates fake {NAME}"

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help=f"How many {NAME} do you want to create")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        all_rooms = room_models.Room.objects.all()

        seeder.add_entity(Reservation, number, {
            "status": lambda x: random.choice(["pending", "confirmed", "canceled"]),
            "guest": lambda x: random.choice(all_users),
            "room": lambda x: random.choice(all_rooms),
            "check_in": lambda x: datetime.now(),
            "check_out": lambda x: datetime.now() + timedelta(days=random.randint(3, 25))
        })

        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number} {NAME} created!"))
