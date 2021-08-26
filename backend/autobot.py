import yaml
import os
from loguru import logger
import string
import requests
import csv
import random
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

########################
## SOME CUSTOM ERRORS ##
########################

class HunterError(Exception):
    def __init__(self, msg=None):
        self.message = msg
        super().__init__(self.message)

class AutoBotError(Exception):
    pass

class UserLoginError(Exception):
    pass

class MakePostError(Exception):
    pass

######### END ########


class User(list):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def get_post


#### MAIN CLASS #####
class Autobot:

    base_url = 'http://127.0.0.1:8070/api/'

    def __init__(self):

        # read settings file
        with open('config.yaml') as f:
            settings = yaml.load(f, Loader=yaml.FullLoader)
        
        defaults = {
            'number_of_users': 10,
            'max_post_per_user': 100,
            'max_likes_per_user': 100
        }
        
        for key, value in defaults.items():
            param = settings.get(key)
            if param is None or not isinstance(param, int):
                logger.warning(
                    f'<{param}>is not found, defaulting to {value}')
                setattr(self, key, value)
            else:
                setattr(self, key, param)

        
        # load csv file with companies data
        with open('links.csv', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)

        self.links = [i[0] for i in data]

    
    def run(self):
        # self._generate_users()
        # self._create_posts()
        self._create_posts()

    def _get_token(self, user, refresh_token=None):
        
        url = self.base_url + "token/"
        
        if refresh_token is not None:
            url = url + "refresh"
            body = {'refresh':refresh_token}

        else:
            body={'username':user.get('username'),
                'password':user.get('password')}

        response = requests.post(url=url, json=body)

        if response.status_code == 200:
            access_token = json.loads(response.text).get('access')
            if access_token is None:
                raise UserLoginError
        else:
            raise UserLoginError
            

    def _create_posts(self):
        """
        makes a post
        """
        for user in self.created_users:

            this_user_posts = random.randint(1, self.max_post_per_user)
            user['posts'] = []
            user['posts_count'] = 0

            for i in range(this_user_posts): # max attemts
                post_message = ''.join(random.choices(string.ascii_letters + string.digits, k = 150))
                
                try:
                    access_token = self._get_token(user)
                except UserLoginError:
                    logger.error("Experiencing UserLoginError")
                    raise AutoBotError

                url = self.base_url + 'post/'
                headers = {'Authorization': 'Bearer '+access_token}
                body = {"post":post_message}

                response = requests.post(url=url, headers=headers, json=body)
                user['posts'].append(json.loads(response.text))
                user['posts_count'] += 1
                # TODO: handle response errors

    def _like_posts(self):
        """
        script to like the posts
        """

        while True:

            # get the user with most posts and has not reached max likes
            user = 


    def _create_user(self, user: dict) -> bool:
        """
        creates user in the social network
        """
        url = self.base_url + "user/create/"
        body = user

        logger.info(f"logging in user \n{user}")
        response = requests.post(url=url, json=body)
        if response.status_code == 200:
            return True
        else:
            return False


    def _get_some_users(self) -> list:
        random_domain = random.choice(self.links)
        results = requests.get(
            f"https://api.hunter.io/v2/domain-search?domain={random_domain}"\
                f"&api_key={os.getenv('HUNTERIO_API_KEY')}")
        
        if results.status_code != 200:
            logger.warning(results.text)
            raise HunterError("Hunterio connection error")

        else:
            e = json.loads(results.text).get('data', {}).get("emails")
            if e is not None:
                #parse email list
                e = [i.get("value")
                     for i in e if i.get("value") is not None]

                users = [
                    {'username': i,
                     'email': i,
                     'password': str(uuid.uuid4())}
                    for i in e]

                return users
        return []

    def _generate_users(self):
        """
        generates and registers users up to max number_of_users
        """

        success_counter = 0
        created_users = []
        hunter_attempts = 0
        hunter_max_attempts = 3

        while success_counter < self.number_of_users:
            try:
                users = self._get_some_users()
            except HunterError:
                hunter_attempts += 1
                if hunter_attempts >= hunter_max_attempts:
                    logger.error("reached max retries to connect to hunterio\
                    likely. will stop")
                    raise AutoBotError("TERMINTATING")
                users = []

            for user in users:
                created = self._create_user(user)
                if created:
                    created_users.append(user)
                    success_counter += 1
                if len(created_users) >= self.number_of_users:
                    break
        
        self.created_users = created_users
        if not self.error:
            logger.info(f"successfully created {self.number_of_users} users")
        else:
            logger.error("returned error")
            




        



if __name__ == '__main__':
    bot = Autobot()
    bot.run()

