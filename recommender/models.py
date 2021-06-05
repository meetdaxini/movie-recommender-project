from django.db import models


class Movie(models.Model):
    imdbID = models.CharField(max_length=20, primary_key=True)
    Title = models.CharField(max_length=100)
    Poster = models.URLField()
    Year = models.IntegerField()
    imdbRating = models.FloatField()
    rotten_tomatoes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        punc = """!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""
        punc_free = self.Title
        for char in punc_free:
            if char in punc:
                punc_free = punc_free.replace(char, "")
            elif char == "-":
                punc_free = punc_free.replace(char, " ")

        return "_".join(punc_free.split(" "))
