#!/usr/bin/python3

from webthing import (
    Event,
    Thing,
    WebThingServer
)
from asyncio import (
    Task,
    sleep,
    gather
)
from tornado import (
    IOLoop
)


class TargetDown(Event):
    def __init__(self, thing, data):
        super(TargetDown, self).__init__(thing, 'target_down', data=data)


class RestartTarget(Event):
    def __init__(self, thing, data):
        super(RestartTarget, self).__init__(thing, 'restart_target', data=data)


class PingThing(Thing):
    def __init__(self, ping_target_address):
        super(PingThing, self).__init__(
            name='ping_thing',
            description='a Linux service as a Web Thing'
        )
        self.add_available_event(
            "target_down",
            {
                "description": "the target service is down",
                "type": "boolean"
            }
        )
        self.add_available_event(
            "restart_target",
            {
                "description": "the target should restart",
                "type": "boolean"
            }
        )

        self.ping_target_address = ping_target_address
        self.target_up = True

    async def ping(self):
        pass  # TODO write ping code

    async def monitor_target(self):
        while True:
            await self.ping()
            if self.target_up:
                await sleep(60.0)
                continue
            self.add_event(TargetDown(self, True))
            await sleep(30.0)
            self.add_event(RestartTarget(self, True))
            await sleep(60.0)


def run_server():
    print('run server')

    ping_monitor = PingThing('192.168.168.1')

    server = WebThingServer([ping_monitor], port=8888)
    try:
        print('server.start')
        # the Tornado Web server has uses an asyncio event loop.  We want to
        # add tasks to that event loop, so we must reach into Tornado to get it
        io_loop = IOLoop.current().asyncio_loop
        print('create task')
        io_loop.create_task(ping_monitor.monitor_target())

        server.start()

    except KeyboardInterrupt:
        print('server.stop')
        # when stopping the server, we need to halt any tasks pending from the
        # method 'monitor_target'. Gather them together and cancel them en masse.
        pending_tasks_in_a_group = gather(*Task.all_tasks(), return_exceptions=True)
        pending_tasks_in_a_group.cancel()
        # let the io_loop run until the all the tasks complete their cancelation
        io_loop.run_until_complete(pending_tasks_in_a_group)
        # finally stop the server
        server.stop()


if __name__ == '__main__':
    print('main')
    run_server()
