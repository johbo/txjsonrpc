import json

from twisted.trial.unittest import TestCase
from twisted.internet import defer
from txjsonrpc.jsonrpclib import (
    Fault, VERSION_PRE1, VERSION_1, VERSION_2, dumps, loads)


class DumpTestCase(TestCase):

    def test_noVersion(self):
        object = {"some": "data"}
        result = dumps(object)
        self.assertEquals(result, '{"some": "data"}')

    def test_noVersionError(self):
        expected = {
            'fault': 'Fault',
            'faultCode': 'code',
            'faultString': 'message'}

        fault = Fault("code", "message")
        result = dumps(fault)

        self.assertEquals(expected, json.loads(result))

    def test_versionPre1(self):
        object = {"some": "data"}
        result = dumps(object, version=VERSION_PRE1)
        self.assertEquals(result, '{"some": "data"}')

    def test_errorVersionPre1(self):
        expected = {
            'fault': 'Fault',
            'faultCode': 'code',
            'faultString': 'message'}

        fault = Fault("code", "message")
        result = dumps(fault, version=VERSION_PRE1)

        self.assertEquals(expected, json.loads(result))

    def test_version1(self):
        expected = {
            'id': None,
            'result': {'some': 'data'},
            'error': None}

        data = {"some": "data"}
        result = dumps(data, version=VERSION_1)

        self.assertEquals(expected, json.loads(result))

    def test_errorVersion1(self):
        expected = {
            'id': None,
            'result': None,
            'error': {
                'fault': 'Fault',
                'faultCode': 'code',
                'faultString': 'message'}}

        fault = Fault("code", "message")
        result = dumps(fault, version=VERSION_1)

        self.assertEquals(expected, json.loads(result))

    def test_version2(self):
        expected = {'id': None, 'jsonrpc': '2.0', 'result': {'some': 'data'}}

        data = {"some": "data"}
        result = dumps(data, version=VERSION_2)

        self.assertEquals(
            expected, json.loads(result))

    def test_errorVersion2(self):
        expected = {
            'id': None,
            'jsonrpc': '2.0',
            'error': {
                'message': 'Fault',
                'code': 'code',
                'data': 'message'}}

        fault = Fault("code", "message")
        result = dumps(fault, version=VERSION_2)

        self.assertEquals(expected, json.loads(result))


class LoadsTestCase(TestCase):

    def test_loads(self):
        jsonInput = ["1", '"a"', '{"apple": 2}', '[1, 2, "a", "b"]']
        expectedResults = [1, "a", {"apple": 2}, [1, 2, "a", "b"]]
        for input, expected in zip(jsonInput, expectedResults):
            unmarshalled = loads(input)
            self.assertEquals(unmarshalled, expected)

    def test_FaultLoads(self):
        dl = []
        for version in (VERSION_PRE1, VERSION_2, VERSION_1):
            fault = Fault("code", "message")
            d = defer.maybeDeferred(loads, dumps(fault, version=version))
            d = self.assertFailure(d, Fault)

            def callback(exc):
                self.assertEquals(exc.faultCode, fault.faultCode)
                self.assertEquals(exc.faultString, fault.faultString)
            d.addCallback(callback)

            dl.append(d)
        return defer.DeferredList(dl, fireOnOneErrback=True)
