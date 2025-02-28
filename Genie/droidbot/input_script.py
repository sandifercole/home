# DroidBotScript
# This file contains the definition of DroidBotScript
# DroidBotScript is a domain-specific language, which defines how DroidBot interacts with target app
import logging
import re
from typing import Optional, Dict, Any

from droidbot.device_state import DeviceState
from .input_event import InputEvent, KEY_TouchEvent, KEY_LongTouchEvent
from .utils import safe_re_match

VIEW_ID = '<view_id>'
STATE_ID = '<state_id>'
OPERATION_ID = '<operation_id>'
DEFAULT_ID = 'default'
INTEGER_VAL = 0
BOOL_VAL = True
REGEX_VAL = r'<regex>'
EVENT_POLICY_VAL = '<event_policy>'
EVENT_TYPE_VAL = '<event_type>'
IDENTIFIER_RE = re.compile(r'^[^\d\W]\w*\Z', re.UNICODE)

MULTIPLE_SCRIPT = "multiple_script"  # ljx add new field to support multiple scripts
MultipleScript_VAL = "1"
ViewSelector_VAL = 'ViewSelector'
StateSelector_VAL = 'StateSelector'
DroidBotOperation_VAL = 'DroidBotOperation'
ScriptEvent_VAL = 'ScriptEvent'


