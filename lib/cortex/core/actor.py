""" cortex.core.actor:
      http://en.wikipedia.org/wiki/Actor_model_theory

  Actor Activation ordering

    The activation ordering (-≈→) is a fundamental ordering that models
    one event activating another (there must be energy flow in the message
    passing from an event to an event which it activates).

        * Because of the transmission of energy, the activation ordering is
        relativistically invariant; that is, for all events e1.e2, if e1 -≈→ e2,
        then the time of e1 precedes the time of e2 in the relativistic frames
        of reference of all observers.

        * Law of Strict Causality for the Activation Ordering:
        For no event does e -≈→ e.

        * Law of Finite Predecession in the Activation Ordering:
        For all events e1 the set {e|e -≈→ e1} is finite.

  Independence of the Law of Finite Chains Between Events in the Combined Ordering

    However, [Clinger 1981] surprisingly proved that the Law of Finite Chains Between Events in the Combined Ordering is independent of the previous laws, i.e.,

    Theorem. The Law of Finite Chains Between Events in the Combined Ordering does not follow from the previously stated laws.

    Proof. It is sufficient to show that there is an Actor computation that satisfies the previously stated laws but violates the Law of Finite Chains Between Events in the Combined Ordering.

        Consider a computation which begins when an actor Initial is sent a Start message causing it to take the following actions

           1. Create a new actor Greeter1 which is sent the message SayHelloTo with the address of Greeter1
           2. Send Initial the message Again with the address of Greeter1

        Thereafter the behavior of Initial is as follows on receipt of an Again message with address Greeteri (which we will call the event Againi):

           1. Create a new actor Greeteri+1 which is sent the message SayHelloTo with address Greeteri
           2. Send Initial the message Again with the address of Greeteri+1

        Obviously the computation of Initial sending itself Again messages never terminates.

        The behavior of each Actor Greeteri is as follows:

            * When it receives a message SayHelloTo with address Greeteri-1 (which we will call the event SayHelloToi), it sends a Hello message to Greeteri-1
            * When it receives a Hello message (which we will call the event Helloi), it does nothing.

        Now it is possible that Helloi -Greeteri→ SayHelloToi every time and therefore Helloi→SayHelloToi.
        Also Againi -≈→ Againi+1 every time and therefore Againi → Againi+1.

        Furthermore all of the laws stated before the Law of Strict Causality for the Combined Ordering are satisfied.
        However, there may be an infinite number of events in the combined ordering between Again1 and SayHelloTo1 as follows:
        Again1→...→Againi→...\infty...→Helloi→SayHelloToi→...→Hello1→SayHelloTo1

    However, we know from physics that infinite energy cannot be expended along a
    finite trajectory (see for example Quantum information and relativity theory).
    Therefore, since the Actor model is based on physics, the Law of Finite Chains
    Between Events in the Combined Ordering was taken as an axiom of the Actor model.

"""

""" implementation 1.
     actor model, one actor per thread. (just a reference implementation)
       taken from: http://www.valuedlessons.com/2008/06/message-passing-conccurrency-actor.html

     much better:
       http://osl.cs.uiuc.edu/parley/
"""
from threading import Thread, Event
from Queue     import Queue, Empty

class IActor:
    pass
    # send(message, sender)

class HandlerRegistry(dict):
    # should be used as a decorator
    def __call__(self, typ):
        def register(func):
            self[typ] = func
            return func
        return register

OtherMessage = "Other Message"

class Stop(Exception):
    def __repr__(self):
        return "Stop()"

class Stopped:
    def __repr__(self):
        return "Stopped()"

class ActorNotStartedError(Exception):
    def __init__(self):
        Exception.__init__(self, "actor not started")

class Actor(IActor):
    @classmethod
    def spawn(cls, *args, **kargs):
        self = cls(*args, **kargs)
        self.mailbox = Mailbox()
        start_thread(target = self.act, as_daemon = True)
        return self

    def send(self, message, sender):
        if self.mailbox is None:
            raise ActorNotStartedError()
        else:
            self.mailbox.send(message, sender)

    def receive(self):
        if self.mailbox is None:
            raise ActorNotStartedError()
        else:
            return self.mailbox.receive()

    # override if necessary
    def act(self):
        self.handleMessages()



    handles = HandlerRegistry()

    @classmethod
    def makeHandles(*classes):
        return HandlerRegistry((typ, handler) for cls in classes for (typ, handler) in cls.handles.iteritems())

    def handleMessages(self):
        try:
            while True:
                message, sender = self.receive()
                self.handleMessageWithRegistry(message, sender)
        except Stop:
            pass

    def handleMessageWithRegistry(self, message, sender):
        registry = self.__class__.handles
        handler  = registry.get(message.__class__) or registry.get(OtherMessage)
        if handler is not None:
            handler(self, message, sender)

    @handles(OtherMessage)
    def onOther(self, message, sender):
        pass

    @handles(Stop)
    def onStop(self, message, sender):
        sender.send(Stopped(), self)
        raise message

