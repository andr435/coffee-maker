import os
import random
import logging

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
import ask_sdk_dynamodb
from ask_sdk_model.dialog import (ElicitSlotDirective, DelegateDirective)
from ask_sdk_model import (Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model.ui import SimpleCard

import config

dbTable = os.environ["skill_persistence_table"]
skillId = os.environ["skill_id"]
skillName = config.config['skill_name']

sb = StandardSkillBuilder(table_name=dbTable, auto_create_table=False, partition_keygen=ask_sdk_dynamodb.partition_keygen.user_id_partition_keygen)

###########################
# Launcher Request
###########################


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    attr = handler_input.attributes_manager.persistent_attributes
    session_attr = []
    session_attr['state'] = 'launch'
    session_attr['prev_state'] = ''

    if not attr:
        speech_text = f"""
            Welcome to {skillName}, 
            a skill that will help you to get a cup of coffee. 
            First I need to know your name and name of your coffee maker.
            Please tell me, what is your name?
            """
        reprompt = 'Please tell me, what is your name?'
    else:
        speech_text = f"{attr['user']}, good to hear from you again. What kind of coffee would like to drink?"
        reprompt = 'What coffee do you want?'

    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


