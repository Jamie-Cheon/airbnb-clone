from django.db import models
from core import models as core_models


class Conversation(core_models.TimeStampedModel):

    """ Conversation Model Definition """

    participants = models.ManyToManyField("users.User", blank=True, related_name="conversations")

    def __str__(self):
        usernames = [user.username for user in self.participants.all()]
        return ", ".join(usernames)

    def count_messages(self):
        return self.messages.count()

    count_messages.short_description = "Messages"

    def count_participants(self):
        return self.participants.count()

    count_participants.short_description = "Participants"


class Message(core_models.TimeStampedModel):

    """ Message Model Definition """

    message = models.TextField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="messages")
    conversation = models.ForeignKey("Conversation", on_delete=models.CASCADE, related_name="messages")

    def __str__(self):
        return f"{self.user} says: {self.message}"