class DroidBotScript(object):
    """
    DroidBotScript is a DSL for customizing input for certain states
    """
    script_grammar = {
        'views': {
            VIEW_ID: ViewSelector_VAL
        },
        'states': {
            STATE_ID: StateSelector_VAL
        },
        'operations': {
            OPERATION_ID: DroidBotOperation_VAL
        },
        'multiple': {
            MULTIPLE_SCRIPT: [MultipleScript_VAL]
        },
        'main': {
            STATE_ID: [OPERATION_ID]
        }
    }

    def __init__(self, script_dict: Dict[str, Any]):
        self.tag = self.__class__.__name__
        self.logger = logging.getLogger(self.tag)
        self.script_dict = script_dict

        #  add a flag to record the last state selector
        self.last_state_selector_index = 0

        #
        self.script_sequential_exec_mode = False

        self.script_num = -1  # ljx clarify how many scripts to process
        self.switch = False  # ljx whether a script is finished
        # End

        self.views = {}
        self.states: Dict[StateSelector, Any] = {}
        self.operations = {}
        self.main = {}
        # ljx add new key-value "multiple"
        self.multiple = []
        self.parse()
        #  debug
        print("at the end of script parsing")

    def parse(self):
        self.check_grammar_type(self.script_dict, self.script_grammar, self.tag)
        self.parse_views()
        self.parse_states()
        self.parse_operations()
        # self.parse_multiple()
        self.parse_main()
        self.check_duplicated_ids()
        # self.check_id_not_defined()

    def parse_views(self):
        script_key = 'views'
        script_value = self.check_and_get_script_value(script_key)
        for view_id in script_value:
            self.check_grammar_identifier_is_valid(view_id)
            view_selector_dict = script_value[view_id]
            view_selector = ViewSelector(view_id, view_selector_dict, self)
            self.views[view_id] = view_selector

    def parse_states(self):
        script_key = 'states'
        script_value = self.check_and_get_script_value(script_key)
        for state_id in script_value:
            self.check_grammar_identifier_is_valid(state_id)
            state_selector_dict = script_value[state_id]
            state_selector = StateSelector(state_id, state_selector_dict, self)
            self.states[state_id] = state_selector

    def parse_operations(self):
        script_key = 'operations'
        script_value = self.check_and_get_script_value(script_key)
        for operation_id in script_value:
            self.check_grammar_identifier_is_valid(operation_id)
            event_list = script_value[operation_id]
            operation = DroidBotOperation(operation_id, event_list, self)
            self.operations[operation_id] = operation

    def parse_multiple(self):
        script_key = 'multiple'
        script_value = self.check_and_get_script_value(script_key)
        for each in script_value:
            self.multiple = script_value[
                each]  # get the value, each value shows the number of operations of the corresponding script
            self.script_num = len(self.multiple)

    def parse_main(self):
        script_key = 'main'
        key_tag = "%s.%s" % (self.tag, script_key)
        script_value = self.check_and_get_script_value(script_key)
        for state_id in script_value:
            self.check_grammar_identifier_is_valid(state_id)
            self.check_grammar_key_is_valid(state_id, self.states, key_tag)
            state_selector = self.states[state_id]
            self.main[state_selector] = []
            operation_ids = script_value[state_id]
            for operation_id in operation_ids:
                self.check_grammar_identifier_is_valid(operation_id)
                self.check_grammar_key_is_valid(operation_id, self.operations, key_tag)
                operation = self.operations[operation_id]
                self.main[state_selector].append(operation)

    def get_switch(self):
        return self.switch

    def set_switch(self, flag):
        self.switch = flag

    def get_operation_based_on_state(self, state) -> Optional['ScriptEvent']:
        """
        get ScriptEvents based on the DeviceState given, according to the script definition
        @param state: DeviceState
        @return:
        """
        if not state:
            return None

        operation = None
        matched_state_selector = None

        # find the state that matches current DeviceState
        for state_selector in self.main:
            if self.script_sequential_exec_mode:
                #  sequential execution strategy for script (for whole test suite execution)
                if state_selector.match_seq_id(self.last_state_selector_index + 1) and state_selector.match(state):
                    matched_state_selector = state_selector
                    self.last_state_selector_index += 1
                    if self.last_state_selector_index == self.multiple[len(self.multiple) - self.script_num]:
                        self.script_num -= 1
                        if self.script_num > 0:  # if it reaches the last script, there is no need to restart the app
                            self.switch = True
                    break
            else:
                #  state matching execution strategy (Droidbot's original algorithm)
                if state_selector.match(state):
                    matched_state_selector = state_selector

                    # annotate this state has been matched one time
                    state_selector.matched_once = True

                    break
        if not matched_state_selector:
            return None

        # get the operation corresponding to the matched state
        operations = self.main[matched_state_selector]
        if len(operations) > 0:
            operation = operations[0]

        # rotate operations
        operations = operations[1:] + operations[:1]
        self.main[matched_state_selector] = operations

        if operation:
            msg = "matched state: %s, taking operation: %s" % (matched_state_selector.id, operation.id)
            self.logger.info(msg)

        return operation

    @staticmethod
    def check_grammar_type(value, grammar, tag):
        if (isinstance(value, str) or value is None) and isinstance(grammar, str):
            return
        if not isinstance(value, type(grammar)):
            msg = '%s: type should be %s, %s given' % (tag, type(grammar), type(value))
            raise ScriptSyntaxError(msg)

    @staticmethod
    def check_grammar_key_is_valid(value, valid_keys, tag):
        if value not in valid_keys:
            msg = '%s: key should be %s, %s given' % (tag, list(valid_keys), value)
            raise ScriptSyntaxError(msg)

    @staticmethod
    def check_grammar_has_key(dict_keys, required_key, tag):
        if required_key not in dict_keys:
            msg = '%s: key required: %s' % (tag, required_key)
            raise ScriptSyntaxError(msg)

    @staticmethod
    def check_grammar_identifier_is_valid(value):
        m = safe_re_match(IDENTIFIER_RE, value)
        if not m:
            msg = "invalid identifier: %s" % value
            raise ScriptSyntaxError(msg)

    @staticmethod
    def check_grammar_is_coordinate(value):
        if not isinstance(value, tuple) or len(value) != 2:
            msg = "illegal coordinate format: %s, should be 2-tuple" % value
            raise ScriptSyntaxError(msg)
        if not isinstance(value[0], int) or not isinstance(value[1], int):
            msg = "illegal coordinate value: %s, should be integer" % value
            raise ScriptSyntaxError(msg)

    @staticmethod
    def check_grammar_is_list(value):
        if not isinstance(value, list):
            msg = "illegal list: %s" % value
            raise ScriptSyntaxError(msg)

    def check_and_get_script_value(self, script_key):
        self.check_grammar_has_key(self.script_dict, script_key, self.tag)
        key_tag = "%s.%s" % (self.tag, script_key)
        script_value = self.script_dict[script_key]
        grammar_value = self.script_grammar[script_key]
        self.check_grammar_type(script_value, grammar_value, key_tag)
        return script_value

    def check_duplicated_ids(self):
        all_ids = []
        all_ids.extend(self.views)
        all_ids.extend(self.states)
        all_ids.extend(self.operations)
        all_ids_set = set(all_ids)
        if len(all_ids) > len(all_ids_set):
            msg = "duplicated identifier definition"
            raise ScriptSyntaxError(msg)
        if DEFAULT_ID in all_ids_set:
            msg = "defining reserved identifier: %s" % DEFAULT_ID
            raise ScriptSyntaxError(msg)

    def check_id_not_defined(self):
        defined_view_ids = set()
        defined_view_ids.update(self.views)
        used_view_ids = set()
        for state_id in self.states:
            state_selector = self.states[state_id]
            used_view_ids.update(state_selector.get_used_views())
        for operation_id in self.operations:
            operation = self.operations[operation_id]
            used_view_ids.update(operation.get_used_views())
        if not defined_view_ids.issuperset(used_view_ids):
            undefined_view_ids = used_view_ids - defined_view_ids
            msg = "using undefined views: %s" % list(undefined_view_ids)
            raise ScriptSyntaxError(msg)

        defined_state_ids = set()
        defined_state_ids.update(self.states)
        used_state_ids = set()
        used_state_ids.update(self.main)
        if not defined_state_ids.issuperset(used_state_ids):
            undefined_state_ids = used_state_ids - defined_state_ids
            msg = "using undefined states: %s" % list(undefined_state_ids)
            raise ScriptSyntaxError(msg)

        defined_operation_ids = set()
        defined_operation_ids.update(self.operations)
        used_operation_ids = set()
        for state_id in self.main:
            used_operation_ids.update(self.main[state_id])
        for operation_id in self.operations:
            operation = self.operations[operation_id]
            used_operation_ids.update(operation.get_used_operations())
        if not defined_operation_ids.issuperset(used_operation_ids):
            undefined_operation_ids = used_operation_ids - defined_operation_ids
            msg = "using undefined operations: %s" % list(undefined_operation_ids)
            raise ScriptSyntaxError(msg)


