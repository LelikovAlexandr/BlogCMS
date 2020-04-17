from igramscraper.instagram import Instagram
from time import sleep
from django.core.cache import cache
import os
from dotenv import load_dotenv
from propitanie.settings import BASE_DIR

load_dotenv()


def inst():
    if cache.get('instagram') is None:
        instagram = Instagram()

        instagram.with_credentials(os.getenv('INSTAGRAM_LOGIN'),
                                   os.getenv('INSTAGRAM_PASSWORD'),
                                   os.path.join(BASE_DIR, 'cache',
                                                'instagram/'))
        instagram.login(force=False, two_step_verificator=False)

        sleep(2)

        username = os.getenv('INSTAGRAM_USER')
        account = instagram.get_account(username)
        sleep(1)
        followers = instagram.get_followers(account.identifier,
                                            account.followed_by_count)
        result = []
        for follower in followers['accounts']:
            result.append(follower.username)
        cache.set('instagram', set(result), 300)
    return cache.get('instagram')
