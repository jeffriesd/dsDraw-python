from command import DSCommand

class SequenceExecuteCommand(DSCommand):

    def __init__(self, receiver):
        """
        Class to handle execution of CommandSequence
        from the console.
        :param receiver:
        """
        super().__init__()
        self.receiver = receiver

    def execute(self):
        self.receiver.execute()

    def undo(self):
        self.receiver.undo()