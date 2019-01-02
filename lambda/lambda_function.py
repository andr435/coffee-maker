import os
import random

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
import ask_sdk_dynamodb
from ask_sdk_model.dialog import (ElicitSlotDirective, DelegateDirective)
from ask_sdk_model import (Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
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
    session_attr = {
        'state': 'launch',
        'prev_state': '',
    }

    if not attr:
        session_attr['state'] = 'user_name'
        speech_text = f"""
            Welcome to {skillName}, 
            a skill that will help you to get a cup of coffee. 
            First I need to know your name and name of your coffee maker.
            Please tell me, what is your name?
            """
        reprompt = 'Please tell me, what is your name?'
        card_text = f"Welcome to {skillName}, what is your name?"
    else:
        speech_text = f"{attr['user']}, good to hear from you again. What kind of coffee would you like?"
        reprompt = 'What coffee do you want?'
        card_text = reprompt

        required = ('user', 'maker')
        if all(k in attr for k in required):
            session_attr['user'] = attr['user']
            session_attr['maker'] = attr['maker']

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("SetupIntent"))
def setup_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'setup')

    if handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED:
        return handler_input.response_builder.add_directive(DelegateDirective()).response

    filled_slots = handler_input.request_envelope.request.intent.slots
    slots = get_slot_values(filled_slots)

    settings = {
        'user': slots['user_name'],
        'maker': slots['maker_name']
    }

    handler_input.attributes_manager.persistent_attributes = settings
    handler_input.attributes_manager.save_persistent_attributes()
    speech_text = "What kind of coffee would you like?"
    reprompt = 'What coffee do you want?'
    card_text = speech_text

    session_attr['user'] = slots['user_name']
    session_attr['maker'] = slots['maker_name']
    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input: is_intent_name("MakeCoffeeIntent")(input) or is_intent_name("AMAZON.NavigateHomeIntent")(input))
def make_coffee_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'make_coffee')

    required = ('user', 'maker')
    if all(k in session_attr for k in required):
        user = session_attr['user']
        maker = session_attr['maker']
    else:
        attr = handler_input.attributes_manager.persistent_attributes
        if not attr:
            session_attr['state'] = 'user_name'
            speech_text = f"""
                        Welcome to {skillName}, 
                        a skill that will help you to get a cup of coffee. 
                        First I need to know your name and name of your coffee maker.
                        Please tell me, what is your name?
                        """
            reprompt = 'Please tell me, what is your name?'
            card_text = f"Welcome to {skillName}, what is your name?"

            save_last_response(session_attr, speech_text, reprompt, card_text)
            handler_input.attributes_manager.session_attributes = session_attr
            handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
            return handler_input.response_builder.response

        maker = attr['maker']
        user = attr['user']
        session_attr['user'] = user
        session_attr['maker'] = maker

    filled_slots = handler_input.request_envelope.request.intent.slots
    slots = get_slot_values(filled_slots, True)
    coffee = slots['coffee']

    text_a = random.choice(config.replay)
    text_b = random.choice(config.replay)
    speech_text = text_a['text'].format(user=user, maker=maker, coffee=coffee)
    reprompt = text_b['text'].format(user=user, maker=maker, coffee=coffee)
    card_text = text_a['card'].format(user=user, maker=maker, coffee=coffee)

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name('NameIntent'))
def name_intent_handler(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr.setdefault('state', '')

    filled_slots = handler_input.request_envelope.request.intent.slots
    slots = get_slot_values(filled_slots)

    if session_attr['state'] == 'user_name':
        session_attr['user'] = slots['name']
        if 'maker' not in session_attr:
            speech_text = "What a name of coffee maker?"
            reprompt = "Who will serve you a coffee?"
            card_text = speech_text
            session_attr['state'] = 'maker_name'
        else:
            speech_text = "What kind of coffee would you like?"
            reprompt = "What coffee do you want?"
            card_text = speech_text
            session_attr['state'] = 'make_coffee'

    elif session_attr['state'] == 'maker_name':
        session_attr['maker'] = slots['name']
        if 'user' not in session_attr:
            speech_text = "What is your name?"
            reprompt = "What is your first name?"
            card_text = speech_text
            session_attr['state'] = 'user_name'
        else:
            speech_text = "What kind of coffee would you like?"
            reprompt = "What coffee do you want?"
            card_text = speech_text
            session_attr['state'] = 'make_coffee'

    else:
        speech_text = "What kind of coffee would you like?"
        reprompt = "What coffee do you want?"
        card_text = speech_text
        session_attr['state'] = 'make_coffee'

    required = ('user', 'maker')
    if all(k in session_attr for k in required):
        settings = {
            'user': session_attr['user'],
            'maker': session_attr['maker']
        }

        handler_input.attributes_manager.persistent_attributes = settings
        handler_input.attributes_manager.save_persistent_attributes()

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'fallback')

    if 'user' in session_attr:
        speech_text = f"""
                    Sorry {session_attr['user']}, I can not help you with that, 
                    But what kind of coffee would you like?
                    """
        reprompt = 'What coffee do you want?'
        card_text = reprompt
    else:
        attr = handler_input.attributes_manager.persistent_attributes
        if not attr:
            session_attr['state'] = 'user_name'
            speech_text = f"""
                        Sorry, I can not help you with that.
                        I am the {skillName}, 
                        a skill that will help you to get a cup of coffee. 
                        First I need to know your name and name of your coffee maker.
                        Please tell me, what is your name?
                        """
            reprompt = 'Please tell me, what is your name?'
            card_text = f"I am the {skillName}, what is your name?"
        else:
            speech_text = f"""
                        Sorry {attr['user']}, I can not help you with that, 
                        But what kind of coffee would you like?
                        """
            reprompt = 'What coffee do you want?'
            card_text = reprompt

            session_attr['user'] = attr['user']
            session_attr['maker'] = attr['maker']

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.StopIntent")(input) or is_intent_name("AMAZON.CancelIntent")(input))
def stop_or_cancel_intent_handler(handler_input):
    handler_input.response_builder.set_should_end_session(True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'help')

    speech_text = """
        This is a funny skill that will help you to get a cup of coffee.
        If you want change your name or name of coffee maker say: go to settings or update.
        To get a fresh coffee say: I want coffee
    """
    reprompt = 'Try to say: I want coffee'
    card_text = reprompt

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.RepeatIntent"))
def repeat_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'repeat')
    handler_input.attributes_manager.session_attributes = session_attr
    handler_input.response_builder.speak(session_attr['speech']).ask(session_attr['reprompt']).set_card(SimpleCard(skillName, session_attr['card']))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("InfoIntent"))
