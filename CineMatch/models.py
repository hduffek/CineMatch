from django.db import models


class Questionnaire(models.Model):
    genre_select = models.CharField(max_length=100, choices=(
        ('', '----------------------'),
        ('HORROR', 'Horror'),
        ('ROMANCE', 'Romance'),
        ('COMEDY', 'Comedy'),
        ('ACTION', 'Action'),
        ('DOCUMENTARY', 'Documentary'),
    ))
    actor_select = models.CharField(max_length=200)
    director_select = models.CharField(max_length=200)
    rating_select = models.CharField(max_length=100, choices=(
        ('', '----------------------'),
        ('LOWEST', 'Lowest First'),
        ('HIGHEST', 'Highest First'),
        ('NO_PREFERENCE', 'No Preference'),
    ))

    def __str__(self):
        return f"Questionnaire {self.pk}"