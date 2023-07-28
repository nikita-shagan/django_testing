from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_news_page_availability_for_anonymous_user(
    client, news, news_detail_url
):
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('comment_edit_url'),
        pytest.lazy_fixture('comment_delete_url')
    )
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, url, comment, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    comment_url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={comment_url}'
    response = client.get(comment_url)
    assertRedirects(response, redirect_url)
