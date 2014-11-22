# Topydo - A todo.txt client written in Python.
# Copyright (C) 2014 Bram Schoenmakers <me@bramschoenmakers.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from topydo.lib.Config import config
from topydo.lib.Sorter import Sorter

from TestFacilities import load_file, todolist_to_string, load_file_to_todolist

class SorterTest(unittest.TestCase):
    def sort_file(self,p_filename, p_filename_ref, p_sorter):
        """
        Sorts a file and compares it with a reference result.
        Also check that the sort algorithm hasn't touched the original data.
        """
        todos = load_file(p_filename)
        text_before = todolist_to_string(todos)
        todos_sorted = todolist_to_string(p_sorter.sort(todos))
        todos_ref = todolist_to_string(load_file(p_filename_ref))

        self.assertEquals(todos_sorted, todos_ref)
        self.assertEquals(todolist_to_string(todos), text_before)

    def test_sort1(self):
        """ Alphabetically sorted """
        sorter = Sorter('text')
        self.sort_file('data/SorterTest1.txt', 'data/SorterTest1-result.txt', sorter)

    def test_sort2a(self):
        """
        Ascendingly sorted by priority. Also checks stableness of the sort.
        """
        sorter = Sorter('prio')
        self.sort_file('data/SorterTest2.txt', 'data/SorterTest2-result.txt', sorter)

    def test_sort2b(self):
        """
        Ascendingly sorted by priority. Also checks stableness of the sort.
        """
        sorter = Sorter('asc:prio')
        self.sort_file('data/SorterTest2.txt', 'data/SorterTest2-result.txt', sorter)

    def test_sort3(self):
        """
        Descendingly sorted by priority. Also checks stableness of the
        sort.
        """
        sorter = Sorter('desc:prio')
        self.sort_file('data/SorterTest3.txt', 'data/SorterTest3-result.txt', sorter)

    def test_sort4(self):
        """ Ascendingly sorted by due date """
        sorter = Sorter(config().tag_due())
        self.sort_file('data/SorterTest4.txt', 'data/SorterTest4-result.txt', sorter)

    def test_sort5(self):
        """ Descendingly sorted by due date """
        sorter = Sorter('desc:due')
        self.sort_file('data/SorterTest5.txt', 'data/SorterTest5-result.txt', sorter)

    def test_sort6(self):
        """ Ascendingly sorted by creation date """
        sorter = Sorter('creation')
        self.sort_file('data/SorterTest6.txt', 'data/SorterTest6-result.txt', sorter)

    def test_sort7(self):
        """ Ascendingly sorted by completion date. """
        sorter = Sorter('completion')
        self.sort_file('data/SorterTest7.txt', 'data/SorterTest7-result.txt', sorter)

    def test_sort8(self):
        """ Descendingly sorted by importance """
        sorter = Sorter('desc:importance')
        self.sort_file('data/SorterTest8.txt', 'data/SorterTest8-result.txt', sorter)

    def test_sort9(self):
        """
        Sort on multiple levels: first descending importance, then
        ascending priority.
        """
        sorter = Sorter('desc:importance,priority')
        self.sort_file('data/SorterTest9.txt', 'data/SorterTest9-result.txt', sorter)

    def test_sort10(self):
        """ Deal with garbage input. """
        sorter = Sorter('')
        self.sort_file('data/SorterTest9.txt', 'data/SorterTest9.txt', sorter)

    def test_sort11(self):
        """ Deal with garbage input. """
        sorter = Sorter('fnord')
        self.sort_file('data/SorterTest9.txt', 'data/SorterTest9.txt', sorter)

    def test_sort12(self):
        """ Deal with garbage input. """
        sorter = Sorter('desc:importance,,priority')
        self.sort_file('data/SorterTest9.txt', 'data/SorterTest9-result.txt', sorter)

    def test_sort13(self):
        """
        Descendingly sorted by average importance.

        Reusing input and output for normal importance test, since without
        dependencies the average importance should be equal.
        """
        sorter = Sorter('desc:importance-avg')
        self.sort_file('data/SorterTest9.txt', 'data/SorterTest9-result.txt', sorter)

    def test_sort14(self):
        sorter = Sorter('desc:importance-average')

        todolist = load_file_to_todolist('data/SorterTest10.txt')
        view = todolist.view(sorter, [])
        result = load_file('data/SorterTest10-result.txt')

        self.assertEquals(str(view), todolist_to_string(result))

    def test_sort15(self):
        """
        Test that own importance is used when average turns out to be
        lower.
        """
        sorter = Sorter('desc:importance-average')

        todolist = load_file_to_todolist('data/SorterTest11.txt')
        view = todolist.view(sorter, [])
        result = load_file('data/SorterTest11-result.txt')

        self.assertEquals(str(view), todolist_to_string(result))

    def test_sort16(self):
        """
        Check sort of low priority tasks (D or lower) with non-priority tasks.
        """
        sorter = Sorter('desc:importance,desc:prio')

        todolist = load_file_to_todolist('data/SorterTest12.txt')
        view = todolist.view(sorter, [])
        result = load_file('data/SorterTest12-result.txt')

        self.assertEquals(str(view), todolist_to_string(result))