class ViewSelector(object):
    """
    selector used to select a view
    """
    selector_grammar = {
        'text': REGEX_VAL,
        'resource_id': REGEX_VAL,
        'class': REGEX_VAL,
        'index': INTEGER_VAL,
        'child_text': REGEX_VAL,  # the text of child or grandchild
        'actionable_view': BOOL_VAL,
        'content_description': REGEX_VAL,  # ljx add field "content_description" to match a view
        'out_coordinates': [(INTEGER_VAL, INTEGER_VAL)],
        'in_coordinates': [(INTEGER_VAL, INTEGER_VAL)]
    }

    def __init__(self, view_selector_id, selector_dict, script):
        self.tag = self.__class__.__name__
        self.id = view_selector_id
        self.selector_dict = selector_dict
        self.text_re = None
        self.resource_id_re = None
        self.class_re = None
        self.index = None
        self.child_text_re = None
        # The flag that indicates whether the view itself is actionable or not.
        #   By default, the view is actionable (i.e. True). Otherwise, we will locate its actionable parent view to
        #   execute this event.
        self.actionable_view = True
        self.content_description_re = None
        self.script = script
        self.out_coordinates = []
        self.in_coordinates = []
        self.parse()

    def parse(self):
        DroidBotScript.check_grammar_type(self.selector_dict, self.selector_grammar, self.tag)
        for selector_key in self.selector_dict:
            DroidBotScript.check_grammar_key_is_valid(selector_key, self.selector_grammar, self.tag)
            selector_value = self.selector_dict[selector_key]
            grammar_value = self.selector_grammar[selector_key]
            key_tag = "%s.%s" % (self.tag, selector_key)
            DroidBotScript.check_grammar_type(selector_value, grammar_value, key_tag)
            if selector_key == 'text':
                self.text_re = re.compile(selector_value)
            elif selector_key == 'resource_id':
                if selector_value is not None:
                    self.resource_id_re = re.compile(selector_value)
                else:
                    self.resource_id_re = None
            elif selector_key == 'class':
                self.class_re = re.compile(selector_value)
            elif selector_key == 'index':
                self.index = int(selector_value)
            elif selector_key == 'child_text':
                self.child_text_re = re.compile(selector_value)
            elif selector_key == 'actionable_view':
                self.actionable_view = selector_value
            elif selector_key == 'content_description':
                self.content_description_re = re.compile(selector_value)
            elif selector_key == 'out_coordinates':
                for out_coordinate in grammar_value:
                    DroidBotScript.check_grammar_is_coordinate(out_coordinate)
                    self.out_coordinates.append(out_coordinate)
            elif selector_key == 'in_coordinates':
                for in_coordinate in grammar_value:
                    DroidBotScript.check_grammar_is_coordinate(in_coordinate)
                    self.in_coordinates.append(in_coordinate)

    def match(self, view_dict, state_of_view_dict: DeviceState) -> bool:
        """
        return True if this view_selector matches a view_dict
        @param view_dict: a view in dict, element of DeviceState.views
        @param state_of_view_dict: the state of this view dict
        @return:
        """
        if 'text' in view_dict and 'resource_id' in view_dict \
                and 'class' in view_dict and 'bounds' in view_dict and 'content_description' in view_dict:
            pass
        else:
            return False
        if self.text_re and not safe_re_match(self.text_re, view_dict['text']):
            return False
        if self.resource_id_re and not safe_re_match(self.resource_id_re, view_dict['resource_id']):
            return False
        if self.resource_id_re is None and view_dict['resource_id'] is not None:
            # handle the case: resource_id is None in the script
            return False
        if self.class_re and not safe_re_match(self.class_re, view_dict['class']):
            return False
        if self.index and not (self.index == view_dict['sibling_id']):
            return False
        if self.content_description_re and not safe_re_match(self.content_description_re,
                                                             view_dict['content_description']):
            return False

        if self.child_text_re and not state_of_view_dict.contain_child_with_text(view_dict, self.child_text_re):
            return False

        # ljx when we use a coordinate to operate as we have implemented,
        # this part could be helpless

        # bounds = view_dict['bounds']
        # bound_x_min = bounds[0][0]
        # bound_x_max = bounds[1][0]
        # bound_y_min = bounds[0][1]
        # bound_y_max = bounds[1][1]
        # for (x, y) in self.in_coordinates:
        #     if x < bound_x_min or x > bound_x_max or y < bound_y_min or y > bound_y_max:
        #         return False
        # for (x, y) in self.out_coordinates:
        #     if bound_x_min < x < bound_x_max and bound_y_min < y < bound_y_max:
        #         return False
        return True


