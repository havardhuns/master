import unittest
from aggregate_outputs import value_has_more_than_four_decimals, get_addresses, has_self_change_address, get_index_of_tx_hash

class MyTest(unittest.TestCase):
    def test_value_has_more_than_four_decimals(self):
        self.assertEqual(value_has_more_than_four_decimals(123450000), False)
        self.assertEqual(value_has_more_than_four_decimals(100010000), False)
        self.assertEqual(value_has_more_than_four_decimals(123456000), True)
        self.assertEqual(value_has_more_than_four_decimals(100000000), False)
        self.assertEqual(value_has_more_than_four_decimals(1000), True)
        self.assertEqual(value_has_more_than_four_decimals(10000), False)
        self.assertEqual(value_has_more_than_four_decimals(1), True)
        self.assertEqual(value_has_more_than_four_decimals(0), False)

    def test_get_addresses(self):
        puts = [ { "address" : [ "address1" ] } ]
        self.assertEqual(get_addresses(puts), ["address1"])

        puts = [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] }  ]
        self.assertEqual(get_addresses(puts), ["address1", "address2"])

        puts = [ { "address" : [ "address1" ] }, { "address" : [] }  ]
        self.assertEqual(get_addresses(puts), ["address1"])

        puts = [ { "address" : [] }, { "address" : [] }  ]
        self.assertEqual(get_addresses(puts), [])

    def test_get_addresses_json(self):
        puts = [ { "address" : [{"" : "address1" }] } ]
        self.assertEqual(get_addresses(puts, json=True), ["address1"])

        puts = [ { "address" : [{"" : "address1" }] }, { "address" : [{"" : "address2" }] }  ]
        self.assertEqual(get_addresses(puts, json=True), ["address1", "address2"])

        puts = [ { "address" : [{"" : "address1" }] }, { "address" : [] }  ]
        self.assertEqual(get_addresses(puts, json=True), ["address1"])

        puts = [ { "address" : [] }, { "address" : [] }  ]
        self.assertEqual(get_addresses(puts, json=True), [])

    def test_has_self_change_address(self):
        inputs = [ { "address" : [ "address1" ] } ]
        outputs = [ { "address" : [ "address1" ] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), True)

        inputs = [ { "address" : [ "address1" ] } ]
        outputs = [ { "address" : [ "address2" ] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), False)

        inputs = [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ]
        outputs = [ { "address" : [ "address3" ] }, { "address" : [ "address1" ] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), True)

        inputs = [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ]
        outputs = [ { "address" : [ "address3" ] }, { "address" : [ "address4" ] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), False)

        inputs = [ { "address" : [ "address1" ] }, { "address" : [ "address1" ] } ]
        outputs = [ { "address" : [ "address1" ] }, { "address" : [ "address1" ] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), True)

        inputs = [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ]
        outputs = [ { "address" : [ "address3" ] }, { "address" : [] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), False)

        inputs = [ { "address" : [] } ]
        outputs = [ { "address" : [ "address1" ] } ]
        self.assertEqual(has_self_change_address(inputs, outputs), False)

    def test_get_index_of_tx_hash(self):
        transactions = [{"tx_hash": "1"}, {"tx_hash": "2"}, {"tx_hash": "3"}]

        self.assertEqual(get_index_of_tx_hash("1", transactions), 0)
        self.assertEqual(get_index_of_tx_hash("2", transactions), 1)
        self.assertEqual(get_index_of_tx_hash("3", transactions), 2)
        self.assertEqual(get_index_of_tx_hash("4", transactions), False)

        
