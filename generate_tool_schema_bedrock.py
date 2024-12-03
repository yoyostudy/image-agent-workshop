# Notice: Code adopted with edition from 
# https://github.com/yefan/image-agent-workshop/blob/main/details/generate_tools_schema.py

import inspect
from typing import Dict, Any, Callable

Struct = Dict[str, Dict]

def generate_json_schema(
    func: Callable, 
) -> Struct:
    """
    Generate Bedrock tool JSON Schema for a callable object.

    The `func` function needs to follow specific rules.
    All parameters must be names explicitly (`*args` and `**kwargs` are not supported).

    :param func: Function for which to generate schema
    :return: The JSON Schema for the tool as a dict.
    """

    from pydantic import v1 as pydantic
    from pydantic.v1 import fields as pydantic_fields
    import docstring_parser

    function_description = func.__doc__
    #print(function_description)

    # Parsed parameter descriptions from the docstring
    # Also parse the function description in a better way
    parameter_description = {}
    parsed_docstring = docstring_parser.parse(func.__doc__)
    #print(dir(parsed_docstring))
    function_description = parsed_docstring.long_description or parsed_docstring.short_description
    #print(function_description)
    for meta in parsed_docstring.meta:
        if isinstance(meta, docstring_parser.DocstringParam):
            parameter_description[meta.arg_name] = meta.description
    #print(parameter_description)

    defaults = dict(inspect.signature(func).parameters)
    #print(defaults)
    fields_dict = {
        name: (
            # 1. We infer the argument type here: use Any rather than None so
            # it will not try to auto-infer the type based on the default value.
            (param.annotation if param.annotation != inspect.Parameter.empty else Any),
            pydantic.Field(
                # 2. We do not support default values for now.
                default=(
                    param.default
                    if param.default != inspect.Parameter.empty
                    # ! Need to use Undefined instead of None
                    else pydantic_fields.Undefined
                ),
                # 3. We support user-provided descriptions.
                description=parameter_description.get(name, None),
            ),
        )
        for name, param in defaults.items()
        # We do not support *args or **kwargs
        if param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
            inspect.Parameter.POSITIONAL_ONLY,
        )
    }
    fields_schema = pydantic.create_model(func.__name__, **fields_dict).schema()

    input_schema = {}
    input_schema["json"] = fields_schema

    tool_spec_schema = {}
    tool_spec_schema["name"] = func.__name__
    tool_spec_schema["description"] = function_description if function_description else "" 
    tool_spec_schema["inputSchema"] = input_schema

    tool_schema = {}
    tool_schema["toolSpec"] = tool_spec_schema
    return tool_schema