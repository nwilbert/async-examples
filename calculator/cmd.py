
from interpreter import expression_gen


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