def repeat_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'info')
    session_attr.setdefault('user', 'not set')
    session_attr.setdefault('maker', 'not set')
    speech_text = f"""
            Information that I know about you is: your name: {session_attr['user']},
            and a maker name is: {session_attr['maker']}
        """
    reprompt = 'Try to say: I want coffee'
    card_text = reprompt

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("DeleteInfoIntent"))
def repeat_intent_handler(handler_input):
    session_attr = get_session_attr(handler_input, 'delete_info')
    session_attr['user'] = ''
    session_attr['maker'] = ''
    session = {'user': session_attr['user'], 'maker' :  session_attr['user']}
    handler_input.attributes_manager.persistent_attributes = session
    handler_input.attributes_manager.save_persistent_attributes()

    speech_text = f"""
            Information about you was deleted
        """
    reprompt = 'Try to say: I want coffee'
    card_text = reprompt

    save_last_response(session_attr, speech_text, reprompt, card_text)
    handler_input.attributes_manager.session_attributes = session_attr

    handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(skillName, card_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    print(f"Reason for ending session: {handler_input.request_envelope.request.reason}")
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    print(f"Encountered following exception: {exception}")
    speech = "I don't understand that. Please say it again. "
    handler_input.response_builder.speak(speech).ask(speech).set_card(SimpleCard(skillName, speech))
    return handler_input.response_builder.response


def get_slot_values(filled_slots, resolution=False):
    slots = {}
    if resolution:
        for key, val in filled_slots.items():
            tmp = val.resolutions.to_dict()
            if tmp['resolutions_per_authority'][0]['status']['code'] != 'ER_SUCCESS_MATCH':
                slots[key] = val.value
            else:
                slots[key] = tmp['resolutions_per_authority'][0]['values'][0]['value']['name']
    else:
        slots = {}
        for key, val in filled_slots.items():
            slots[key] = val.value

    return slots


def get_session_attr(handler_input, state=''):
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr.setdefault('state', '')
    session_attr['prev_state'] = session_attr['state']
    session_attr['state'] = state
    return session_attr


def save_last_response(session_attr, speech='', reprompt='', card=''):
    session_attr['speech'] = speech
    session_attr['reprompt'] = reprompt
    session_attr['card'] = card


handler = sb.lambda_handler()