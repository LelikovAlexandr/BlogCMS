import os
from time import sleep

from django.core.cache import cache
from dotenv import load_dotenv
from igramscraper.instagram import Instagram

from config.settings import BASE_DIR

load_dotenv()

proxies = {
    'http': os.getenv('INSTAGRAM_PROXY'),
    'https': os.getenv('INSTAGRAM_PROXY'),
}


def login():
    instagram = Instagram()
    instagram.set_proxies(proxies)

    instagram.with_credentials(os.getenv('INSTAGRAM_LOGIN'),
                               os.getenv('INSTAGRAM_PASSWORD'),
                               os.path.join(BASE_DIR, 'cache', 'instagram/'))
    instagram.login()

    sleep(2)
    return instagram


def get_followers():
    if cache.get('followers') is None:
        instagram = login()
        account = instagram.get_account(os.getenv('INSTAGRAM_USER'))
        sleep(1)
        followers = instagram.get_followers(account.identifier,
                                            account.followed_by_count)
        result = []
        for follower in followers['accounts']:
            result.append(follower.username)
        cache.set('followers', set(result), 300)
    return cache.get('followers')
