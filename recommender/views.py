from django.shortcuts import render, redirect
from django.http import JsonResponse
from requests import get
import json
from .models import Movie
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import environ
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(BASE_DIR,  ".env")
env = environ.Env()
env.read_env(env_file)

# Create your views here.


def get_trending_from_tmdb():
    baseurl = "https://api.themoviedb.org/3/trending/movie/day"
    par = {}
    par["api_key"] = env('TMDB_API')
    trend_req = get(baseurl, params=par)
    trend_movies_dicts = trend_req.json()
    print(trend_movies_dicts)
    trend_movies = []
    for result in trend_movies_dicts['results']:
        trend_movie = [{'Title': result['title'], 'Poster':  'http://image.tmdb.org/t/p/w300' +
                        result['poster_path'], 'Year': result['release_date'], 'imdbRating': 0, 'rotten_tomatoes': 0}]
        trend_movies += trend_movie
    return trend_movies


def get_movies_from_tastedive(mov):
    baseurl = "https://tastedive.com/api/similar"
    par = {}
    par["q"] = mov
    par["k"] = env('TASTE_API')
    par["limit"] = "16"
    par["type"] = "movie"
    sim_req = get(baseurl, params=par)
    similar_movies = sim_req.json()
    sim16 = [movie["Name"] for movie in similar_movies["Similar"]["Results"]]
    return sim16


def get_movie_data(mov):
    baseurl = "http://www.omdbapi.com/"
    par = {}
    par["apikey"] = env('OMDB_API')
    par["t"] = mov
    par["r"] = "json"
    movie_data = get(baseurl, params=par)
    md = movie_data.json()
    if md['Response'] == 'True':
        required_md = [md['imdbID'], md['Title'], md['Poster'], md['Year']]
        for rating in md["Ratings"]:
            if rating['Source'] == "Internet Movie Database":
                required_md += [float(rating["Value"][:3])]

            elif rating['Source'] == "Rotten Tomatoes":
                required_md += [int(rating["Value"][:-1])]
        if len(required_md) < 6:
            for i in range(6-len(required_md)):
                required_md += [0]

    else:
        required_md = 0

    return required_md


def home(request):
    params = {}
    try:
        trending_movies = get_trending_from_tmdb()
        # print(trending_movies)
        params['many_movies'] = trending_movies
    except:
        pass
    return render(request, 'recommender/home.html', params)


def recommender(request):
    if 'movie' in request.GET:
        movie = request.GET['movie']

        # from db
        try:
            search_movie = Movie.objects.get(Title__iexact=movie)
            # print(search_movie.Title, 'found in db')

        except MultipleObjectsReturned:
            search_movie = Movie.objects.filter(
                Title__iexact=movie).order_by('-imdbRating').first()

        # from api
        except ObjectDoesNotExist:
            added_movie = get_movie_data(movie)
            if not added_movie:
                params = {'movie_name': movie,
                          'no_movie': "No Movie found for you query '" + movie + "'"}
                return render(request, 'recommender/recommender.html', params)
            search_movie = Movie(imdbID=added_movie[0], Title=added_movie[1], Poster=added_movie[2],
                                 Year=added_movie[3][:4], imdbRating=added_movie[4], rotten_tomatoes=added_movie[5])
            search_movie.save()
            # print(search_movie.Title, 'found in api')
        get_movie_recommendations = get_movies_from_tastedive(
            search_movie.Title)
        # print(get_movie_recommendations)
        related_movies = []
        for title in get_movie_recommendations:
            # from db
            try:
                db_related_mv = Movie.objects.get(Title__iexact=title)
                # print(db_related_mv.Title, 'found related in  db')
                related_movies += [db_related_mv]

            except MultipleObjectsReturned:
                db_related_mv = Movie.objects.filter(
                    Title__iexact=title).order_by('-imdbRating').first()
                # print(db_related_mv.Title, 'found related in  double db')
                related_movies += [db_related_mv]

            # from api
            except ObjectDoesNotExist:
                related_movie_data = get_movie_data(title)
                if related_movie_data:
                    new_related_mv = Movie(imdbID=related_movie_data[0], Title=related_movie_data[1], Poster=related_movie_data[2],
                                           Year=related_movie_data[3][:4], imdbRating=related_movie_data[4], rotten_tomatoes=related_movie_data[5])
                    new_related_mv.save()
                    # print(new_related_mv.Title, 'found related in api')
                    related_movies += [new_related_mv]
                else:
                    continue

        params = {'movie_name': movie, 'search_movie': search_movie,
                  'many_movies': related_movies}
        return render(request, 'recommender/recommender.html', params)
    else:
        return redirect('recommender:home')


def auto_complete(request):
    search = request.GET.get('term')
    # print(search)
    if len(search) < 3:
        movie_objects = Movie.objects.filter(Title__istartswith=search)
    else:
        movie_objects = Movie.objects.filter(Title__icontains=search)
    movies = [movie.Title for movie in movie_objects][:15]
    movies_json = JsonResponse(movies, safe=False)
    return movies_json