class StateSelector(object):
    """
    selector used to select a UI state
    """
    selector_grammar = {
        'activity': REGEX_VAL,
        'services': [REGEX_VAL],
        'views': [ViewSelector_VAL],
        'always_match': BOOL_VAL,
        #  add 'seq_id' to denote its execution order
        # must start from ONE
        'seq_id': REGEX_VAL
    }

    def __init__(self, state_selector_id, selector_dict, script):
        self.tag = self.__class__.__name__
        self.id = state_selector_id
        #  add a flag to record test seq. id
        self.seq_id = None
        self.matched_once = False
        # the flag that indicates whether the state is always matched
        # by default, if the state is matched, the corresponding script will always be executed
        self.always_match = True
        # End
        self.script = script
        self.selector_dict = selector_dict
        self.activity_re = None
        self.service_re_set = set()
        self.views = set()
        self.parse()

    #  match the target seq id
    def match_seq_id(self, target_seq_id):
        if int(self.seq_id) == target_seq_id:
            return True
        else:
            return False

    def parse(self):
        DroidBotScript.check_grammar_type(self.selector_dict, self.selector_grammar, self.tag)
        for selector_key in self.selector_dict:
            DroidBotScript.check_grammar_key_is_valid(selector_key, self.selector_grammar, self.tag)
            selector_value = self.selector_dict[selector_key]
            grammar_value = self.selector_grammar[selector_key]
            key_tag = "%s.%s" % (self.tag, selector_key)
            DroidBotScript.check_grammar_type(selector_value, grammar_value, key_tag)
            if selector_key == 'activity':
                self.activity_re = re.compile(selector_value)
            elif selector_key == 'services':
                for service_re_str in selector_value:
                    service_re = re.compile(service_re_str)
                    self.service_re_set.add(service_re)
            #  handle "seq_id"
            elif selector_key == 'seq_id':
                self.seq_id = selector_value
            elif selector_key == 'always_match':
                self.always_match = selector_value
            # End
            elif selector_key == 'views':
                for view_id in selector_value:
                    DroidBotScript.check_grammar_key_is_valid(view_id, self.script.views, key_tag)
                    self.views.add(self.script.views[view_id])

    def match(self, device_state):
        """
        check if the selector matches the DeviceState
        @param device_state: DeviceState
        @return:
        """
        #  only match this state one time
        if self.matched_once and (not self.always_match):
            return False

        if self.activity_re and not safe_re_match(self.activity_re, device_state.foreground_activity):
            return False
        for service_re in self.service_re_set:
            service_re_matched = False
            if device_state.background_services is None:
                return False
            if not isinstance(device_state.background_services, list):
                return False
            for background_service in device_state.background_services:
                if safe_re_match(service_re, background_service):
                    service_re_matched = True
                    break
            if not service_re_matched:
                return False
        for view_selector in self.views:
            view_selector_matched = False
            view_dicts = device_state.views
            if view_dicts is None:
                return False
            if not isinstance(view_dicts, list):
                return False
            for view_dict in view_dicts:
                if view_selector.match(view_dict, device_state):
                    view_selector_matched = True
                    break
            if not view_selector_matched:
                return False
        return True


