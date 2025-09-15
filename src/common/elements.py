from collections import defaultdict
from src.utils.text import clean_text
from unstructured.documents.elements import Element

class DocumentNode:
    def __init__(self, depth, path = "", element: Element = None, father: Element = None, prefix: str = ""):
        self.depth = depth
        self.father = father
        self.children = defaultdict(list)
        self.element = element
        self.prefix = prefix
        self.content = clean_text(element.text) if element else ""
        self.path = element.metadata.filename if element else path

    def set_father(self, father):
        if not self.check_father(father):
            return False
        depth, lev = self.depth
        # Get last elements since father is indicated beforehand
        lev = lev[-1] if isinstance(lev, list) else lev
        self.father = father
        father.children[depth].append(self)
        if lev == 0:
            lev = len(self.father.children[depth])
            self.depth = (depth, [lev])
        self.path = father.path + "/" + f"{self.prefix}{depth}.{lev}"
        return True

    def check_father(self, node):
        """
        Check if the element is a child of this node.
        """
        n_depth, n_lev = node.depth
        s_depth, s_lev = self.depth
        if n_depth > s_depth or n_depth < 0:
            return False
        elif (n_depth == s_depth) and (len(s_lev) - len(n_lev) == 1):
            for s_l, n_l in zip(s_lev[:-1], n_lev):
                if s_l != n_l:
                    return False
            if s_depth not in node.children.keys() and s_lev[-1] > 1:
                return False
            # Add tolerance for falsely partitioning
            elif s_lev[-1] > len(node.children[s_depth]) + 2:
                return False
            return True
        elif (n_depth < s_depth):
            if s_depth not in node.children.keys() and s_lev[-1] > 1:
                return False
            # Add tolerance for falsely partitioning
            elif s_lev[-1] > len(node.children[s_depth]) + 2:
                return False
            return True
        else:
            return False

    def __repr__(self):
        return f"DocumentNode(depth={self.depth}, path={self.path}, content={self.content[:30]})"

