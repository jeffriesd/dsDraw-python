from command import DSCommand
from . import command_factory
from command import ModelCommand


class SequenceFactory(object):
    
    def create_sequence(self, receiver, name, *seq_args):
        if not seq_args:
            return CommandSequence(receiver, name)

        keyword, args = seq_args[0], seq_args[1:]
        if keyword == "for":
            return ForSequence(receiver, name, *args)
        elif keyword == "while":
            return WhileSequence(receiver, name, *args)

        raise Exception("Unknown sequence keyword: '%s'" % keyword)

class CommandSequence(DSCommand):

    def __init__(self, receiver, name):
        """
        CommandSequence class to handle building of sequence,
        sequential execution.

        self.sequence is a list of command text.
        parsing is saved for run-time of command sequence
        because assignment statements may need to be executed
        before later commands can be parsed

        Future features: variable time for each task

        :param receiver: receiver of this command object (control object)
        :param name: name to be stored in control.my_variables
        :param cmd_args: other arguments to sequence (for, while)
        """
        super().__init__()
        self.receiver = receiver
        self.name = name
        self.sequence = []

    def get_command_factory(self):
        return command_factory.SequenceCommandFactory(self)

    def add_command(self, command_obj):
        self.sequence.append(command_obj)

    def execute(self):
        """Execute each command in sequence, waiting for the previous
            task to finish before moving on"""

        for command_text in self.sequence:
            command = self.receiver.parse_command(command_text)
            command.execute()

            if command.should_redraw:
                # if command receiver is control or sequence
                if not isinstance(command, ModelCommand):
                    self.receiver.display()
                else:
                    control = self.receiver
                    model_name = command.receiver.name
                    render_obj = control.my_renders[model_name]
                    render_obj.display()

    def undo(self):
        pass


class ForSequence(CommandSequence):

    def __init__(self, receiver, name, v_name, iterable):
        """
        CommandSequence with for loop structure. Assigns variable
        name to values of some iterable. Command takes the form:
            seq_for abc i g:nodes
        name - abc
        variable name - i
        iterable - g:nodes (g is some reference to datastructure)
        :param receiver: receiver of this command - control object
        :param name: name to be assigned to the sequence in control.my_variables
        :param v_name: name to be temporarily assigned to each item in iterable
        :param iter_string: name of some data structure and iterable attribute
        """
        DSCommand.__init__(self)
        self.receiver = receiver
        self.name = name
        self.sequence = []
        self.v_name = v_name

        # get reference to iterable structure
        self.iterable = iterable

        # assign name in control object
        self.receiver.my_variables[name] = self

    def execute(self):
        """
        Attempt to iterate through iterable object and
        perform sequence of commands, assigning the
        iterated value to control.my_variables[self.v_name]
         """
        try:
            # generate list before iteration in case contents
            # change (e.g. adding nodes to graph while iterating through g:nodes)
            iter = list(self.iterable)
            for i in iter:
                # assign i to variable name
                self.receiver.my_variables[self.v_name] = i

                # execute sequence of commands
                super().execute()

            # delete iterated variable reference
            del self.receiver.my_variables[self.v_name]

        except TypeError as e:
            print(e)
            raise Exception("Error completing sequence: %s is not iterable" % self.iterable)


class WhileSequence(CommandSequence):

    def __init__(self, receiver, name, *condition_args):
        DSCommand.__init__(self)
        self.receiver = receiver
        self.name = name
        self.sequence = []
        self.condition = condition_args


    def execute(self):
        """
        Execute sequence as long as condition
        evaluates True
        """
        # while self.condition():
        #     super().execute()

    def undo(self):
        pass