class DroidBotOperation(object):
    """
    an operation is what DroidBot do to target device
    It might be a set of events, or an event policy
    """
    custom_operation_grammar = [ScriptEvent_VAL]

    def __init__(self, operation_id, event_list, script):
        self.tag = self.__class__.__name__
        self.id = operation_id
        self.script = script
        self.event_list = event_list
        self.events = []
        self.parse()

    def parse(self):
        DroidBotScript.check_grammar_is_list(self.event_list)
        for event_dict in self.event_list:
            if 'target_view' in event_dict:
                target_view_id = event_dict['target_view']
                DroidBotScript.check_grammar_key_is_valid(target_view_id, self.script.views, self.tag)
                target_view_selector = self.script.views[target_view_id]
                event_dict['target_view_selector'] = target_view_selector
            script_event = ScriptEvent(event_dict)
            self.events.append(script_event)


class ScriptEvent(object):
    """
    an event defined in DroidBotScript
    the grammar of ScriptEvent is similar with the InputEvent in dict format
    but must be transformed before being used
    """

    def __init__(self, event_dict):
        self.event_dict = event_dict
        print(self.event_dict)

    def get_transformed_event(self, input_policy) -> Optional[InputEvent]:
        device = input_policy.device
        event_dict = self.event_dict.copy()
        if 'target_view' in event_dict:
            target_view = event_dict.pop('target_view')
            target_view_selector = event_dict.pop('target_view_selector')

            state = device.get_last_known_state()
            if not state:
                state = device.get_current_state(device.output_dir)
            if state:
                matched_view = None
                for view_dict in state.views:
                    if target_view_selector.match(view_dict, state):

                        # TODO now we only handle these two event types, i.e., touch and long-touch
                        #   Please add the other events if needed.
                        if event_dict['event_type'] == KEY_TouchEvent and view_dict['clickable'] is False:
                            matched_view = ScriptEvent.locate_executable_parent_view(view_dict, 'clickable', state)
                        elif event_dict['event_type'] == KEY_LongTouchEvent and view_dict['long_clickable'] is False:
                            matched_view = ScriptEvent.locate_executable_parent_view(view_dict, 'long_clickable', state)
                        else:
                            matched_view = view_dict
                        break
                if matched_view is None:
                    device.logger.warning("target_view no match: %s" % target_view)
                    return None
                else:
                    event_dict['view'] = matched_view
        if event_dict['event_type'] == 'spawn':
            event_dict['master'] = input_policy.master
        return InputEvent.from_dict(event_dict)

    def to_dict(self):
        event_dict = self.event_dict.copy()
        if 'target_view_selector' in event_dict:
            event_dict.pop('target_view_selector')
        return event_dict

    @staticmethod
    def locate_executable_parent_view(view_dict, view_property_name, current_state: DeviceState):
        """
        find the view that is actionable for the property of the given view
        :param view_dict: the given view dict
        :param view_property_name: the given property name
        :param current_state: the current state
        :return:
        """

        parent_ids = current_state.get_all_ancestors(view_dict)
        for parent_id in parent_ids:
            parent_view = current_state.views[parent_id]
            if parent_view[view_property_name]:
                return parent_view


class ScriptSyntaxError(RuntimeError):
    """
    syntax error of DroidBotScript
    """
    pass
