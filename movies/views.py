from django.db.models import Value, FloatField, Count
from django.db.models.functions import Length, Lower, Replace
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MovieRequest, MoviePetition, MoviePetitionVote
from .forms import MovieRequestForm, MoviePetitionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

@login_required
def movie_requests(request):
    """
    Single page where a user can:
      - submit a new movie request (name + description)
      - see all of their own requests
      - delete a request they made
    """
    # Handle delete from the same page
    if request.method == "POST" and "delete_id" in request.POST:
        obj = get_object_or_404(MovieRequest, pk=request.POST.get("delete_id"), user=request.user)
        obj.delete()
        messages.success(request, "Request deleted.")
        return redirect("movies.requests")

    # Handle create
    if request.method == "POST":
        form = MovieRequestForm(request.POST)
        if form.is_valid():
            MovieRequest.objects.create(
                user=request.user,
                name=form.cleaned_data["name"].strip(),
                description=form.cleaned_data["description"].strip(),
            )
            messages.success(request, "Request submitted. Thanks!")
            return redirect("movies.requests")
    else:
        form = MovieRequestForm()

    my_requests = MovieRequest.objects.filter(user=request.user)
    return render(
        request,
        "movies/requests.html",
        {"form": form, "my_requests": my_requests},
    )


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


def movie_petitions(request):
    """
    Display all movie petitions with vote counts.
    Users can create new petitions and vote on existing ones.
    """
    # Handle voting
    if request.method == "POST" and "vote_petition_id" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to vote.")
            return redirect("movies.petitions")
        
        petition_id = request.POST.get("vote_petition_id")
        petition = get_object_or_404(MoviePetition, pk=petition_id)
        
        # Check if user already voted
        if petition.user_has_voted(request.user):
            messages.warning(request, "You have already voted on this petition.")
        else:
            # Create vote
            MoviePetitionVote.objects.create(user=request.user, petition=petition)
            messages.success(request, f"Your vote for '{petition.name}' has been recorded!")
        
        return redirect("movies.petitions")
    
    # Handle petition creation
    if request.method == "POST" and "create_petition" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to create a petition.")
            return redirect("movies.petitions")
        
        form = MoviePetitionForm(request.POST)
        if form.is_valid():
            MoviePetition.objects.create(
                user=request.user,
                name=form.cleaned_data["name"].strip(),
                description=form.cleaned_data["description"].strip(),
            )
            messages.success(request, "Petition created successfully!")
            return redirect("movies.petitions")
    else:
        form = MoviePetitionForm()
    
    # Get all petitions with vote counts and check if current user has voted
    petitions = MoviePetition.objects.annotate(vote_count=Count('votes')).order_by('-vote_count', '-created_at')
    
    # Add user vote status to each petition
    for petition in petitions:
        petition.user_has_voted = petition.user_has_voted(request.user)
    
    template_data = {
        'title': 'Movie Petitions',
        'form': form,
        'petitions': petitions,
    }
    return render(request, 'movies/petitions.html', {'template_data': template_data})