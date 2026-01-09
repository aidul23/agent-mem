# auth_and_profile.py

from dataclasses import dataclass


@dataclass
class UserProfile:
    user_id: str
    allow_memory: bool


# In real GPT-Lab system, load from DB; here, use a dict.
USER_DB: dict[str, UserProfile] = {}


def get_or_create_user(user_id: str) -> UserProfile:
    if user_id not in USER_DB:
        USER_DB[user_id] = UserProfile(user_id=user_id, allow_memory=False)
    return USER_DB[user_id]


def set_user_consent(user_id: str, allow: bool):
    profile = get_or_create_user(user_id)
    profile.allow_memory = allow

