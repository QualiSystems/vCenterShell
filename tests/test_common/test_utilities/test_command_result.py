from unittest import TestCase

from vCenterShell.models.ActionResult import ActionResult
from vCenterShell.models.ConnectionResult import ConnectionResult

from vCenterShell.common.utilites.command_result import get_result_from_command_output, set_command_result
from vCenterShell.models.DriverResponse import DriverResponse, DriverResponseRoot


class TestCommandResult(TestCase):
    def test_get_result_from_command_output_with_result(self):
        result = get_result_from_command_output('command_json_result={"result":"MY RESULT"}=command_json_result_end')
        self.assertEqual(result["result"], 'MY RESULT')

    def test_command_result_empty(self):
        result = get_result_from_command_output('')
        self.assertEqual(result, None)

    def test_get_result_from_command_output_with_result_unpickable_true(self):
        connection_result = ConnectionResult(mac_address='AA', vm_uuid='BB', network_name='CC', network_key='DD')
        output_result = set_command_result(result=connection_result, unpicklable=True)
        result = get_result_from_command_output(output_result)

        self.assertEqual(result.mac_address, 'AA')
        self.assertEqual(result.vm_uuid, 'BB')
        self.assertEqual(result.network_name, 'CC')
        self.assertEqual(result.network_key, 'DD')

    def test_get_result_from_command_output_with_result_unpickable_false(self):
        connection_result = ConnectionResult(mac_address='AA', vm_uuid='BB', network_name='CC', network_key='DD')
        output_result = set_command_result(result=[connection_result], unpicklable=False)
        results = get_result_from_command_output(output_result)

        self.assertEqual(results[0]['mac_address'], 'AA')
        self.assertEqual(results[0]['vm_uuid'], 'BB')
        self.assertEqual(results[0]['network_name'], 'CC')
        self.assertEqual(results[0]['network_key'], 'DD')

    def test_get_result_from_command_output_with_result(self):
        output_result = 'command_json_result=[{"py/object": "vCenterShell.models.ConnectionResult.ConnectionResult", "vm_uuid": "422258ab-47e9-d57c-3741-6832a432bc3a", "network_name": "QualiSB/anetwork", "mac_address": "00:50:56:a2:23:76"}]=command_json_result_end'
        results = get_result_from_command_output(output_result)

        self.assertEqual(results[0].mac_address, '00:50:56:a2:23:76')

    def test_get_result_from_command_output_with_result_unpickable_false(self):
        output_result = 'command_json_result=[{"vm_uuid": "422258c6-15d0-0646-d5e7-f2cb411eee94", "network_name": "QualiSB/anetwork", "mac_address": "00:50:56:a2:6c:04"}]=command_json_result_end'
        results = get_result_from_command_output(output_result)

        for result in results:
            v = dict(result)
            self.assertEqual(result['mac_address'], '00:50:56:a2:6c:04')

    def test_set_command_result(self):
        action_result = ActionResult()
        action_result.actionId = 'A'
        action_result.errorMessage = ''
        action_result.infoMessage = ''
        action_result.success = True
        action_result.type = 'setVlan'
        action_result.updatedInterface = 'AA-BB'

        driver_response = DriverResponse()
        driver_response.actionResults = [action_result]

        driver_response_root = DriverResponseRoot()
        driver_response_root.driverResponse = driver_response

        result = set_command_result(driver_response_root)

        self.assertEqual(result, 'command_json_result={"driverResponse": {"actionResults": [{"success": true, "updatedInterface": "AA-BB", "errorMessage": "", "infoMessage": "", "actionId": "A", "type": "setVlan"}]}}=command_json_result_end')
