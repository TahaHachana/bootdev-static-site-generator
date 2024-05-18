import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        expected = ' href="https://www.google.com" target="_blank"'
        actual = node.props_to_html()
        self.assertEqual(expected, actual)

    def test_leaf_tag_none(self):
        leaf = LeafNode(None, "value only", None)
        expected = "value only"
        actual = leaf.to_html()
        self.assertEqual(expected, actual)

    def test_leaf_p(self):
        leaf = LeafNode("p", "This is a paragraph of text.", None)
        expected = "<p>This is a paragraph of text.</p>"
        actual = leaf.to_html()
        self.assertEqual(expected, actual)

    def test_leaf_a(self):
        leaf = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        expected = '<a href="https://www.google.com">Click me!</a>'
        actual = leaf.to_html()
        self.assertEqual(expected, actual)

    def test_parent_to_html(self):
        parent = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
            None,
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        actual = parent.to_html()
        self.assertEqual(expected, actual)

    def test_parent_to_html_nested(self):
        parent = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
                ParentNode(
                    "p",
                    [
                        LeafNode("b", "Bold text"),
                        LeafNode(None, "Normal text"),
                        LeafNode("i", "italic text"),
                        LeafNode(None, "Normal text"),
                    ],
                    None,
                ),
            ],
            None,
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p></p>"
        actual = parent.to_html()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
