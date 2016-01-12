from qualipy.api.cloudshell_api import AttributeNameValue


class VnicUpdater(object):
    def __init__(self, qualipy_helpers):
        self.qualipy_helpers = qualipy_helpers

    def update_vnics(self, update_mapping, source_resource_full_name, target_resource_full_name):
        reservation_id = self.qualipy_helpers.get_reservation_context_details().id

        for vnic, network, connect in update_mapping:
            self.qualipy_helpers.SetConnectorAttributes(reservation_id,
                                                        source_resource_full_name,
                                                        target_resource_full_name,
                                                        {AttributeNameValue('Target Interface', vnic.macAddress)})
            break
