""" cortex.tests.__main__

    tests for cortex.  these tests are arbitrated by the unittest
    service which itself is an agent in cortex.  turns out the best
    place to run tests are to be inside the system that's being
    tested..

    execute like this:

      $ python -m"cortex.tests.__main__"
      $ python <src>/cortex/tests/

      >>> ...

"""

from cortex.tests import main
main()
