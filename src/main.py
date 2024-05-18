from textnode import TextNode, TextType
from htmlnode import ParentNode, LeafNode
from typing import List
import re
from enum import Enum
import os
import glob
import shutil

HeadingPattern = r"^#{1,6}\s"
CodePattern = r"^```.+```$"
QuotePattern = r"^>"
UnorderedListPattern = r"^(\*|-)\s"
OrderedListPattern = r"^\d\.\s"
PublicDir = "./public"
StaticDir = "./static/**/*"
PublicDirStr = "/public"
StaticDirStr = "/static"


class BlockType(Enum):
    Paragraph = 1
    Heading = 2
    Code = 3
    Quote = 4
    UnorderedList = 5
    OrderedList = 6


def text_node_to_html_node(text_node: TextNode):
    text_type = text_node.text_type
    if text_type == TextType.text_type_text:
        return LeafNode(None, text_node.text)
    elif text_type == TextType.text_type_bold:
        return LeafNode("b", text_node.text)
    elif text_type == TextType.text_type_italic:
        return LeafNode("i", text_node.text)
    elif text_type == TextType.text_type_code:
        return LeafNode("code", text_node.text)
    elif text_type == TextType.text_type_link:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_type == TextType.text_type_image:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception("unknown text type")


def split_nodes_delimiter(old_nodes: List[TextNode], delimiter, text_type: TextType):
    rslt = []
    for old_node in old_nodes:
        if old_node.text_type == TextType.text_type_text:
            arr = old_node.text.split(delimiter, 2)
            if len(arr) == 1:
                rslt.append(old_node)
            else:
                rslt.append(TextNode(arr[0], TextType.text_type_text))
                rslt.append(TextNode(arr[1], text_type))
                text_node = TextNode(arr[2], TextType.text_type_text)
                rslt.extend(split_nodes_delimiter([text_node], delimiter, text_type))
        else:
            rslt.append(old_node)
    return rslt


def extract_markdown_images(text):
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"\[(.*?)\]\((.*?)\)", text)
    return matches


def parse_images_links(text, images_links, formatter, text_type, acc):
    # print(f"parsing {text}")
    img_link = images_links[0]
    arr = text.split(formatter(img_link), 1)
    if arr[0] != "":
        txt_node = TextNode(arr[0], TextType.text_type_text)
        acc.append(txt_node)
    img_link_node = TextNode(img_link[0], text_type, img_link[1])
    acc.append(img_link_node)
    if not images_links[1:]:
        if arr[1] != "":
            txt_node = TextNode(arr[1], TextType.text_type_text)
            acc.append(txt_node)
        return acc
    else:
        return parse_images_links(arr[1], images_links[1:], formatter, text_type, acc)


def split_nodes(old_nodes: List[TextNode], extractor, formatter, text_type):
    rslt = []
    for node in old_nodes:
        original_text = node.text
        images_links = extractor(original_text)
        if not images_links:
            rslt.append(node)
        else:
            rslt.extend(
                parse_images_links(
                    original_text, images_links, formatter, text_type, []
                )
            )
    return rslt


def img_formatter(img):
    return f"![{img[0]}]({img[1]})"


def link_formatter(link):
    return f"[{link[0]}]({link[1]})"


def split_nodes_image(old_nodes: List[TextNode]):
    return split_nodes(
        old_nodes, extract_markdown_images, img_formatter, TextType.text_type_image
    )


def split_nodes_link(old_nodes: List[TextNode]):
    return split_nodes(
        old_nodes, extract_markdown_links, link_formatter, TextType.text_type_link
    )


def text_to_textnodes(text):
    text_node = TextNode(text, TextType.text_type_text)
    rslt = split_nodes_image([text_node])
    rslt = split_nodes_link(rslt)
    rslt = split_nodes_delimiter(rslt, "**", TextType.text_type_bold)
    rslt = split_nodes_delimiter(rslt, "*", TextType.text_type_italic)
    rslt = split_nodes_delimiter(rslt, "`", TextType.text_type_code)
    return rslt


def markdown_to_blocks(markdown):
    blocks = re.split(r"\n\s*\n", markdown, flags=re.MULTILINE)
    blocks = [block.strip() for block in blocks]
    return list(filter(lambda str: str != "", blocks))


def is_heading(block):
    return re.match(HeadingPattern, block)


