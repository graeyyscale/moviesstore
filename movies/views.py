from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Value, FloatField
from django.db.models.functions import Length, Lower, Replace
def index(request):

    search_term = request.GET.get('search')

    if search_term:

        movies = Movie.objects.filter(name__icontains=search_term)

    else:

        movies = Movie.objects.all()

    template_data = {}

    template_data['title'] = 'Movies'

    template_data['movies'] = movies

    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):

    movie = Movie.objects.get(id=id)

    reviews = Review.objects.filter(movie=movie)

    template_data = {}

    template_data['title'] = movie.name

    template_data['movie'] = movie

    template_data['reviews'] = reviews

    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required

def create_review(request, id):

    if request.method == 'POST' and request.POST['comment'] != '':

        movie = Movie.objects.get(id=id)

        review = Review()

        review.comment = request.POST['comment']

        review.movie = movie

        review.user = request.user

        review.save()

        return redirect('movies.show', id=id)

    else:

        return redirect('movies.show', id=id)
    
@login_required

def edit_review(request, id, review_id):

    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:

        return redirect('movies.show', id=id)

    if request.method == 'GET':

        template_data = {}

        template_data['title'] = 'Edit Review'

        template_data['review'] = review

        return render(request, 'movies/edit_review.html', {'template_data': template_data})

    elif request.method == 'POST' and request.POST['comment'] != '':

        review = Review.objects.get(id=review_id)

        review.comment = request.POST['comment']

        review.save()

        return redirect('movies.show', id=id)

    else:

        return redirect('movies.show', id=id)
    
@login_required

def delete_review(request, id, review_id):

    review = get_object_or_404(Review, id=review_id, user=request.user)

    review.delete()

    return redirect('movies.show', id=id)


def top_comments(request):
    """
    Show 'top' comments across all movies, ranked by a simple funny score:
    counts of 'lol', 'haha', 'lmao' (case-insensitive) and emojis 😂 🤣.
    Ties fall back to newest first.
    """
    lc = Lower('comment')
    total_len_lc = Length(lc)
    total_len = Length('comment')
    # Count occurrences via the REPLACE length-delta trick, then normalize by token length
    lol_score  = (total_len_lc - Length(Replace(lc, Value('lol'),  Value('')))) / Value(3.0)
    haha_score = (total_len_lc - Length(Replace(lc, Value('haha'), Value('')))) / Value(4.0)
    lmao_score = (total_len_lc - Length(Replace(lc, Value('lmao'), Value('')))) / Value(4.0)
    tears_score = (total_len - Length(Replace('comment', Value('😂'), Value(''))))  # per char
    rofl_score  = (total_len - Length(Replace('comment', Value('🤣'), Value(''))))  # per char
    funny_score = lol_score + haha_score + lmao_score + tears_score + rofl_score

    reviews_qs = (
        Review.objects.select_related('user', 'movie')
        .annotate(funny_score=funny_score)
        .order_by('-funny_score', '-date')[:50]
    )

    template_data = {
        'title': 'Top Comments',
        'reviews': reviews_qs,
    }
    return render(request, 'movies/top_comments.html', {'template_data': template_data})