from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from . models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required

# Create your views here.

# @login_required


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_of_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genres = Genre.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_of_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "num_visits": num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    # model = Book
    # context_object_name = "book_list" # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains="harry")[:5] # Get 5 books containing the title harry
    # template_name = "book/book_list.html" # Specify your own template name/location

    # OR you can override some methods
    def get_queryset(self):
        # return Book.objects.filter(title__icontains="harry")[:5] # Get 5 books containing te title harry
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        # call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context["some_data"] = "This is just some data"
        return context

    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user).filter(
                status__exact='o').order_by('due_back')
        )
        
class LoanedBooksListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing all books loaned out from the library."""  
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'  
    paginate_by = 10
    
    def get_queryset(self):
        return (
            BookInstance.objects.all().filter(
                status__exact='o').order_by('due_back')
        )
