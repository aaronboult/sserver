"""Handles tag registration and lookup."""


import copy
from typing import Dict, List, Optional, Union
from sserver.templating import exception


# Inline and block tags
_inline_tag_map = {}
_block_tag_map = {}


TagMatch = Dict[str, Union[str, callable]]


def tag_is_inline(tag_name: str) -> bool:
    """Checks if a tag is an inline tag.

    Args:
        tag_name (`str`): The name of the tag.

    Returns:
        `bool`: True if the tag is an inline tag, False otherwise.
    """

    return tag_name in _inline_tag_map


def tag_is_block(tag_name: str) -> bool:
    """Checks if a tag is a block tag.

    Args:
        tag_name (`str`): The name of the tag.

    Returns:
        `bool`: True if the tag is a block tag, False otherwise.
    """

    return tag_name in _block_tag_map


def get_block_tag_match(tag_name: str) -> TagMatch:
    """Gets a matched block tag.

    Args:
        tag_name (`str`): The name of the tag.

    Returns:
        `TagMatch`: The data for the block tag.
    """

    if tag_name not in _block_tag_map:
        raise exception.UnknownTagException(
            f'Unknown block tag {tag_name}'
        )

    return copy.deepcopy(_block_tag_map[tag_name])


def get_tag_function(tag_name: str, is_block: bool = False,
                     sub_tag: Optional[str] = None) -> callable:
    """Gets the tag function for the given tag name.

    Args:
        tag_name (`str`): The name of the tag.
        is_block (`bool`): Whether the tag is a block tag.
        sub_tag (`str`, optional): The sub tag of the block tag.

    Returns:
        `Callable`: The tag function.

    Raises:
        `UnknownTagException`: If the tag is not recognized.
        `MissingTagFunctionException`: If the tag does not have a
            function.
    """

    tag_data = (
        _block_tag_map if is_block
        else _inline_tag_map
    )

    if tag_name not in tag_data:
        raise exception.UnknownTagException(f'Unknown tag {tag_name}')

    tag_function = tag_data[tag_name].get('tag_function')

    if sub_tag is not None:
        sub_tag_data = tag_data[tag_name].get('sub_tags', [])

        if sub_tag not in sub_tag_data:
            raise exception.UnknownTagException(
                f'Unknown sub tag {sub_tag} for tag {tag_name}'
            )

        if isinstance(sub_tag_data, dict):
            sub_tag_function = tag_data[tag_name]['sub_tags'][sub_tag].get(
                'tag_function'
            )

            if sub_tag_function is not None:
                tag_function = sub_tag_function

    if tag_function is None:
        raise exception.MissingTagFunctionException(
            f'Missing tag function for tag {tag_name}'
        )

    return tag_function


def _tag_already_registered(tag_name: str) -> bool:
    """Checks if a tag is already registered.

    Args:
        tag_name (`str`): The name of the tag.

    Returns:
        `bool`: True if the tag is already registered, False otherwise.
    """

    tag_registered = (
        tag_name in _inline_tag_map or
        tag_name in _block_tag_map
    )

    # If tag is not registered as a main tag, check all sub tags
    if not tag_registered:
        for block_tag_match in _block_tag_map.values():
            sub_tags = block_tag_match.get('sub_tags', [])

            if tag_name in sub_tags:
                tag_registered = True
                break

    return tag_registered


def _register_block_tag(tag_name: str, end_tag: str,
                        tag_function: callable,
                        sub_tag_list: Optional[List[
                            Union[str, TagMatch]
                        ]] = None):
    """Registers a block tag.

    Args:
        tag_name (`str`): The name of the tag.
        end_tag (`str`): The end tag for the block tag.
        tag_function (`callable`): The function to call when the
            tag is encountered.
        sub_tag_list (`List[Union[str, TagMatch]]`, optional): A
            list of sub tags for the block tag. A dict can be passed
            to override the tag function for the sub tag.
    """

    if _tag_already_registered(tag_name):
        raise exception.TagAlreadyRegisteredException(
            f'Tag {tag_name} is already registered'
        )

    if sub_tag_list is not None:
        for sub_tag in sub_tag_list:
            if _tag_already_registered(tag_name):
                raise exception.TagAlreadyRegisteredException(
                    f'Sub tag {sub_tag} is already registered'
                )

    _block_tag_map[tag_name] = {
        'end_tag': end_tag,
        'tag_function': tag_function,
        'sub_tags': sub_tag_list
    }


def _register_inline_tag(tag_name: str, tag_function: callable):
    """Registers an inline tag.

    Args:
        tag_name (`str`): The name of the tag.
        tag_function (`callable`): The function to call when the
            tag is encountered.
    """

    if _tag_already_registered(tag_name):
        raise exception.TagAlreadyRegisteredException(
            f'Tag {tag_name} is already registered'
        )

    _inline_tag_map[tag_name] = {
        'tag_function': tag_function
    }


def register_inline_tag(tag_name: str) -> callable:
    """Registers an inline tag.

    Args:
        tag_name (`str`): The name of the tag.

    Returns:
        `callable`: The decorator function.
    """

    def decorator(func):
        _register_inline_tag(tag_name, func)
        return func

    return decorator


def register_block_tag(tag_name: str, end_tag: str,
                       sub_tag_list: Optional[List[
                           Union[str, TagMatch]
                       ]] = None) -> callable:
    """Registers a block tag.

     Args:
        tag_name (`str`): The name of the tag.
            end_tag (`str`): The end tag for the block tag.
            sub_tag_list (`List[Union[str, TagMatch]]`, optional): A
                list of sub tags for the block tag. A dict can be passed
                to override the tag function for the sub tag.

    Returns:
        `callable`: The decorator function.
    """

    def decorator(func):
        _register_block_tag(tag_name, end_tag, func, sub_tag_list)
        return func

    return decorator
