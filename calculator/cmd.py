
from interpreter import expression_gen


if __name__ == '__main__':
    print('Welcome to the Calculator')
    state = expression_gen()
    input_value = None
    while True:
        try:
            input_value = input('enter ' + state.send(input_value) + ': ')
        except StopIteration as e:
            print('result:', e.value)
            break
