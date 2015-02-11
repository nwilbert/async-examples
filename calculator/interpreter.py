
import asyncio


class InvalidValue(Exception):
    pass


@asyncio.coroutine
def expression_gen(nested=False):
    result = 0
    product = 1
    while True:
        value = yield 'number or ('
        if value == '(':
            product *= yield from expression_gen(nested=True)

        else:
            try:
                product *= int(value)
            except ValueError:
                raise InvalidValue()

        value = yield '+ or * or ' + (')' if nested else '=')
        if value == '+':
            result += product
            product = 1
        elif value == '*':
            pass

        elif (nested and value == ')') or (not nested and value == '='):
            return result + product
        else:
            raise InvalidValue()



