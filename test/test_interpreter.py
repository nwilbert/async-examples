
import unittest

from calculator.interpreter import expression_gen


class ExpressionTests(unittest.TestCase):

    def assert_expression_result(self, values, expected_result):
        state = expression_gen()
        next(state)
        for value in values:
            state.send(value)
        try:
            state.send('=')
        except StopIteration as e:
            self.assertEqual(e.value, expected_result)

    def test_expression_results(self):
        self.assert_expression_result(['2', '*', '3'], 6)
        self.assert_expression_result(['2', '+', '3'], 5)
        self.assert_expression_result(['2', '+', '3', '*', '4'], 14)
        self.assert_expression_result(['2', '*', '(', '3', '+', '4', ')'], 14)
