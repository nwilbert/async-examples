"""
Simple example with to model a multi-step process.
"""


def expression():
    result = 0
    product = 1
    while True:
        value = yield 'number or ('
        if value == '(':
            product *= yield from expression()
        else:
            try:
                product *= int(value)
            except ValueError:
                raise Exception('invalid input')
        value = yield '+ or * or ) or ='
        if value == '+':
            result += product
            product = 1
        elif value == '*':
            pass
        elif value == ')':
            return result + product
        else:
            raise Exception('invalid input')


if __name__ == '__main__':
    print('enter ) at top level to terminate')
    state = expression()
    v = None
    while True:
        try:
            v = input('enter ' + state.send(v) + ': ')
        except StopIteration as e:
            print('result:', e.value)
            break
