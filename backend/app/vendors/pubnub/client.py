import os
import uuid

from environs import Env
from pubnub.models.consumer.v3.channel import Channel
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

env = Env()
env.read_env(override=True)


class PubNubClient:
    def __init__(self):
        pn_config = PNConfiguration()
        pn_config.subscribe_key = env.str("PUBNUB_SUBSCRIBE_KEY")
        pn_config.publish_key = env.str("PUBNUB_PUBLISH_KEY")
        pn_config.secret_key = env.str("PUBNUB_SECRET_KEY")
        pn_config.user_id = "main-backend"
        pn_config.enable_subscribe = True
        pn_config.connect_timeout = 10
        pn_config.non_subscribe_request_timeout = 30
        self.pubnub = PubNub(pn_config)
        self.token_ttl = env.int("PUBNUB_TOKEN_TTL")

    def grant_channel_access(self, channel_name: str, user_uuid):
        envelope = self.pubnub.grant_token(channels=[
            Channel.id(channel_name).read().write()
        ]).authorized_uuid(user_uuid).ttl(ttl=self.token_ttl).sync()
        return envelope.result.token

    @staticmethod
    def generate_chanel_name(sensor_id: str):
        return f'sensor_{sensor_id}_{str(uuid.uuid4())}'


CLIENT = PubNubClient()
