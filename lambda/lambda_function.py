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


def persist_user_attributes(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes

    handler_input.attributes_manager.persistent_attributes = session_attr
    handler_input.attributes_manager.save_persistent_attributes()


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    attr = handler_input.attributes_manager.persistent_attributes
    session_attr = {}
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
        card_text = f"Welcome to {skillName}, what is your name?"
    else:
        speech_text = f"{attr['user']}, good to hear from you again. What kind of coffee would like to drink?"
        reprompt = 'What coffee do you want?'

    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("SetupIntent"))
def launch_request_handler(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['prev_state'] = session_attr['state']
    session_attr['state'] = 'setup'
    handler_input.attributes_manager.session_attributes = session_attr

    if handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED:
        return handler_input.response_builder.add_directive(DelegateDirective()).response

    filled_slots = handler_input.request_envelope.request.intent.slots

    settings = {}
    settings['user'] = filled_slots.user_name.value
    settings['maker'] = filled_slots.maker_name.value

    handler_input.attributes_manager.persistent_attributes = settings
    handler_input.attributes_manager.save_persistent_attributes()
    speech_text = "What kind of coffee would like to drink?"
    reprompt = 'What coffee do you want?'
    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, speech_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("CoffeeIntent"))
def launch_request_handler(handler_input):
    attr = handler_input.attributes_manager.persistent_attributes
    speech_text = 'test'
    reprompt = 'test'
    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, speech_text))
    return handler_input.response_builder.response

handler = sb.lambda_handler()