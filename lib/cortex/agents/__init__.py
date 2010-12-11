""" cortex.agents

      Holds reusable agent definitions.
      Looking for the core agent functionality?  see cortex.core.agent
"""

# Core functionality
from cortex.core.agent import Agent, AgentManager

# Misc. shortcuts for importing particular agents
from cortex.agents.turntaker import TurnTaker
from cortex.agents.workers import TaskIterator
