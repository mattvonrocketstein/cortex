""" cortex.core.tasks
"""
class TaskList(Agent):
    """ """
    def _post_init(self, tasks=[]):
        """ """
        self.tasks = tasks

    def start(self):
        """ """
        while self.tasks:
            task = self.tasks.pop()
            task()
