from django.contrib import admin
from .models import Author, Genre, Language, Book, BookInstance

# Register your models here.

# Define the Admin classes for Author
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "date_of_death")


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

# Define the Admin classes for Book
# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")

# Define the Admin classes for BookInstance
# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ("status", "due_back")


admin.site.register(Genre)
admin.site.register(Language)
