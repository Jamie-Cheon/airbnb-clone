from django.core.management import BaseCommand
from rooms.models import Amenity


class Command(BaseCommand):

    help = "This command creates amenities"

    def handle(self, *args, **options):
        amenities = [
            "Kitchen",
            "Heating",
            "Washer",
            "Wifi",
            "Indoor fireplace",
            "Iron",
            "Laptop friendly workspace",
            "Crib",
            "Self check-in",
            "Carbon monoxide detector",
            "Shampoo",
            "Air conditioning",
            "Dryer",
            "Breakfast",
            "Hangers",
            "Hair dryer",
            "TV",
            "High chair",
            "Smoke detector",
            "Private bathroom",
        ]

        for a in amenities:
            Amenity.objects.create(name=a)

        self.stdout.write(self.style.SUCCESS(f"{len(amenities)} Amenities created!"))
