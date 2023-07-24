import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from . models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
from catalog.forms import RenewBookForm

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


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this a POST request, then process the form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL
            return HttpResponseRedirect(reverse('all-borrowed'))

        # If this is GET (or any other method) create the default form
        else:
            proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
            form = RenewBookForm(
                initial={'renewal_date': proposed_renewal_date})

            context = {
                'form': form,
                'book_instance': book_instance,
            }

            return render(request, 'catalog/book_renew_librarian.html', context)
