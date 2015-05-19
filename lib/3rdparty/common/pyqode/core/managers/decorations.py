"""
Contains the text decorations manager
"""
import logging
from pyqode.core.api.manager import Manager


def _logger():
    return logging.getLogger(__name__)


class TextDecorationsManager(Manager):
    """
    Manages the collection of TextDecoration that have been set on the editor
    widget.
    """
    def __init__(self, editor):
        super(TextDecorationsManager, self).__init__(editor)
        self._decorations = []

    def append(self, decoration):
        """
        Adds a text decoration on a CodeEdit instance

        :param decoration: Text decoration to add
        :type decoration: pyqode.core.api.TextDecoration
        """
        if decoration not in self._decorations:
            self._decorations.append(decoration)
            self._decorations = sorted(
                self._decorations, key=lambda sel: sel.draw_order)
            self.editor.setExtraSelections(self._decorations)
            return True
        return False

    def remove(self, decoration):
        """
        Removes a text decoration from the editor.

        :param decoration: Text decoration to remove
        :type decoration: pyqode.core.api.TextDecoration
        """
        try:
            self._decorations.remove(decoration)
            self.editor.setExtraSelections(self._decorations)
            return True
        except ValueError:
            return False

    def clear(self):
        """
        Removes all text decoration from the editor.

        """
        self._decorations[:] = []
        self.editor.setExtraSelections(self._decorations)

    def __iter__(self):
        return iter(self._decorations)

    def __len__(self):
        return len(self._decorations)
