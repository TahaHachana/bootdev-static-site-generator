import unittest

from textnode import (
    TextNode,
    TextType,
)

from main import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

    def test_url_is_none(self):
        node = TextNode("This is a text node", "bold", None)
        node2 = TextNode("This is a text node", "bold", None)
        self.assertEqual(node, node2)

    def test_text_type_noteq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "italic")
        self.assertNotEqual(node, node2)

    def test_split_nodes_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.text_type_text)
        expected = [
            TextNode("This is text with a ", TextType.text_type_text),
            TextNode("bolded", TextType.text_type_bold),
            TextNode(" word", TextType.text_type_text),
        ]
        actual = split_nodes_delimiter([node], "**", TextType.text_type_bold)
        self.assertEqual(expected, actual)

    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)"
        expected = [
            (
                "image",
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            (
                "another",
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png",
            ),
        ]
        actual = extract_markdown_images(text)
        self.assertEqual(expected, actual)

    def test_extract_markdown_links(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        expected = [
            ("link", "https://www.example.com"),
            ("another", "https://www.example.com/another"),
        ]
        actual = extract_markdown_links(text)
        self.assertEqual(expected, actual)

    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and another ![second image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png)",
            TextType.text_type_text,
        )
        expected = [
            TextNode("This is text with an ", TextType.text_type_text),
            TextNode(
                "image",
                TextType.text_type_image,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and another ", TextType.text_type_text),
            TextNode(
                "second image",
                TextType.text_type_image,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png",
            ),
        ]
        actual = split_nodes_image([node])
        self.assertEqual(expected, actual)

    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a [link](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and another [link](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png)",
            TextType.text_type_text,
        )
        expected = [
            TextNode("This is text with a ", TextType.text_type_text),
            TextNode(
                "link",
                TextType.text_type_link,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and another ", TextType.text_type_text),
            TextNode(
                "link",
                TextType.text_type_link,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png",
            ),
        ]
        actual = split_nodes_link([node])
        self.assertEqual(expected, actual)

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and a [link](https://boot.dev)"
        expected = [
            TextNode("This is ", TextType.text_type_text),
            TextNode("text", TextType.text_type_bold),
            TextNode(" with an ", TextType.text_type_text),
            TextNode("italic", TextType.text_type_italic),
            TextNode(" word and a ", TextType.text_type_text),
            TextNode("code block", TextType.text_type_code),
            TextNode(" and an ", TextType.text_type_text),
            TextNode(
                "image",
                TextType.text_type_image,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and a ", TextType.text_type_text),
            TextNode("link", TextType.text_type_link, "https://boot.dev"),
        ]
        actual = text_to_textnodes(text)
        self.assertEqual(expected, actual)

    def test_markdown_to_blocks(self):
        text = """This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items"""
        expected = ['This is **bolded** paragraph', 'This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line', '* This is a list\n* with items']
        actual = markdown_to_blocks(text)
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
