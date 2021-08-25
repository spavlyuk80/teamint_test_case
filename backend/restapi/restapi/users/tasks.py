import clearbit
import os
import logging
import json
from celery import shared_task, group


logger = logging.getLogger(__name__)


@shared_task
def enrich_multiple():
    """
    periodic function that checks if user data has been enriched
    """

    # TODO: ignore staff users in general
    empty_data = Profile.objects.filter(enriched=False, user__is_superuser=False)

    run_group = group(enrich_user_data(i.user_id) for i in empty_data)
    run_group()


@shared_task
def enrich_user_data(user_id):
    from django.contrib.auth.models import User
    from users.models import Profile
    """
    Enrichment data is not needed upon signup,
    we use celery to get more info about user and
    we let clearbit block the response by using stream=True

    currently only populates First Name, Last Name, stores
    everything else as json string in Profile
    """
    api_key = os.getenv('CLEARBIT_API_KEY')

    if api_key is None:
        logger.error("Clearbit key is not found")

    profile = Profile.objects.get(user_id=user_id)
    user = User.objects.get(id=user_id)

    clearbit.key = api_key

    response = clearbit.Enrichment.find(
        email=user.email, stream=True
        )

    # only need personal data
    if 'person' in response:
        # try to get person's first name and last name
        # put everything reg person as a json string
        # into profile
        # keep on trying if no person data

        # TODO: review update policy

        personal_data = response.get('person',{}).get('name')
        if personal_data is None:
            return
        else:
            first_name = personal_data.get("givenName","")
            last_name = personal_data.get("familyName","")

            if len(first_name)>0:
                user.first_name = first_name
            if len(last_name)>0:
                user.last_name = last_name
            user.save()

            profile.extra_info = json.dumps(response['person'])
            profile.enriched = True
            profile.save()
