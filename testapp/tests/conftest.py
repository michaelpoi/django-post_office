import multiprocessing
import pytest
import os

from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


@pytest.fixture
def admin_user(db):
    UserModel = get_user_model()
    admin_user = UserModel.objects.get(username='admin')
    return admin_user


@pytest.fixture(scope='session', autouse=True)
def init_multiprocessing():
    multiprocessing.set_start_method('fork')
