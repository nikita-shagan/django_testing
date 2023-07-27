from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import News, Comment
from yanews import settings


@pytest.fixture
def news():
    return News.objects.create(title='Title', text='Text')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment text'
    )


@pytest.fixture
def bulk_news():
    today = datetime.today()
    News.objects.bulk_create([
        News(
            title=f'News {index}',
            text='Text',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def bulk_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Text {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_comments_url(news_detail_url):
    return news_detail_url + '#comments'


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def form_data():
    return {'text': 'Comment text'}


@pytest.fixture
def new_form_data():
    return {'text': 'New comment text'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Some text, {BAD_WORDS[0]}, and more text'}
