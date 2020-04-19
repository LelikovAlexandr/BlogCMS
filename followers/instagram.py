import os
from time import sleep

from django.core.cache import cache
from dotenv import load_dotenv
from igramscraper.instagram import Instagram

from propitanie.settings import BASE_DIR

load_dotenv()


def login():
    instagram = Instagram()

    instagram.with_credentials(os.getenv('INSTAGRAM_LOGIN'),
                               os.getenv('INSTAGRAM_PASSWORD'),
                               os.path.join(BASE_DIR, 'cache',
                                            'instagram/'))
    instagram.login(force=False, two_step_verificator=True)

    sleep(2)
    return instagram


def get_followers():
    if cache.get('followers') is None:
        instagram = login()
        username = os.getenv('INSTAGRAM_USER')
        account = instagram.get_account(username)
        sleep(1)
        followers = instagram.get_followers(account.identifier,
                                            account.followed_by_count)
        result = []
        for follower in followers['accounts']:
            result.append(follower.username)
        cache.set('followers', set(result), 300)
    return cache.get('followers')
