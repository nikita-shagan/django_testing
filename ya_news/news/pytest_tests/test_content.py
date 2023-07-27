import pytest
from django.urls import reverse

from yanews import settings

HOME_URL = reverse('news:home')


@pytest.mark.django_db
@pytest.mark.usefixtures('bulk_news')
def test_news_count(client):
    response = client.get(HOME_URL)
    news_count = len(response.context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('bulk_news')
def test_news_order(client):
    response = client.get(HOME_URL)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('bulk_comments')
def test_comments_order(client, news, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news, news_detail_url):
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(admin_client, news, news_detail_url):
    response = admin_client.get(news_detail_url)
    assert 'form' in response.context
