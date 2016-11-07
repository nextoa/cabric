# -*- coding: utf-8 -*-

from cliez.slot import SlotComponent
import threading


class WatcherComponent(SlotComponent):
    # un-comment this can disable global options
    # exclude_global_option = True

    class Handle(SlotComponent.Handle):

        todo_list = []

        def initialize(self):
            if self.options.small:
                self.todo_list = list(range(0, 10))
            else:
                self.todo_list = list(range(0, 20))
            pass

        def __enter__(self):
            if not self.todo_list:
                self.component.print_message("{}:No todo data found, waiting {}s...".format(threading.current_thread().name, self.options.sleep))
                return False
            else:
                return self.todo_list.pop()

        def slot(self, msg):
            self.component.print_message("{}:Get todo id:{}".format(threading.current_thread().name, msg))
            pass

        pass

    @classmethod
    def add_slot_args(cls):
        """
        a watcher for service
        """
        return [
            (('--small',), dict(action='store_true', help='set list from 0 to 10'))
        ]

    pass