def start_thread(target, as_daemon, name = None):
    thread = Thread(target = target)
    if name:
        thread.setName(name)
    thread.setDaemon(as_daemon)
    thread.start()
    return thread

class Mailbox:
    def __init__(self):
        self.mailbox = Queue()

    def send(self, message, sender):
        self.mailbox.put((message, sender), block = False)

    def receive(self, timeout = None):
        return self.mailbox.get(block = True, timeout = timeout)

class Bridge(IActor):
    def __init__(self):
        self.mailbox = Mailbox()

    def send(self, message, sender):
        self.mailbox.send(message, sender)

    def call(self, target, request, timeout, default = None):
        self.sendRequest(target, request)
        return self.receiveResponse(timeout, default)

    # targeted_requests can be an iterator
    def multiCall(self, targeted_requests, timeout, default = None):
        count = 0
        for target, request in targeted_requests:
            self.sendRequest(target, request)
            count += 1

        for _ in xrange(count):
            yield self.receiveResponse(timeout, default)

    def stop(self, actors, timeout):
        stop = Stop()
        return list(self.multiCall(((actor, stop) for actor in actors), timeout, default = None))

    def sendRequest(self, target, request):
        target.send(request, self)

    def receiveResponse(self, timeout, default):
        try:
            message, sender = self.mailbox.receive(timeout = timeout)
            return message
        except Empty:
            return default


if __name__ == "__main__":
    import time

    class GetInventory:
        pass

    class Task:
        def __init__(self, input, destination):
            self.input       = input
            self.destination = destination

    class Worker(Actor):
        handles = Actor.makeHandles()

        def __init__(self, skill):
            self.skill = skill

        @handles(Task)
        def onTask(self, task, sender):
            output = self.skill(task.input)
            task.destination.send(output, self)

    class Warehouse(Actor):
        handles = Actor.makeHandles()

        def __init__(self):
            self.inventory = []

        @handles(GetInventory)
        def onGetInventory(self, message, sender):
            # copy the inventory to avoid anyone mutating it
            sender.send(list(self.inventory), self)

        @handles(OtherMessage)
        def onTaskResult(self, result, sender):
            self.inventory.append(result)

    worker    = Worker.spawn(lambda x : x * 2)
    positives = Warehouse.spawn()
    negatives = Warehouse.spawn()
    bridge    = Bridge()

    for val in [1, 2, 3, -2, -4, -6]:
        warehouse = positives if val >= 0 else negatives
        worker.send(Task(val, warehouse), sender = None)

    print bridge.call(positives, GetInventory(), 1.0) #should be [ 2,  4,   6]
    print bridge.call(negatives, GetInventory(), 1.0) #should be [-4, -8, -12]
    print bridge.stop([worker, positives, negatives], 1.0) #should be [Stopped(), Stopped(), Stopped()]


    class Start:
        def __init__(self, target):
            self.target = target

    class Ping:
        def __repr__(self):
            return "Ping()"

    class Pong:
        def __repr__(self):
            return "Pong()"

    class Pinger(Actor):
        handles = Actor.makeHandles()

        @handles(Start)
        def onStart(self, start, sender):
            start.target.send(Ping(), self)

        @handles(Pong)
        def onPong(self, pong, sender):
            print "-",
            sender.send(Ping(), self)

    class Ponger(Actor):
        handles = Actor.makeHandles()

        @handles(Ping)
        def onPing(self, ping, sender):
            print "+",
            sender.send(Pong(), self)

    # should print lots of +-+-+-
    pinger = Pinger.spawn()
    ponger = Ponger.spawn()
    pinger.send(Start(ponger), sender = None)
    time.sleep(0.1)
    bridge.stop([pinger, ponger], 1.0)