def is_code(block):
    return re.match(CodePattern, block, re.DOTALL)


def all_lines_match_pattern(block, pattern):
    lines = block.split("\n")
    return all(re.match(pattern, line) for line in lines)


def is_quote(block):
    return all_lines_match_pattern(block, QuotePattern)


def is_unordered_list(block):
    return all_lines_match_pattern(block, UnorderedListPattern)


def is_ordered_list(block):
    return all_lines_match_pattern(block, OrderedListPattern)


def block_to_block_type(block: str) -> BlockType:
    if is_heading(block):
        return BlockType.Heading
    elif is_code(block):
        return BlockType.Code
    elif is_quote(block):
        return BlockType.Quote
    elif is_unordered_list(block):
        return BlockType.UnorderedList
    elif is_ordered_list(block):
        return BlockType.OrderedList
    else:
        return BlockType.Paragraph


def render_paragraph(block):
    children = text_to_textnodes(block)
    return ParentNode("p", [text_node_to_html_node(child) for child in children])


def render_quote(block):
    parent = ParentNode("blockquote")
    children = []
    lines = block.split("\n")
    for line in lines:
        inner_text = re.sub(r"^>\s*", "", line)
        children.append(LeafNode("p", inner_text))
    parent.children = children
    return parent

def render_list(block, parent_tag):
    parent = ParentNode(parent_tag)
    children = []
    for line in block.split("\n"):
        inner_text = re.sub(r"^(\*|-|\d\.)\s", "", line)
        li_children = [text_node_to_html_node(child) for child in text_to_textnodes(inner_text)]
        children.append(ParentNode("li", li_children))
    parent.children = children
    return parent


def render_code(block):
    inner_text = block.replace("```", "").strip()
    parent = ParentNode("pre")
    child = LeafNode("code", inner_text)
    parent.children = [child]
    return parent


def count_leading_characters(s, char):
    count = 0
    for c in s:
        if c == char:
            count += 1
        else:
            break
    return count


def render_heading(block):
    level = count_leading_characters(block, "#")
    inner_text = re.sub(r"^#+\s*", "", block)
    children = [text_node_to_html_node(child) for child in text_to_textnodes(inner_text)]
    return ParentNode(f"h{level}", children)


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent = ParentNode("div")
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.Quote:
            children.append(render_quote(block))
        elif block_type == BlockType.UnorderedList:
            children.append(render_list(block, "ul"))
        elif block_type == BlockType.OrderedList:
            children.append(render_list(block, "ol"))
        elif block_type == BlockType.Code:
            children.append(render_code(block))
        elif block_type == BlockType.Heading:
            children.append(render_heading(block))
        else:
            children.append(render_paragraph(block))
    parent.children = children
    return parent


def copy_dir(source_dir, dest_dir, source_dir_str, dest_dir_str):
    shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)

    source_files = glob.glob(source_dir, recursive=True)
    for source in source_files:
        if os.path.isfile(source):
            directory, file_name = os.path.split(source)

            destination_directory = directory.replace(source_dir_str, dest_dir_str, 1)
            os.makedirs(destination_directory, exist_ok=True)

            destination_file = os.path.join(destination_directory, file_name)
            shutil.copy(source, destination_file)


def extract_title(markdown):
    return re.match(r"#\s([^\n]+)", markdown).group(1)


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = None
    template = None
    with open(from_path, "r") as file:
        markdown = file.read()
    with open(template_path, "r") as file:
        template = file.read()
    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    directory, file_name = os.path.split(dest_path)
    os.makedirs(directory, exist_ok=True)
    with open(dest_path, "w") as file:
        file.write(template)

def generate_pages(dir_path_content, template_path, dest_dir_path):
    source_files = glob.glob(dir_path_content + "/**/*", recursive=True)
    print(source_files)
    for source in source_files:
        if os.path.isfile(source):
            relative_path = os.path.relpath(source, dir_path_content)
            destination_path = os.path.join(dest_dir_path, relative_path)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            destination_file = os.path.join(destination_path.replace(".md", ".html"))
            print(f"writing {destination_file}")
            generate_page(source, template_path, destination_file)


def main():
    copy_dir(StaticDir, PublicDir, StaticDirStr, PublicDirStr)
    generate_pages("./content", "template.html", "./public")


if __name__ == "__main__":
    main()
