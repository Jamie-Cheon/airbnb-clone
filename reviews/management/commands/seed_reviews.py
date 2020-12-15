import random
from django.core.management import BaseCommand
from django_seed import Seed
from reviews.models import Review
from users import models as user_models
from rooms import models as room_models


class Command(BaseCommand):

    help = "This command creates fake reviews"

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help="How many reviews do you want to create")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        all_rooms = room_models.Room.objects.all()

        seeder.add_entity(Review, number, {
            "accuracy": lambda x: random.randint(1, 5),
            "communication": lambda x: random.randint(1, 5),
            "cleanliness": lambda x: random.randint(1, 5),
            "location": lambda x: random.randint(1, 5),
            "check_in": lambda x: random.randint(1, 5),
            "value": lambda x: random.randint(1, 5),
            "user": lambda x: random.choice(all_users),
            "room": lambda x: random.choice(all_rooms),
        })
        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number} reviews created!"))
