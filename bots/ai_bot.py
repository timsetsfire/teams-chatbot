# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount
from botbuilder.schema import InputHints
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import ChannelAccount, CardAction, ActionTypes, SuggestedActions

from requests_futures.sessions import FuturesSession
import pandas as pd
import os
import logging 
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
                format="{} - %(levelname)s - %(asctime)s - %(message)s".format("debug-loggers"),
        )


import datetime
import sys
import json
import requests
import pandas as pd 
 
API_URL = ''
API_KEY = ''
DATAROBOT_KEY = ''
DEPLOYMENT_ID = ''

def make_datarobot_deployment_predictions(data, deployment_id):
    headers = {
        'Content-Type': 'text/plain; charset=UTF-8',
        'Authorization': 'Bearer {}'.format(API_KEY),
        'DataRobot-Key': DATAROBOT_KEY,
    }
 
    url = API_URL.format(deployment_id=deployment_id)
    params = {}
    predictions_response = requests.post(
        url,
        data=data.to_csv(index = False),
        headers=headers,
    )
    return predictions_response.json()

def ai_query(prompt):
    df = pd.DataFrame(dict(promptText = [prompt]))
    response = make_datarobot_deployment_predictions(df, DEPLOYMENT_ID)
    return response


class AIBot(ActivityHandler):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel("DEBUG")
        super().__init__()


    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!  Ask me any questions about DataRobot and I will do my best to answer them, as well as provide some relevant resources.")

    async def on_message_activity(self, turn_context: TurnContext):
        MessageFactory.text("Give me one moment while i look up that detail")
        text = turn_context.activity.text.strip()
        try:
            response = ai_query(text)
            reply_text = response["data"][0]["prediction"]

            ## add some references 
            references = [ response["data"][0]["extraModelOutput"][f"CITATION_SOURCE_{i}"] for i in range(3)]
            references = "\n".join( references) 
            response = reply_text + "\n\nHere are some references\n\n" + references
        except Exception as e:
            self.logger.error("="*20)
            self.logger.error(e)
            self.logger.error("="*20)
            response = "I'm sorry Dave, I'm afraid I can't do that."
        reply = MessageFactory.text(response)
        # reply.suggested_actions = SuggestedActions(
        #     actions=[
        #         CardAction(
        #             title=":thumbs_up:",
        #             type=ActionTypes.im_back,
        #             value="Good",
        #             image="https://via.placeholder.com/20/00FF00?text=G",
        #             image_alt_text="G",
        #         ),
        #         CardAction(
        #             title=":thumbs_down:",
        #             type=ActionTypes.im_back,
        #             value="Bad",
        #             image="https://via.placeholder.com/20/FF0000?text=B",
        #             image_alt_text="B",
        #         )
        #     ]
        # )
        
        return await turn_context.send_activity(reply)
        
        # prompt_message = MessageFactory.text(response, response, InputHints.expecting_input)
        # return await turn_context.prompt(
        #     ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        # )

