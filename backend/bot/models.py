from typing import Union, Tuple

from pydantic import BaseModel
import requests
import json
import uuid
import os
import random
from loguru import logger
from bot.errors import *


class ApiInterface:
    base_url = f"http://localhost:{os.getenv('DEFAULT_PORT', '8079')}/api/"

    def call_api(self, **kwargs) -> Tuple[any, int]:
        if not 'http' in kwargs['path']:
            kwargs['url'] = self.base_url + kwargs['path']
        else:
            kwargs['url'] = kwargs['path']
        kwargs.pop('path')
        resp = requests.request(**kwargs)
        return json.loads(resp.text), resp.status_code

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class Post(BaseModel):
    id: int = None
    likes: list = []
    contents: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contents = ' '.join(str(uuid.uuid4()) for i in range(5))

    @property
    def likes_count(self) -> int:
        return len(self.likes)

    def get_post(self) -> dict:
        return {"post": self.contents}

    def do_post(self, api, user, retry=True):
        user.login_me(api)
        path = 'post/'
        with api as api:
            method = 'POST'
            js = self.get_post()
            headers = user.get_login_header()
            response, status = api.call_api(path=path, method=method, json=js, headers=headers)

            if status == 201:
                self.id = response.get('id')
                logger.info(f"created post with {self.id} for {user.username}")
            else:
                if retry is True:
                    self.do_post(api=api, user=user, retry=False)
                else:
                    raise AutoBotError(f"error making post")
        return self


class User(BaseModel):
    username: str = None
    email: str = None
    password: str = str(uuid.uuid4())
    posts: list = []
    max_posts: int = 0
    signed_in: bool = False
    access: str = "a"
    refresh: str = "a"
    likes: list = []

    def __str__(self):
        return f"user: {self.username}"

    @property
    def likes_count(self):
        return len(self.likes)

    def has_posts_with_zero_likes(self):
        return True if len([i for i in self.posts if i.likes_count == 0]) else False

    def create_me(self, api, **kwargs):

        with api as api:
            logger.info(f"logging in user \n{self}")
            response, status = api.call_api(path="user/create/", method="POST", json=self.dict(include={
                'username': ...,
                'password': ...,
                'email': ...}))

            if status == 201:
                self.signed_in = True
                return self, True
            elif status == 400:
                logger.info("there was an error, likely not a valid email, try another")
                return self, False
            else:
                logger.warning(f"Could not create user {self}")
                return self, False

    def get_login_header(self):
        return {'Authorization': 'Bearer ' + self.access}

    def generate_posts(self, api, max_posts):

        self.max_posts = random.randint(1, max_posts)
        for i in range(self.max_posts):
            post = Post()
            created_post = post.do_post(api=api, user=self)
            self.posts.append(created_post)

    def login_me(self, api):
        """
        logs user, returns token
        """
        with api as api:
            self._get_token(api=api)

    def _get_token(self, api, refresh_token=True, break_on_error=False):
        method = 'POST'

        if refresh_token:
            path = 'token/refresh/'
            js = {'refresh': self.refresh}
        else:
            path = 'token/'
            js = self.dict(include={'username': ..., 'password': ...})

        with api as api:

            response, status = api.call_api(
                method=method, path=path,
                json=js)

            if status != 200:
                if break_on_error:
                    raise AutoBotError(f"could not get token for {self}")
                self._get_token(api=api, refresh_token=False, break_on_error=True)
            else:
                self.refresh = response.get('refresh')
                self.access = response.get('access')
                logger.info(f"token updated for {self}")


class UserList(list):
    api = ApiInterface()

    def __init__(self, **kwargs):
        """This class creates and manages user list
        
        Requires:
            - links: list - import from csv file with some domain names
            - settings: dict - settings for the autobot
        """

        super().__init__()
        self.max_likes_per_user = None
        self.max_post_per_user = None
        self.number_of_users = None
        self.links = kwargs.get('links')

        for k, v in kwargs.get('settings').items():
            setattr(self, k, v)

        self._generate_users()

    def _generate_users(self):

        success_counter = 0
        hunter_attempts = 0
        hunter_max_attempts = 3

        while success_counter < self.number_of_users:
            try:
                users = self._get_some_users()
            except HunterError:
                hunter_attempts += 1
                if hunter_attempts >= hunter_max_attempts:
                    logger.error("reached max retries to connect to hunterio\
                                will stop")
                    raise AutoBotError("TERMINTATING")
                users = []

            for user in users:
                new_user, created = user.create_me(self.api)

                if created:
                    self.append(new_user)
                    success_counter += 1
                if len(self) >= self.number_of_users:
                    break
        logger.info(f"successfully created {self.number_of_users} users")

    def _get_some_users(self) -> list:
        """
        """
        random_domain = random.choice(self.links)
        hunter_path = (f"https://api.hunter.io/v2/domain-search?"
                       f"domain={random_domain}"
                       f"&api_key={os.getenv('HUNTERIO_API_KEY')}")

        response, status = self.api.call_api(method='GET', path=hunter_path)
        if status != 200:
            logger.warning(response)
            raise HunterError("Hunterio connection error")
        else:
            emails = response.get('data')

            if emails is None:
                return []

            emails = emails.get('emails')

            if emails is None:
                return []

            user_list = []

            for email in emails:
                email_val = email.get('value')
                if email_val is not None:
                    user_list.append(User(username=email_val, email=email_val))

            return user_list

    def generate_posts(self) -> None:

        for i in range(len(self)):
            self[i].generate_posts(
                api=self.api,
                max_posts=self.max_post_per_user
            )

    def get_id_of_next_user_to_post(self) -> Union[int, None]:

        users_with_no_max_likes = [
            i for i in sorted(self, key=lambda x: x.likes_count, reverse=True) # returns new list
            if i.like_count < self.max_likes_per_user
        ]

        if len(users_with_no_max_likes) > 0:
            return self.index(users_with_no_max_likes[0])
        else:
            return None

    def like_posts(self):
        """
        Likes posts according to the following logics:
        next user to perform the like is the one with the most posts
        and which has not reached max likes

        then we select user whose posts to like (he needs to have at least one post with 0 likes)

        """
        while True:
            user_id = self.get_id_of_next_user_to_post()
            if user_id is None:
                logger.info(f"reached max likes per user")
                break

            self.do_like(with_user_id=user_id)

    def do_like(self, with_user_id):
        # select
        user = self[with_user_id]
        users_with_posts_with_zero_likes = [
            i for i in self if i.has_posts_with_zero_likes() and i != user and i.user
        ]


