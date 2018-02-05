# An Accessory for the flic button
# using https://github.com/50ButtonsEach/fliclib-linux-hci

import sensors.fliclib as fliclib

from pyhap.accessory import Accessory, Category
import pyhap.loader as loader


class FlicButton(Accessory):
    category = Category.PROGRAMMABLE_SWITCH

    def __init__(self, *args, **kwargs):
        super(FlicButton, self).__init__(*args, **kwargs)

        self.switch_char = self.get_service("StatelessProgrammableSwitch") \
            .get_characteristic("ProgrammableSwitchEvent")

        self.flic = fliclib.FlicClient("localhost")

    def _set_services(self):
        super(FlicButton, self)._set_services()
        self.add_service(
            loader.get_serv_loader().get("StatelessProgrammableSwitch"))

    def __getstate__(self):
        state = super(FlicButton, self).__getstate__()
        state["flic"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.flic = fliclib.FlicClient("localhost")

    def got_button(self, bd_addr):
        cc = fliclib.ButtonConnectionChannel(bd_addr)
        cc.on_button_up_or_down = \
            lambda channel, click_type, was_queued, time_diff: \
                print(channel.bd_addr + " " + str(click_type))
        cc.on_connection_status_changed = \
            lambda channel, connection_status, disconnect_reason: \
                print(channel.bd_addr + " " + str(connection_status) + (
                    " " + str(disconnect_reason) if connection_status == fliclib.ConnectionStatus.Disconnected else ""))
        self.flic.add_connection_channel(cc)

    def got_info(self, items):
        print(items)
        for bd_addr in items["bd_addr_of_verified_buttons"]:
            self.got_button(bd_addr)

    def run(self):
        self.flic.get_info(self.got_info)
        self.flic.on_new_verified_button = self.got_button
        self.flic.handle_events()
