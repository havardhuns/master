import unittest
from heuristics_otc import value_has_more_than_four_digits_after_dot, get_addresses, has_self_change_address, otc_value_is_smaller_than_all_input_values

class MyTest(unittest.TestCase):
    def test_value_has_more_than_four_decimals(self):
        self.assertFalse(value_has_more_than_four_digits_after_dot(123450000))
        self.assertFalse(value_has_more_than_four_digits_after_dot(100010000))
        self.assertTrue(value_has_more_than_four_digits_after_dot(123456000))
        self.assertFalse(value_has_more_than_four_digits_after_dot(100000000))
        self.assertTrue(value_has_more_than_four_digits_after_dot(1000))
        self.assertFalse(value_has_more_than_four_digits_after_dot(10000))
        self.assertTrue(value_has_more_than_four_digits_after_dot(1))
        self.assertFalse(value_has_more_than_four_digits_after_dot(0))

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
        transaction = {
            "inputs": [ { "address" : [ "address1" ] } ],
            "outputs": [ { "address" : [ "address1" ] } ]
        }
        self.assertTrue(has_self_change_address(transaction))

        transaction = {
            "inputs": [ { "address" : [ "address1" ] } ],
            "outputs": [ { "address" : [ "address2" ] } ]
        }
        self.assertFalse(has_self_change_address(transaction))

        transaction = {
            "inputs": [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ],
            "outputs": [ { "address" : [ "address3" ] }, { "address" : [ "address1" ] } ]
        }
        self.assertTrue(has_self_change_address(transaction))

        transaction = {
            "inputs": [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ],
            "outputs": [ { "address" : [ "address3" ] }, { "address" : [ "address4" ] } ]
        }
        self.assertFalse(has_self_change_address(transaction))

        transaction = {
            "inputs": [ { "address" : [ "address1" ] } ],
            "outputs": [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ]
        }
        self.assertTrue(has_self_change_address(transaction))

        transaction = {
            "inputs": [ { "address" : [ "address1" ] }, { "address" : [ "address2" ] } ],
            "outputs": [ { "address" : [ "address3" ] }, { "address" : [ ] } ]
        }
        self.assertFalse(has_self_change_address(transaction))

        transaction = {
            "inputs": [ { "address" : [ ] } ],
            "outputs": [ { "address" : [ "address1" ] }]
        }
        self.assertFalse(has_self_change_address(transaction))

    def test_otc_value_is_smaller_than_all_input_values(self):
        inputs = [{"value": {"value": 100000000}}]
        self.assertTrue(otc_value_is_smaller_than_all_input_values(999, inputs))

        inputs = [{"value": {"value": 999}}]
        self.assertFalse(otc_value_is_smaller_than_all_input_values(1000, inputs))

        inputs = [{"value": {"value": 1000}}, {"value": {"value": 1001}}, ]
        self.assertTrue(otc_value_is_smaller_than_all_input_values(999, inputs))

        inputs = [{"value": {"value": 999}}, {"value": {"value": 1001}}, ]
        self.assertFalse(otc_value_is_smaller_than_all_input_values(1000, inputs))

        inputs = [{"value": {"value": 1000}}, {"value": {"value": 2000}}, {"value": {"value": 998}}, {"value": {"value": 99912931299}},]
        self.assertFalse(otc_value_is_smaller_than_all_input_values(999, inputs))  