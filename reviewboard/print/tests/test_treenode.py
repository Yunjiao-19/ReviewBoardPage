from reviewboard.testing import TestCase
from reviewboard.reviews.treenode import *

class PrintViewTests(TestCase):
    """Tests for reviewboard.reviews:TreeNode."""

    def _test_tree_node(self, node, child_list):
        """Helper function for testing a single node"""
        num_children = len(child_list)
        self.assertEqual(len(node.children), num_children)
        for child in child_list:
            self.assertTrue(child in node.children_names)

    def testing_file_tree_structure(self):
        """Testing tree file structure is generated properly"""
        files=[
            "c++/utils.cc",
            "c++/scrambler.cc",
            "python/scrambler.py",
            "python/utils/utils.py",
            "Makefile"
        ]
        file_tree = generate_tree_structure(files)

        # Head node tests
        self.assertEqual(file_tree.name, "root")
        children_names = ["c++", "python", "Makefile"]
        self._test_tree_node(file_tree, children_names)

        # Traverse to python child node
        node = file_tree.get_child("python")
        children_names = ["scrambler.py", "utils"]
        self._test_tree_node(node, children_names)

        node = node.get_child("scrambler.py")
        children_names = []
        self._test_tree_node(node, children_names)

        html_out = generate_tree_html(file_tree, False, ["c++/scrambler.cc","python/utils/utils.py"])
        self.assertEqual(html_out,'<ul><li><label>c++</label><ul><li><label><input id="c++/utils.cc" name="c++/utils.cc" type="checkbox" />utils.cc</label></li></ul><ul><li><label><input id="c++/scrambler.cc" name="c++/scrambler.cc" type="checkbox" value="yes" checked />scrambler.cc</label></li></ul></li></ul><ul><li><label>python</label><ul><li><label><input id="python/scrambler.py" name="python/scrambler.py" type="checkbox" />scrambler.py</label></li></ul><ul><li><label>utils</label><ul><li><label><input id="python/utils/utils.py" name="python/utils/utils.py" type="checkbox" value="yes" checked />utils.py</label></li></ul></li></ul></li></ul><ul><li><label><input id="Makefile" name="Makefile" type="checkbox" />Makefile</label></li></ul>')
        
        html_out = generate_tree_html(file_tree, True, ["c++/scrambler.cc","python/utils/utils.py"])
        self.assertEqual(html_out,'<ul><li><label>c++</label><ul><li><label><input id="c++/utils.cc" name="c++/utils.cc" type="checkbox" value="yes" checked />utils.cc</label></li></ul><ul><li><label><input id="c++/scrambler.cc" name="c++/scrambler.cc" type="checkbox" value="yes" checked />scrambler.cc</label></li></ul></li></ul><ul><li><label>python</label><ul><li><label><input id="python/scrambler.py" name="python/scrambler.py" type="checkbox" value="yes" checked />scrambler.py</label></li></ul><ul><li><label>utils</label><ul><li><label><input id="python/utils/utils.py" name="python/utils/utils.py" type="checkbox" value="yes" checked />utils.py</label></li></ul></li></ul></li></ul><ul><li><label><input id="Makefile" name="Makefile" type="checkbox" value="yes" checked />Makefile</label></li></ul>')