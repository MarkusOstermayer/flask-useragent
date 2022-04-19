import re
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


class UserAgentEndpointException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UserAgentEndpoints:
    def __init__(self, user_agent: Optional[str], func: Callable) -> None:
        if user_agent == "*" or user_agent is None:
            self.user_agent_function_map: Dict[str, Callable] = {}
            self.fallback = func
        else:
            self.user_agent_function_map: Dict[str, Callable] = {
                user_agent: func
            }
            self.fallback: Callable = None

    def add_user_agent_endpoint(self, user_agent: str, func: Callable) -> None:
        # if no useragent is specified, we'll use the function as fallback
        if user_agent is None:
            self.add_fallback(func)
            return

        if user_agent in self.user_agent_function_map:
            error_msg = \
                f"{user_agent} is already used as useragent for this endpoint"

            raise UserAgentEndpointException(error_msg)

        self.user_agent_function_map[user_agent] = func

    def add_fallback(self, func) -> None:
        self.fallback = func

    def get_fallback(self) -> Optional[Callable]:
        return self.fallback

    def get_function(self, user_agent: str) -> Optional[Callable]:
        # if the useragent is None, return the fallback
        if user_agent is None:
            return self.get_fallback()

        # find exact matches
        for exact_user_agent in self.user_agent_function_map:
            if exact_user_agent == user_agent:
                return self.user_agent_function_map[exact_user_agent]

        # find with regex
        for user_agent_re in self.user_agent_function_map:
            if re.match(user_agent_re, user_agent):
                return self.user_agent_function_map[user_agent_re]

        # If a fallback exists, return it
        if self.fallback:
            return self.fallback

        return None


class EndpointContainer:
    def __init__(self):
        self.rules: Dict[str, [UserAgentEndpoints]] = {}

    def add_function(self, rule: str, user_agent: str, func: Callable):

        re_rule = rule_to_regex(rule)

        if re_rule in self.rules:
            self.rules[re_rule].add_user_agent_endpoint(user_agent, func)
        else:
            self.rules[re_rule] = UserAgentEndpoints(user_agent, func)

    def add_fallback(self, rule: str, func: Callable):

        re_rule = rule_to_regex(rule)

        if re_rule in self.rules:
            self.rules[re_rule].add_fallback(func)
        else:
            self.rules[re_rule] = UserAgentEndpoints(None, func)

    def get_function(self, rule: str, user_agent: str) -> Optional[Callable]:
        # search for rules that satisfy the regex
        for re_rule in self.rules:
            if re.fullmatch(re_rule, rule):
                return self.rules[re_rule].get_function(user_agent)

        return None

    def get_fallback(self, rule: str) -> Optional[Callable]:
        return self.get_function(rule, None)


def get_substitution(rule: str, position: Tuple[int, int]) -> str:
    variable_substitution = rule[position[0] + 1: position[1] + 1]

    # per default the type is string
    var_type = "string"
    if ":" in variable_substitution:
        var_type = variable_substitution.split(":")[0]

    if var_type == "string":
        return "([a-zA-Z0-9]+)"
    if var_type == "int":
        return "([0-9]+)"
    if var_type == "float":
        return "([0-9]+.[0-9]+)"
    if var_type == "path":
        return "([a-zA-Z0-9/]+)"
    if var_type == "uuid":
        return "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"


def rule_to_regex(rule: str) -> str:

    variable_positions: List[Tuple] = []
    i = 0
    variable_start = None

    for i, char in enumerate(rule):
        # try to find the start of the variable
        if char == "<":
            variable_start = i
        elif char == ">":
            variable_positions.append((variable_start, i))

    if len(variable_positions) < 1:
        return rule

    new_str: str = ""
    for i, variable_position in enumerate(variable_positions):
        if i == 0:
            new_str += rule[:variable_position[0]]
            new_str += get_substitution(rule, variable_position)
        else:
            new_str += rule[
                variable_positions[i-1][1] + 1: variable_position[0]
            ]
            new_str += get_substitution(rule, variable_position)

    new_str += rule[variable_positions[-1][1] + 1:]

    return new_str
