import Todo
import TodoFile
import TodoList

def load_file(p_filename):
    """
    Loads a todo file from the given filename and returns a list of todos.
    """
    todolist = load_file_to_raw_list(p_filename)
    return [Todo.Todo(src) for src in todolist]

def load_file_to_raw_list(p_filename):
    """
    Loads a todo file from the given filename and returns a list of todo
    strings (unparsed).
    """
    todofile = TodoFile.TodoFile(p_filename)
    return todofile.read()

def load_file_to_todolist(p_filename):
    """
    Loads a todo file to a TodoList instance.
    """
    todolist = load_file_to_raw_list(p_filename)
    return TodoList.TodoList(todolist)

def todolist_to_string(p_list):
    """ Converts a todo list to a single string. """
    return '\n'.join([str(t) for t in p_list])
