class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        print(
            f"HTMLNode - Tag: {self.tag} - Value: {self.value} - Children: {self.children} - Props: {self.props}"
        )

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is not None and bool(self.props):
            return " " + " ".join(
                [f'{key}="{value}"' for key, value in self.props.items()]
            )
        else:
            return ""


class LeafNode(HTMLNode):

    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("value is required")
        elif self.tag is None:
            return self.value
        else:
            attrs = self.props_to_html()
            open_tag = f"<{self.tag}{attrs}>"
            close_tag = f"</{self.tag}>"
            return f"{open_tag}{self.value}{close_tag}"


class ParentNode(HTMLNode):

    def __init__(self, tag=None, children=None, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        # print(self)
        if self.tag is None:
            raise ValueError("tag is required")
        elif self.children is None:
            raise ValueError("children is required")
        else:

            def to_html_rec(children, acc):
                acc += children[0].to_html()
                rest = children[1:]
                if len(rest) == 0:
                    return acc
                else:
                    return to_html_rec(rest, acc)

            attrs = self.props_to_html()
            open_tag = f"<{self.tag}{attrs}>"
            close_tag = f"</{self.tag}>"
            inner_html = ""
            if self.children is None:
                inner_html = f"{open_tag}{close_tag}"
            else:
                inner_html = to_html_rec(self.children, inner_html)
            return f"{open_tag}{inner_html}{close_tag}"

