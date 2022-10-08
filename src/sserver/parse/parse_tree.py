"""Definitions for a parse tree."""

from typing import Any, List, Optional, Union
from sserver.parse import exception
from sserver.parse.literal import (
    Evaluatable,
    Operator,
    Context
)


# Alias for expression item
ExpressionItem = Union[Operator, Evaluatable]


class Expression(Evaluatable):
    """Represents an expression."""

    def __init__(self, items: List[ExpressionItem]):
        self._items: List[ExpressionItem] = items

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, items: {self._items}>'

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index: int) -> ExpressionItem:
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def evaluate(self, context: Context) -> Optional[Any]:
        """Evaluates the expression to a value.

        Args:
            context (`Context`): The context variables.

        Returns:
            `Any`: The value of the expression. If the expression is
                empty, `None` is returned.
        """

        # If only a single item was in the expression, that is the
        # expressions evaluated value
        if len(self._items) == 1:
            item = self._items[0]

            # If the item is an evaluatable, evaluate it
            if isinstance(item, Evaluatable):
                return item.evaluate(context)

            # Check if the operator is a constant
            if item.argument_count == 0:
                # If the item is a constant call it to get the value
                return item()

            # If the operator is not a constant, it is not evaluable
            raise exception.ExpressionSyntaxException(
                f'Unexpected operator: {item}'
            )

        # Construct a parse tree and get its value
        return ParseTree(self).evaluate(context)


class ParseTree:
    """Represents a parse tree following operator precedence."""

    def __init__(self, expression: Expression):
        # Ensure the given expression is an expression object
        if not isinstance(expression, Expression):
            raise TypeError((
                'expression must be of type Expression '
                f'not {type(expression)}'
            ))

        self.expression = expression

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'<{class_name}, expression: {self.expression}>'

    def _get_reconstructed_expression(self) -> str:
        """Gets the reconstructed expression.

        Returns:
            `str`: The reconstructed expression.
        """

        return ' '.join(
            map(
                lambda item: str(item),
                self.expression
            )
        )

    def evaluate(self, context: Context) -> Optional[Any]:
        """Evaluates the parse tree to a value.

        Returns:
            `Any`: The evaluated parse tree. None if there are no
                no items to evaluate.

        Raises:
            `ExpressionSyntaxException`: If the operator being
                evaluated does not have all necessary operands, or
                if the expression evaluates to multiple values, or
                if an operator that takes more than 2 arguments is
                used.
        """

        # First evaluate all literals, identifiers and expressions
        # in the expression
        evaluated_items = list(
            map(
                lambda item: item.evaluate(context) if isinstance(
                    item, Evaluatable
                ) else item,
                self.expression
            )
        )

        # Next, create create a list of operatrs and their index
        # in order of precedence (highest to lowest)
        operator_matches = [
            [index, operator]
            for index, operator in enumerate(evaluated_items)
            if isinstance(operator, Operator)
        ]

        # Sort operators by precedence (highest to lowest)
        operator_matches.sort(
            key=lambda operator: operator[1].precedence,
            reverse=True
        )

        # Using the sorted operators, calculate the expression value
        for index, operator in operator_matches:
            # First get the number of expected arguments for the
            # operator
            # @note expected_args of 1 always defaults to a right arg
            expected_args = operator.argument_count

            # Check variables
            has_left_operand = False
            has_right_operand = False

            # For operators that take no arguments, replace in place
            if expected_args == 0:
                evaluated_items[index] = operator()
                continue

            elif expected_args == 1:
                has_right_operand = True

            elif expected_args == 2:
                has_left_operand = True
                has_right_operand = True

            else:
                # If more than 2 operators are expected, an
                # unsupported operator was used
                raise exception.ExpressionSyntaxException(
                    f'Unsupported operator: {operator}'
                )

            # Check left and right operands
            if has_left_operand and index - 1 < 0:
                raise exception.ExpressionSyntaxException((
                    f'Operator {operator} is missing a left operand '
                    f'near {self._get_reconstructed_expression()}'
                ))

            evaluated_items_len = len(evaluated_items)
            if has_right_operand and index + 1 >= evaluated_items_len:
                raise exception.ExpressionSyntaxException((
                    f'Operator {operator} is missing a right operand '
                    f'near {self._get_reconstructed_expression()}'
                ))

            # Get the left and right operands
            operator_args = []

            if has_left_operand:
                operator_args.append(evaluated_items[index - 1])

            if has_right_operand:
                operator_args.append(evaluated_items[index + 1])

            value = operator(*operator_args)

            # Replace the operator and operands with the calculated value
            index_to_replace = index
            index_to_remove_from = index + 1

            if has_left_operand:
                index_to_replace -= 1
                index_to_remove_from -= 1

            evaluated_items[index_to_replace] = value

            for _ in range(expected_args):
                del evaluated_items[index_to_remove_from]

            # Decrement the index of all operators after the current
            # operator
            for operator_match in operator_matches:
                operator_list_index = operator_match[0]

                if operator_list_index > index:
                    operator_match[0] -= expected_args

        # If there are no evaluated items, return None
        if len(evaluated_items) == 0:
            return None

        # Check the evaluated items length is now 1
        if len(evaluated_items) != 1:
            raise exception.ExpressionSyntaxException((
                f'Expression "{self._get_reconstructed_expression()}"'
                ' is not valid'
            ))

        # Return the evaluated value
        return evaluated_items[0]
