""""""
from cortex.core.api import publish

class APICheck(TestCase):
    def test_api_publish(self):
        contents = publish()
        self.assertTrue('do' in contents)
        self.assertTrue('declare_goals' in contents)
        self.assertTrue('universe' in contents)

    def test_api_instruction(self):
        instruction([['load', 'service', {}]])

    def test_do(self):
        [['load', 'service', {}]]
