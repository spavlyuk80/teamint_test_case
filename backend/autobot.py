from dotenv import load_dotenv
load_dotenv()

import yaml
import os
from loguru import logger
import string
import requests
import csv
import random
import json
import uuid

# my imports
from bot.errors import *
from bot.models import *




class Autobot:

    base_url = f"http://localhost:{os.getenv('DEFAULT_PORT','8079')}/api/"

    def __init__(self):

        # read settings file

        config = './config.yaml'

        if os.path.exists(config):
            logger.info("found existing config")
        else:
            logger.warning("could not find config")
            return

        with open(config) as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)

        defaults = {
            'number_of_users': 3,
            'max_post_per_user': 100,
            'max_likes_per_user': 100
        }

        for key, value in defaults.items():
            param = settings.get(key)
            if param is None or not isinstance(param, int):
                logger.warning(
                    f'<{param}>is not found, defaulting to {value}')
                # setattr(self, key, value)
            else:
                # setattr(self, key, param)
                defaults[key] = param

        # load csv file with companies data
        with open('links.csv', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)

        self.links = [i[0] for i in data]

        # init users

        logger.info(f'Using settings\n{defaults}')

        self.users = UserList(links = self.links, settings = defaults)

    def run(self):

        # generate posts
        self.users.generate_posts()
        self.users.like_posts()
        
        

    # def run(self):
    #     self._generate_users()
    #     self.created_users.make_posts(max_post_per_user=self.max_post_per_user)
    #     # self._create_posts()

    # def _get_token(self, user, refresh_token=None):

    #     url = self.base_url + "token/"

    #     if refresh_token is not None:
    #         url = url + "refresh"
    #         body = {'refresh': refresh_token}

    #     else:
    #         body = user.dict(include={'username':..., 'password':...})

    #     response = requests.post(url=url, json=body)

    #     if response.status_code == 200:
    #         access_token = json.loads(response.text).get('access')
    #         if access_token is None:
    #             raise UserLoginError
    #     else:
    #         raise UserLoginError

    # def _create_posts(self):
    #     """
    #     makes a post
    #     """
    #     for user in self.created_users:

    #         this_user_posts = random.randint(1, self.max_post_per_user)
    #         user['posts'] = []
    #         user['posts_count'] = 0

    #         for i in range(this_user_posts):  # max attemts
    #             post_message = ''.join(random.choices(
    #                 string.ascii_letters + string.digits, k=150))

    #             try:
    #                 access_token = self._get_token(user)
    #             except UserLoginError:
    #                 logger.error("Experiencing UserLoginError")
    #                 raise AutoBotError

    #             url = self.base_url + 'post/'
    #             headers = {'Authorization': 'Bearer '+access_token}
    #             body = {"post": post_message}

    #             response = requests.post(url=url, headers=headers, json=body)
    #             user['posts'].append(json.loads(response.text))
    #             user['posts_count'] += 1
    #             # TODO: handle response errors

    # def _like_posts(self):
    #     """
    #     script to like the posts
    #     """

    #     pass

    # def _create_user(self, user: User) -> bool:
    #     """
    #     creates user in the social network
    #     """
    #     url = self.base_url + "user/create/"
    #     body = user.dict()

    #     logger.info(f"logging in user \n{user}")
    #     logger.debug(f"using {url}")
    #     response = requests.post(url=url, json=body)
    #     if response.status_code == 201:
    #         return True
    #     elif response.status_code == 400:
    #         logger.info("there was an error, likely not a valid email, try another")
    #         return False
    #     else:
    #         logger.warning(f"Could not create user {user}")
    #         return False

    # def _get_some_users(self) -> UserList:
    #     random_domain = random.choice(self.links)
    #     results = requests.get(
    #         f"https://api.hunter.io/v2/domain-search?domain={random_domain}"
    #         f"&api_key={os.getenv('HUNTERIO_API_KEY')}")

    #     if results.status_code != 200:
    #         logger.warning(results.text)
    #         raise HunterError("Hunterio connection error")

    #     else:
    #         # TODO: can fail
    #         e = json.loads(results.text).get('data')
            
    #         if e is None:
    #             return []
            
    #         e = e.get("emails")
    #         if e is not None:
    #             user_list = UserList()
    #             for i in e:
    #                 val = i.get("value")
    #                 if val is not None:
    #                     user_list.append(
    #                         User(username=val, email=val,
    #                                 password = str(uuid.uuid4()))
    #                                 )
    #             return user_list

    #     # not really necessasy
    #     return UserList()

    # def _generate_users(self):
    #     """
    #     generates and registers users up to max number_of_users
    #     """

    #     success_counter = 0
    #     created_users = UserList()
    #     hunter_attempts = 0
    #     hunter_max_attempts = 3

    #     while success_counter < self.number_of_users:
    #         try:
    #             users = self._get_some_users()
    #         except HunterError:
    #             hunter_attempts += 1
    #             if hunter_attempts >= hunter_max_attempts:
    #                 logger.error("reached max retries to connect to hunterio\
    #                             will stop")
    #                 raise AutoBotError("TERMINTATING")
    #             users = []

    #         for user in users:
    #             created = self._create_user(user)
    #             if created:
    #                 created_users.append(user)
    #                 success_counter += 1
    #             if len(created_users) >= self.number_of_users:
    #                 break

    #     self.created_users = created_users
    #     logger.info(f"successfully created {self.number_of_users} users")

if __name__ == '__main__':
    bot = Autobot()

    bot.run()
