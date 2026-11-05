from django.db import models
from django.contrib.auth.models import User


class HousePrediction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    area = models.FloatField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    kitchen = models.IntegerField(default=1)
    floors = models.IntegerField(default=1)
    parking = models.IntegerField(default=0)

    location = models.CharField(max_length=100, blank=True)
    house_type = models.CharField(max_length=100, blank=True)
    furnishing = models.CharField(max_length=100, blank=True)

    house_plan = models.FileField(
        upload_to="house_plans/",
        blank=True,
        null=True
    )

    predicted_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.predicted_price}"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name