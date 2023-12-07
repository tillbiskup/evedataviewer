"""
General utils of the eveviewer package.

Mostly small functions that are more general and get used in the other
modules.
"""


def lists_are_equal(list1, list2):
    """
    Check whether two lists contain only identical items.

    The sequence of the items does not matter, as otherwise, one could
    simply use the equal operator ``==``. Furthermore, the two lists are
    not sorted or otherwise altered.

    Parameters
    ----------
    list1 : :class:`list`
        First list to compare to second list

    list2 : :class:`list`
        Second list to compare to first list

    Returns
    -------
    equal : :class:`bool`
        Whether the two lists are equal

    """
    return len(list1) == len(list2) and len(
        [1 for i in list1 if i in list2]
    ) == len(list1)


class NotifyingList(list):
    """
    List calling a given function when items are added or removed.

    In order to get notified when items are appended to or removed from a
    list, you can register a callback function in the :attr:`callback` that
    gets called whenever changes occur -- and the callback is set.

    Besides that, simply the methods of the superclass :class:`list` are called.

    Attributes
    ----------
    callback : :py:obj:`function <types.FunctionType>`
        Function to be called whenever items are added/removed


    .. note::

        Currently, only :meth:`append` and :meth:`remove` are handled. Add
        further methods as necessary.

    """

    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def append(self, value):
        """
        Add element to the list

        Parameters
        ----------
        value
            Element to be added to the list

        """
        super().append(value)
        if self.callback:
            self.callback()

    def remove(self, value):
        """
        Remove element from the list

        Parameters
        ----------
        value
            Element to be removed from the list

        """
        super().remove(value)
        if self.callback:
            self.callback()
