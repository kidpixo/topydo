"""
A list of todo items.
"""

import re

import Graph
from PrettyPrinter import pretty_print_list
import Todo
import View

class TodoList(object):
    """
    Provides operations for a todo list, such as adding items, removing them,
    etc.

    The list is usually a complete list found in the program's input (e.g. a
    todo.txt file), not an arbitrary set of todo items.
    """

    def __init__(self, p_todostrings):
        """
        Should be given a list of strings, each element a single todo string.
        The string will be parsed.
        """
        self._todos = []
        self._depgraph = Graph.DirectedGraph()

        for string in p_todostrings:
            self.add(string)

        self.dirty = False

    def todo(self, p_number):
        """
        The _todos list has the same order as in the backend store (usually
        a todo.txt file. The user refers to the first task as number 1, so use
        index 0, etc.
        """
        result = None
        try:
            result = self._todos[p_number - 1]
        except IndexError:
            result = None

        return result

    def todo_by_hash(self, p_hash):
        """
        Given the hash value of a todo, return the corresponding hash instance.
        """

        result = None
        for todo in self._todos:
            if hash(todo) == p_hash:
                result = todo
                break
        return result

    def todo_by_dep_id(self, p_dep_id):
        """
        Returns the todo that has the id tag set to the value p_dep_id.
        There is only one such task, the behavior is undefined when a tag has
        more than one id tag.
        """
        hits = [t for t in self._todos if t.tag_value('id') == p_dep_id]

        return hits[0] if len(hits) else None

    def _maintain_dep_graph(self, p_todo):
        """
        Makes sure that the dependency graph is consistent according to the
        given todo.
        """

        dep_id = p_todo.tag_value('id')
        # maintain dependency graph
        if dep_id:
            self._depgraph.add_node(hash(p_todo))

            # connect all tasks we have in memory so far that refer to this
            # task
            for dep in \
                [dep for dep in self._todos if dep.has_tag('p', dep_id)]:

                self._depgraph.add_edge(hash(p_todo), hash(dep), dep_id)

        for child in p_todo.tag_values('p'):
            parent = self.todo_by_dep_id(child)
            if parent:
                self._depgraph.add_edge(hash(parent), hash(p_todo), child)

    def add(self, p_src):
        """ Given a todo string, parse it and put it to the end of the list. """
        todo = None
        if re.search(r'\S', p_src):
            todo = Todo.Todo(p_src)
            self.add_todo(todo)

        return todo

    def add_todo(self, p_todo):
        """
        Add an Todo object to the list.

        Also maintains the dependency graph to track the dependencies between
        tasks.

        The node ids are the todo numbers.
        The edge ids are the numbers denoted by id: and p: tags.

        For example:

        (C) Parent task id:4
        (B) Child task p:4

        Then there will be an edge 1 --> 2 with ID 4.
        """
        self._todos.append(p_todo)

        self._maintain_dep_graph(p_todo)
        self._update_parent_cache()
        self.dirty = True

    def delete(self, p_number):
        """ Deletes a todo item from the list. """
        todo = self.todo(p_number)

        if todo:
            for child in self.children(p_number):
                self.remove_dependency(self.number(todo), self.number(child))

            for parent in self.parents(p_number):
                self.remove_dependency(self.number(parent), self.number(todo))

            del self._todos[p_number - 1]

            self.dirty = True

    def count(self):
        """ Returns the number of todos on this list. """
        return len(self._todos)

    def append(self, p_number, p_string):
        """
        Appends a text to the todo, specified by its number.
        The todo will be parsed again, such that tags and projects in de
        appended string are processed.
        """
        if len(p_string) > 0:
            todo = self.todo(p_number)

            if todo:
                new_text = todo.source() + ' ' + p_string
                todo.set_source_text(new_text)
                self.dirty = True

    def projects(self):
        """ Returns a set of all projects in this list. """
        result = set()
        for todo in self._todos:
            projects = todo.projects()
            result = result.union(projects)

        return result

    def contexts(self):
        """ Returns a set of all contexts in this list. """
        result = set()
        for todo in self._todos:
            contexts = todo.contexts()
            result = result.union(contexts)

        return result

    def view(self, p_sorter, p_filters):
        """
        Constructs a view of the todo list.

        A view is a sorted and filtered todo list, where the properties are
        defined by the end user. Todos is this list should not be modified,
        modifications should occur through this class.
        """
        return View.View(p_sorter, p_filters, self)

    def add_dependency(self, p_number1, p_number2):
        """ Adds a dependency from task 1 to task 2. """
        def find_next_id():
            """
            Find a new unused ID.
            Unused means that no task has it as an 'id' value or as a 'p'
            value.
            """

            new_id = 1
            while self._depgraph.has_edge_id('%d' % new_id):
                new_id += 1

            return '%d' % new_id

        from_todo = self.todo(p_number1)
        to_todo = self.todo(p_number2)
        if not self._depgraph.has_edge(hash(from_todo), hash(to_todo)):

            if not from_todo or not to_todo:
                return

            dep_id = None
            if from_todo.has_tag('id'):
                dep_id = from_todo.tag_value('id')
            else:
                dep_id = find_next_id()
                from_todo.set_tag('id', dep_id)

            to_todo.add_tag('p', dep_id)
            self._depgraph.add_edge(hash(from_todo), hash(to_todo), dep_id)
            self._update_parent_cache()
            self.dirty = True

    def remove_dependency(self, p_number1, p_number2):
        """ Removes a dependency between two todos. """
        from_todo = self.todo(p_number1)
        to_todo = self.todo(p_number2)

        if not from_todo or not to_todo:
            return

        dep_id = from_todo.tag_value('id')

        if dep_id:
            to_todo.remove_tag('p', dep_id)
            self._depgraph.remove_edge(hash(from_todo), hash(to_todo))
            self._update_parent_cache()

            if not self.children(p_number1, True):
                from_todo.remove_tag('id')

            self.dirty = True

    def parents(self, p_number, p_only_direct=False):
        """
        Returns a list of parent todos that (in)directly depend on the
        given todo.
        """
        todo = self.todo(p_number)
        parents = self._depgraph.incoming_neighbors(hash(todo), not p_only_direct)
        return [self.todo_by_hash(parent) for parent in parents]

    def children(self, p_number, p_only_direct=False):
        """
        Returns a list of child todos that the given todo (in)directly depends
        on.
        """
        todo = self.todo(p_number)
        children = \
            self._depgraph.outgoing_neighbors(hash(todo), not p_only_direct)
        return [self.todo_by_hash(child) for child in children]

    def clean_dependencies(self):
        """
        Cleans the dependency graph.

        This is achieved by performing a transitive reduction on the dependency
        graph and removing unused dependency ids from the graph (in that
        order).
        """
        def clean_by_tag(tag_name):
            """ Generic function to handle 'p' and 'id' tags. """
            for todo in [todo for todo in self._todos if todo.has_tag(tag_name)]:
                value = todo.tag_value(tag_name)
                if not self._depgraph.has_edge_id(value):
                    todo.remove_tag(tag_name, value)
                    self.dirty = True

        self._depgraph.transitively_reduce()
        clean_by_tag('p')
        clean_by_tag('id')

    def _update_parent_cache(self):
        """
        Sets the attribute to the list of parents, such that others may access
        it outside this todo list.
        This is used for calculating the average importance, that requires
        access to a todo's parents.
        """

        for todo in self._todos:
            todo.attributes['parents'] = self.parents(self.number(todo))

    def is_dirty(self):
        return self.dirty

    def todos(self):
        return self._todos

    def set_todo_completed(self, p_number):
        todo = self.todo(p_number)
        todo.set_completed()
        self.dirty = True

    def set_priority(self, p_number, p_priority):
        todo = self.todo(p_number)
        todo.set_priority(p_priority)
        self.dirty = True

    def number(self, p_todo):
        return self._todos.index(p_todo) + 1

    def pp_number(self):
        """
        A filter for the pretty printer to append the todo number to the
        printed todo.
        """
        return lambda p_todo_str, p_todo: "%3d %s" % (self.number(p_todo), p_todo_str)

    def __str__(self):
        return '\n'.join(pretty_print_list(self._todos))

