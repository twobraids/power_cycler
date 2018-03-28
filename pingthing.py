#!/usr/bin/python3

from webthing import (
    Event,
    Thing,
    WebThingServer
)
from asyncio import (
    Task,
    CancelledError,
    sleep,
    gather
)
from tornado.ioloop import (
    IOLoop
)
from aiohttp import (
    ClientSession
)
from async_timeout import (
    timeout
)
from configman import (
    configuration,
    Namespace
)

required_config = Namespace()
required_config.add_option(
    'target_url',
    doc='the url to test',
    default='http://uncommonrose.com'
)
required_config.add_option(
    'seconds_for_timeout',
    doc='the number of seconds to allow before assuming the service is down',
    default=10
)
required_config.add_option(
    'seconds_between_tests',
    doc='the number of seconds between each test trial',
    default=120
)
required_config.add_option(
    'seconds_to_leave_service_off',
    doc='the number of seconds to leave the service off after shutting it down',
    default=60
)
required_config.add_option(
    'seconds_to_restore_service',
    doc='the number of seconds required to power up the service',
    default=90
)


class TargetDownEvent(Event):
    def __init__(self, thing, data):
        super(TargetDownEvent, self).__init__(thing, 'target_down', data=data)


class RestartTargetEvent(Event):
    def __init__(self, thing, data):
        super(RestartTargetEvent, self).__init__(thing, 'restart_target', data=data)


class PingThing(Thing):
    def __init__(self, config):
        self.config = config
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

        self.target_up = True

    async def ping(self):
        print('executing ping')
        try:
            async with ClientSession() as session:
                async with timeout(config.seconds_for_timeout):
                    async with session.get(config.target_url) as response:
                        await response.text()
        except CancelledError as e:
            print('ping shutdown')
            raise e
        except Exception:
            print('target error')
            self.target_up = False

    async def monitor_target(self):
        while True:
            await self.ping()
            if self.target_up:
                print('sleep between tests for {} seconds'.format(config.seconds_between_tests))
                await sleep(config.seconds_between_tests)
                continue
            print('add TargetDown')
            self.add_event(TargetDownEvent(self, True))
            print('leave service off for {} seconds'.format(config.seconds_to_leave_service_off))
            await sleep(config.seconds_to_leave_service_off)
            print('add RestartTarget')
            self.add_event(RestartTargetEvent(self, True))
            print('allow time for service to restart for {} seconds'.format(config.seconds_to_restore_service))
            await sleep(config.seconds_to_restore_service)
            self.target_up = True


def run_server(config):
    print('run server')

    ping_monitor = PingThing(config)

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
    config = configuration(required_config)
    for key, value in config.items():
        print('{}: {}'.format(key, value))
    print('main')
    run_server(config)
