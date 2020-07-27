class Observer:
    """Observer base class"""

    def update(self):
        """Gets invoked when the observable has a change in state

        :raises NotImplementedError: To ensure that it gets implemented
        """

        raise NotImplementedError


class Observable:
    """Observable base class"""

    def __init__(self):
        self.observers = []
        self.changed = False

    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def delete_observer(self, observer):
        self.observers.remove(observer)

    async def notify_observers(self):
        """Notify all observers when the state has changed

        When the change flag indicates the state has changed, run update()
        on all observers and clear the flag
        """

        if not self.changed:
            return

        self.clear_changed()

        for observer in self.observers:
            await observer.update()

    def delete_observers(self): self.observers = []

    def set_changed(self): self.changed = True

    def clear_changed(self): self.changed = False

    def has_changed(self): return self.changed

    def count_observers(self): return len(self.observers)