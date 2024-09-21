import pandas as pd

from reviews.models import Category, Comment, GenreTitle, Genre, Review, Title, User

for index, row in pd.read_csv('static/data/category.csv').iterrows():
    category = Category(
        name=row['name'],
        id=row['id'],
        slug=row['slug']
    )
    category.save()

for index, row in pd.read_csv('static/data/genre.csv').iterrows():
    genre = Genre(
        name=row['name'],
        id=row['id'],
        slug=row['slug']
    )
    genre.save()

for index, row in pd.read_csv('static/data/titles.csv').iterrows():
    title = Title(
        name=row['name'],
        id=row['id'],
        year=row['year'],
        category=Category.objects.get(pk=row['category'])
    )
    title.save()

for index, row in pd.read_csv('static/data/genre_title.csv').iterrows():
    genre_title = GenreTitle(
        id=row['id'],
        title=Title.objects.get(pk=row['title_id']),
        genre=Genre.objects.get(pk=row['genre_id'])
    )
    genre_title.save()

for index, row in pd.read_csv('static/data/users.csv').iterrows():
    user = User(
        id=row['id'],
        username=row['username'],
        email=row['email'],
        role=row['role'],
        bio=row['bio'],
        first_name=row['first_name'],
        last_name=row['last_name']
    )
    user.save()

for index, row in pd.read_csv('static/data/review.csv').iterrows():
    review = Review(
        id=row['id'],
        title=Title.objects.get(pk=row['title_id']),
        text=row['text'],
        author=User.objects.get(pk=row['author']),
        score=row['score'],
        pub_date=row['pub_date']
    )
    review.save()

for index, row in pd.read_csv('static/data/comments.csv').iterrows():
    comment = Comment(
        id=row['id'],
        review=Review.objects.get(pk=row['review_id']),
        text=row['text'],
        author=User.objects.get(pk=row['author']),
        pub_date=row['pub_date']
    )
    comment.save()
