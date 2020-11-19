from django.db import models

# Create your models here.
class Movie(models.Model):
    imdbID = models.CharField(max_length=20, primary_key=True)
    Title = models.CharField(max_length=100)
    Poster = models.URLField()
    Year = models.IntegerField()
    imdbRating = models.FloatField()
    rotten_tomatoes = models.IntegerField()

    def __str__(self):
        return self.Title
