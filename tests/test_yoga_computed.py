from pyyoga import Node, Edge

def test_computed_border():
    root = Node()
    root.set_border(Edge.All, 10)
    root.calculate_layout()
    assert root.get_computed_border(Edge.Left) == 10
    assert root.get_computed_border(Edge.Top) == 10
    assert root.get_computed_border(Edge.Right) == 10
    assert root.get_computed_border(Edge.Bottom) == 10

def test_computed_margin():
    root = Node()
    root.set_margin(Edge.All, 10)
    root.calculate_layout()
    assert root.get_computed_margin(Edge.Left) == 10
    assert root.get_computed_margin(Edge.Top) == 10
    assert root.get_computed_margin(Edge.Right) == 10
    assert root.get_computed_margin(Edge.Bottom) == 10

def test_computed_padding():
    root = Node()
    root.set_padding(Edge.All, 10)
    root.calculate_layout()
    assert root.get_computed_padding(Edge.Left) == 10
    assert root.get_computed_padding(Edge.Top) == 10
    assert root.get_computed_padding(Edge.Right) == 10
    assert root.get_computed_padding(Edge.Bottom) == 10
