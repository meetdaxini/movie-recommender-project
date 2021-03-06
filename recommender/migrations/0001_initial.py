# Generated by Django 3.1.3 on 2020-11-17 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('imdbID', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('Title', models.CharField(max_length=100)),
                ('Poster', models.URLField()),
                ('Year', models.IntegerField()),
                ('imdbRating', models.FloatField()),
                ('rotten_tomatoes', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Related_Movie',
            fields=[
                ('movieID', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recommender.movie')),
                ('related_movie', models.ManyToManyField(related_name='rel_movs', to='recommender.Movie')),
            ],
        ),
    ]
