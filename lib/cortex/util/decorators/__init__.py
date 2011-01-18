""" cortex.util.decorators.__init__
"""

from cortex.core.util import report
from cortex.util.decorators.abstract import StrictSimpleAnnotator
from cortex.util.decorators.function_annotator import FunctionAnnotator
from cortex.util.decorators.abstract import AbstractDecorator
from cortex.util.decorators.abstract import SingleArgumentDecorator

from cortex.util.decorators.emits import emits

from cortex.util.decorators.wrappers import call_first_if_exists
from cortex.util.decorators.wrappers import call_after_if_exists
from cortex.util.decorators.wrappers import chain_after_if_exists

from cortex.util.decorators.reactor_recursion import recurse_with_reactor
from cortex.util.decorators.constraint import constraint

class handles_event(StrictSimpleAnnotator):
    label_name = 'handles_event'
handle_event = handles_event
handles      = handle_event

class handles_and_consumes_event(StrictSimpleAnnotator):
    label_name = 'handles_and_consumes_event'
handle_and_consume   = handles_and_consumes_event
handles_and_consumes = handles_and_consumes_event
