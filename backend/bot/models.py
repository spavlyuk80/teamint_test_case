from typing import Union, Tuple, List

from pydantic import BaseModel
import requests
import json
import uuid
import os
import random
from loguru import logger
from bot.errors import *


class ApiInterface:
    """ Basis Api Interface to interact with backend """
    base_url = f"http://localhost:{os.getenv('DEFAULT_PORT', '8079')}/api/"

    def call_api(self, **kwargs) -> Tuple[any, int]:
        if 'http' not in kwargs['path']:
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

    def __str__(self):
        return f"Post: {self.id}, likes: {len(self.likes)}"

    def __repr__(self):
        return f"Post: {self.id}, likes: {len(self.likes)}"

    @property
    def likes_count(self) -> int:
        """ Returns likes count of this post"""
        return len(self.likes)

    def get_post(self) -> dict:
        """ returns post contents """
        return {"post": self.contents}

    def do_post(self, api, user, retry=True):
        """ Makes post to api """
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

    def like_my_random_post(self, user, api, retry=True) -> None:
        """ Store user that liked this post """

        user.login_me(api)
        path = f'post/{self.id}/like/'
        with api as api:
            method = 'POST'
            headers = user.get_login_header()
            response, status = api.call_api(path=path, method=method, headers=headers)

            if status == 200:
                self.likes.append(user.email)
                logger.info(f"Liked post with {self.id} for {user.username}")
            else:
                if retry is True:
                    self.like_my_random_post(api=api, user=user, retry=False)
                else:
                    raise AutoBotError(f"error liking post")


class User(BaseModel):
    """User class"""
    username: str = None
    email: str = None
    password: str = str(uuid.uuid4())
    posts: list = []  # list of post instances
    max_posts: int = 0  # max posts user can make
    signed_in: bool = False  # is user signed in
    access: str = "a"  # my access token
    refresh: str = "a"  # my refresh token
    my_likes: list = []  # stores ids of posts I liked

    def __str__(self):
        return f"user: {self.username}"

    def __repr__(self):
        return f"User: {self.username}"

    @property
    def my_likes_count(self) -> int:
        """Returns number of posts user liked"""
        return len(self.my_likes)

    @property
    def posts_count(self) -> int:
        """Returns number of posts user made"""
        return len(self.posts)

    def has_posts_with_zero_likes(self) -> bool:
        """ Returns amount of posts user has with zero likes"""
        return True if len([i for i in self.posts if i.likes_count == 0]) > 0 else False

    def create_me(self, api, **kwargs):
        """Function that creates a user"""
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
        """Returns login header"""
        return {'Authorization': 'Bearer ' + self.access}

    def generate_posts(self, api, max_posts):
        """Generates posts for the user """
        self.max_posts = random.randint(1, max_posts)
        for i in range(self.max_posts):
            post = Post()
            created_post = post.do_post(api=api, user=self)
            self.posts.append(created_post)

    def login_me(self, api):
        """
        logins user, returns token
        """
        with api as api:
            self._get_token(api=api)

    def _get_token(self, api, refresh_token=True, break_on_error=False):
        """Recursively returns access token"""
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
    """Manages the list of users"""
    api = ApiInterface() # api connection

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
        """Generates users according up to number of users setting"""
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
        gets some users data
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
        """ Generates posts for the userlist """

        for i in range(len(self)):
            self[i].generate_posts(
                api=self.api,
                max_posts=self.max_post_per_user
            )

    def get_id_of_next_user_to_post(self) -> Union[int, None]:
        """
        returns id of the user that should like the post next
        """
        users_with_no_max_likes = [
            i for i in sorted(self, key=lambda x: x.my_likes_count, reverse=True)  # returns new list
            if i.my_likes_count < self.max_likes_per_user
        ]

        if len(users_with_no_max_likes) > 0:
            return self.index(users_with_no_max_likes[0])
        else:
            return None

    def get_sorted_ids(self) -> Union[List[int], None]:
        """
        returns indices of sorted users that should like the post next
        """
        users_with_no_max_likes = [
            i for i in sorted(self, key=lambda x: x.my_likes_count, reverse=True)  # returns new list
            if i.my_likes_count < self.max_likes_per_user
        ]

        if len(users_with_no_max_likes) > 0:

            indices = []
            for u in users_with_no_max_likes:
                for i in range(len(self)):
                    if u == self[i]:
                        indices.append(i)
            # return [self.index(i) for i in users_with_no_max_likes]
            return indices
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

            # if there are no users with posts with zero likes then stop
            if len([i for i in self if i.has_posts_with_zero_likes()]) == 0:
                logger.info("There are no posts with zero likes, finished")
                break

            """
            The logics in the task is not correct, since if we always choose the user with max posts
            and he has not reached max likes, nothing will happen if he does not have any posts to like
            therefore I will amend it
            """

            # get user_id that should like next, stop if all users reached max likes
            # user_id = self.get_id_of_next_user_to_post()
            # if user_id is None:
            #     logger.info(f"No more users to like the posts")
            #     break

            sorted_user_ids = self.get_sorted_ids()

            if sorted_user_ids is None:
                logger.info(f"No more users to like the posts")
                break

            # try to like something
            # self.do_like(with_user_id=user_id)

            for indx in sorted_user_ids:
                self.do_like(with_user_id=indx)

        self.print_summary()
        logger.info("Completed liking posts")

    def print_summary(self):
        """prints summary"""
        #### PRINT SUMMARY
        print(" >>>>>>>>>>>>>>>>> SUMMARY <<<<<<<<<<<<<<<<")
        print("              ------USERS------ ")
        for u in self:
            print(f"{u}, made {len(u.posts)} posts, made {len(u.my_likes)} likes")

        print("            ------- POSTS --------")
        # get posts
        posts = []
        for u in self:
            posts.extend(u.posts)
        for post in posts:
            print(post)

    def do_like(self, with_user_id):
        """
        makes user with user id to like a post
        """
        logger.info(f">>>>>>>>>>>>>>>>>> begin liking algo <<<<<<<<<<<<<<<<<<<<<<<<")
        # select user
        user: User = self[with_user_id]
        logger.info(f"{user} wants to like a post")

        posts_this_user_already_liked = user.my_likes

        # select all users which still have posts with zero likes and not of this user
        users_with_posts_with_zero_likes = [
                i for i in self if i.has_posts_with_zero_likes() and i != user
            ]

        if len(users_with_posts_with_zero_likes) == 0:
            logger.info(f"{user} cannot do anything since there are no other users with posts with zero likes")
            return
        else:
            logger.info(f"available users with posts that have zero likes\n{users_with_posts_with_zero_likes}")
        # select random user
        random_user = random.choice(users_with_posts_with_zero_likes)
        logger.info(f"{user} will like posts if {random_user}")
        # try liking any random post from "random user"
        random_post = random.choice(random_user.posts)
        logger.info(f"{user} wants to like {random_post}")
        # if this user already liked the post start over
        if random_post.id in posts_this_user_already_liked:
            logger.warning(f"{user} cannot like {random_post}, since he already liked it")
            return

        # if all is well, like the posts
        random_user_index = self.index(random_user)
        random_post_index = random_user.posts.index(random_post)

        self[random_user_index].posts[random_post_index].like_my_random_post(user, self.api)

        self[with_user_id].my_likes.append(random_post.id)
        logger.success(f"{user} successfully liked the post")
        return







