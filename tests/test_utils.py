import unittest

from eveviewer import utils


class TestListsAreEqual(unittest.TestCase):
    def test_equal_lists_return_true(self):
        self.assertTrue(utils.lists_are_equal([1, 2, 3], [1, 2, 3]))

    def test_lists_with_different_length_return_false(self):
        self.assertFalse(utils.lists_are_equal([1, 2, 3], [1, 2]))

    def test_lists_with_same_elements_and_different_order_return_true(self):
        self.assertTrue(utils.lists_are_equal([1, 2, 3], [1, 3, 2]))

    def test_lists_with_different_elements_return_false(self):
        self.assertFalse(utils.lists_are_equal([1, 2, 3], [4, 5, 6]))


class TestNotifyingList(unittest.TestCase):
    def setUp(self):
        self.called = False

    def notify(self):
        self.called = True

    def test_append_notifies(self):
        test_list = utils.NotifyingList(callback=self.notify)
        test_list.append("foo")
        self.assertTrue(self.called)

    def test_remove_notifies(self):
        test_list = utils.NotifyingList(callback=self.notify)
        test_list.append("foo")
        self.called = False
        test_list.remove("foo")
        self.assertTrue(self.called)

    def test_append_without_callback_does_not_notify(self):
        test_list = utils.NotifyingList()
        test_list.append("foo")
        self.assertFalse(self.called)

    def test_remove_without_callback_does_not_notify(self):
        test_list = utils.NotifyingList()
        test_list.append("foo")
        test_list.remove("foo")
        self.assertFalse(self.called)


if __name__ == "__main__":
    unittest.main()
