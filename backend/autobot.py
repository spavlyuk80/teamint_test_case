from dotenv import load_dotenv

import yaml
import csv

# my imports
from bot.errors import *
from bot.models import *

load_dotenv()


class Autobot:

    base_url = f"http://localhost:{os.getenv('DEFAULT_PORT', '8079')}/api/"

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
                logger.warning(f'<{param}>is not found, defaulting to {value}')
            else:
                defaults[key] = param

        # load csv file with companies data
        with open('links.csv', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)

        self.links = [i[0] for i in data]

        # init users
        logger.info(f'Using settings\n{defaults}')
        self.users = UserList(links=self.links, settings=defaults)

    def run(self):

        self.users.generate_posts()
        self.users.like_posts()


if __name__ == '__main__':
    bot = Autobot()
    bot.run()
