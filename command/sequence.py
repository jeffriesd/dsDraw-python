

class CommandSequence:

    def __init__(self, control):
        """
        CommandSequence class to handle building of sequence,
        sequential execution, and printing of current sequence for user.

        Future features: variable time for each task,

        :param control: reference to control object to handle redrawing
                        and printing of sequence
        """
        self.control = control
        self.sequence = []

    def add_command(self, command_obj):
        self.sequence.append(command_obj)

    def execute_sequence(self):
        """Execute each command in sequence, waiting for the previous
            task to finish before moving on"""

        for command in self.sequence:
            command.execute()

            if command.should_redraw:
                self.control.display()

    def print_sequence(self):
        pass
