from unittest import TestCase
from common.utilites.command_result import get_result_from_command_output, set_command_result
from models.ConnectionResult import ConnectionResult


class TestCommandResult(TestCase):

    def test_get_result_from_command_output_with_result(self):
        result = get_result_from_command_output('command_json_result={"result":"MY RESULT"}=command_json_result_end')
        self.assertEqual(result["result"], 'MY RESULT')

    def test_command_result_empty(self):
        result = get_result_from_command_output('')
        self.assertEqual(result, None)

    def test_get_result_from_command_output_with_result_unpickable_true(self):

        connection_result = ConnectionResult(mac_address='AA', vm_uuid='BB', network_name='CC')
        output_result = set_command_result(result=connection_result, unpicklable=True)
        result = get_result_from_command_output(output_result)

        self.assertEqual(result.mac_address, 'AA')
        self.assertEqual(result.vm_uuid, 'BB')
        self.assertEqual(result.network_name, 'CC')

    def test_get_result_from_command_output_with_result_unpickable_false(self):

        connection_result = ConnectionResult(mac_address='AA', vm_uuid='BB', network_name='CC')
        output_result = set_command_result(result=[connection_result], unpicklable=False)
        results = get_result_from_command_output(output_result)

        self.assertEqual(results[0]['mac_address'], 'AA')
        self.assertEqual(results[0]['vm_uuid'], 'BB')
        self.assertEqual(results[0]['network_name'], 'CC')
        
    def test_get_result_from_command_output_with_result(self):
        
        output_result = 'command_json_result=[{"py/object": "models.ConnectionResult.ConnectionResult", "vm_uuid": "422258ab-47e9-d57c-3741-6832a432bc3a", "network_name": "QualiSB/anetwork", "mac_address": "00:50:56:a2:23:76"}]=command_json_result_end'
        results = get_result_from_command_output(output_result)

        self.assertEqual(results[0].mac_address, '00:50:56:a2:23:76')

    def test_get_result_from_command_output_with_result_unpickable_false(self):

        output_result = 'command_json_result=[{"vm_uuid": "422258c6-15d0-0646-d5e7-f2cb411eee94", "network_name": "QualiSB/anetwork", "mac_address": "00:50:56:a2:6c:04"}]=command_json_result_end'
        results = get_result_from_command_output(output_result)

        for result in results:
            v = dict(result)
            self.assertEqual(result['mac_address'], '00:50:56:a2:6c:04')
