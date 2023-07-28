from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news, news_detail_url, news_form_data
):
    initial_comments_count = Comment.objects.count()
    client.post(news_detail_url, data=news_form_data)
    assert Comment.objects.count() == initial_comments_count


def test_user_can_create_comment(
        author, author_client, news, news_detail_url, news_form_data
):
    initial_comments_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=news_form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == initial_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == news_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
    bad_words_data, admin_client, news_detail_url
):
    initial_comments_count = Comment.objects.count()
    response = admin_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == initial_comments_count


def test_author_can_delete_comment(
    author_client, comment, comment_delete_url, news_comments_url
):
    initial_comments_count = Comment.objects.count()
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, news_comments_url)
    assert Comment.objects.count() == initial_comments_count - 1


def test_user_cant_delete_comment_of_another_user(
    admin_client, comment_delete_url
):
    initial_comments_count = Comment.objects.count()
    response = admin_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comments_count


def test_author_can_edit_comment(
    author, author_client, comment_edit_url, updated_news_form_data,
    news_comments_url, news, comment
):
    response = author_client.post(
        comment_edit_url, data=updated_news_form_data
    )
    assertRedirects(response, news_comments_url)
    comment.refresh_from_db()
    assert comment.text == updated_news_form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment_edit_url, updated_news_form_data, comment,
    news_form_data, author, news
):
    response = admin_client.post(comment_edit_url, data=updated_news_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == news_form_data['text']
    assert comment.author == author
    assert comment.news == news
