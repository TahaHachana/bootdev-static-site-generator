from enum import Enum


class TextType(Enum):
    text_type_text = 1
    text_type_bold = 2
    text_type_italic = 3
    text_type_code = 4
    text_type_link = 5
    text_type_image = 6


def text_representation(text_type: TextType):
    # Mapping of enum members to their text representations
    representations = {
        TextType.text_type_text: "Plain Text",
        TextType.text_type_bold: "Bold Text",
        TextType.text_type_italic: "Italic Text",
        TextType.text_type_code: "Code Snippet",
        TextType.text_type_link: "Hyperlink",
        TextType.text_type_image: "Image",
    }

    return representations[text_type]


class TextNode:
    def __init__(self, text, text_type: TextType, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self):
        text_type_str = text_representation(self.text_type)
        return f"TextNode({self.text}, {text_type_str}, {self.url})"
