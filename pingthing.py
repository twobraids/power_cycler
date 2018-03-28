from webthing import (
    Action,
    Event,
    Property,
    Thing,
    WebThingServer
)

class TargetDown(Event):
    def __init__(self, thing, data):
        super(TargetDown, self).__init__(thing, 'target_down', data=data)



class PingThing(Thing):
    def __init__(self):
        super(PingThing, self).__init__(
            name='ping_thing',
            description='a Linux service as a Web Thing'
        )
#         self.add_property(
#             Property(
#                 self,
#                 'up',
#                 metadata={
#                     'type': 'boolean',
#                     'description': 'is the target service up?'
#                 },
#                 value=True
#             )
#         )
        self.add_available_event(
            "target_down",
            {
                "description": "the target service is down",
                "type": "boolean"
            }
        )

