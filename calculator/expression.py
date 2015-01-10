"""
Simple example with to model a multi-step process.
"""


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
                raise Exception('invalid input')
        value = yield '+ or * or ' + (')' if nested else '=')
        if value == '+':
            result += product
            product = 1
        elif value == '*':
            pass
        elif (nested and value == ')') or (not nested and value == '='):
            return result + product
        else:
            raise Exception('invalid input')


if __name__ == '__main__':
    print('Welcome to the Calculator')
    state = expression_gen()
    v = None
    while True:
        try:
            v = input('enter ' + state.send(v) + ': ')
        except StopIteration as e:
            print('result:', e.value)
            break
