from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone


class Movie(models.Model):

    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)

    price = models.IntegerField()

    description = models.TextField()

    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):

        return str(self.id) + ' - ' + self.name
    
class Review(models.Model):

    id = models.AutoField(primary_key=True)

    comment = models.CharField(max_length=255)

    date = models.DateTimeField(auto_now_add=True)

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):

        return str(self.id) + ' - ' + self.movie.name
    

class MovieRequest(models.Model):
    """
    A user's request for a movie to be added to the store.
    Only the requesting user can see/delete their own requests.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="movie_requests",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} (by {self.user})"