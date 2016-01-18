from qualipy.api.cloudshell_api import AttributeNameValue


class VnicUpdater(object):
    def __init__(self, qualipy_helpers, logger):
        self.qualipy_helpers = qualipy_helpers
        self.logger = logger

    def update_vnics(self, update_mapping):
        reservation_id = self.qualipy_helpers.get_reservation_context_details().id

        self.logger.debug('update_vnics')
        for mapping in update_mapping:

            attrs = vars(mapping)
            self.logger.info( ', '.join("%s: %s" % item for item in attrs.items()) )

#            target_resource_full_name = mapping.network.network.name
#            mac_address = vnic.macAddress
#            session = self.qualipy_helpers.get_api_session()
#            session.SetConnectorAttributes(reservation_id,
#                                           source_resource_full_name,
#                                           target_resource_full_name,
#                                           [AttributeNameValue('Target Interface', )])
#            break
