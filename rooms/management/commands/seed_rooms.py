import random
from django.core.management import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms.models import Room, RoomType, Photo, Amenity, Facility, HouseRule
from users.models import User


class Command(BaseCommand):

    help = "This command creates fake rooms"

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help="How many rooms do you want to create")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = User.objects.all()
        room_types = RoomType.objects.all()
        seeder.add_entity(Room, number, {
            "name": lambda x: seeder.faker.address(),
            "host": lambda x: random.choice(all_users),
            "room_type": lambda x: random.choice(room_types),
            "guests": lambda x: random.randint(1, 10),
            "price": lambda x: random.randint(1, 300),
            "beds": lambda x: random.randint(1, 5),
            "bedrooms": lambda x: random.randint(1, 5),
            "baths": lambda x: random.randint(1, 5)
        })
        created_rooms = seeder.execute()
        created_clean = flatten(list(created_rooms.values()))
        all_amenities = Amenity.objects.all()
        all_facilities = Facility.objects.all()
        all_rules = HouseRule.objects.all()

        for pk in created_clean:
            room = Room.objects.get(pk=pk)
            for i in range(3, random.randint(10, 30)):
                Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    file=f"room_photos/{random.randint(1, 31)}.webp",
                    room=room
                )

            for a in all_amenities:
                num = random.randint(0, 15)
                if num % 2 == 0:
                    room.amenities.add(a)

            for f in all_facilities:
                num = random.randint(0, 15)
                if num % 2 == 0:
                    room.facilities.add(f)

            for r in all_rules:
                num = random.randint(0, 15)
                if num % 2 == 0:
                    room.house_rules.add(r)

        self.stdout.write(self.style.SUCCESS(f"{number} rooms created!"))
