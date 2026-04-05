from pyyoga import Node, Align, FlexDirection, Direction, Config

def test_align_baseline_parent_using_child_in_column_as_reference():
    config = Config()
    root = Node(config)
    root.flex_direction = FlexDirection.Row
    root.width = 1000
    root.height = 1000
    root.align_items = Align.Baseline

    root_child0 = Node(config)
    root_child0.flex_direction = FlexDirection.Column
    root_child0.width = 500
    root_child0.height = 600
    root.add_child(root_child0, 0)

    root_child1 = Node(config)
    root_child1.flex_direction = FlexDirection.Column
    root_child1.width = 500
    root_child1.height = 800
    root.add_child(root_child1, 1)

    root_child1_child0 = Node(config)
    root_child1_child0.flex_direction = FlexDirection.Column
    root_child1_child0.width = 500
    root_child1_child0.height = 300
    root_child1.add_child(root_child1_child0, 0)

    root_child1_child1 = Node(config)
    root_child1_child1.flex_direction = FlexDirection.Column
    root_child1_child1.width = 500
    root_child1_child1.height = 400
    root_child1_child1.is_reference_baseline = True
    root_child1.add_child(root_child1_child1, 1)

    root.calculate_layout(None, None, Direction.LTR)

    assert root_child0.layout_left == 0
    assert root_child0.layout_top == 100

    assert root_child1.layout_left == 500
    assert root_child1.layout_top == 0

    assert root_child1_child0.layout_left == 0
    assert root_child1_child0.layout_top == 0

    assert root_child1_child1.layout_left == 0
    assert root_child1_child1.layout_top == 300

def test_align_baseline_parent_using_child_in_row_as_reference():
    config = Config()
    root = Node(config)
    root.flex_direction = FlexDirection.Row
    root.width = 1000
    root.height = 1000
    root.align_items = Align.Baseline

    root_child0 = Node(config)
    root_child0.flex_direction = FlexDirection.Column
    root_child0.width = 500
    root_child0.height = 600
    root.add_child(root_child0, 0)

    root_child1 = Node(config)
    root_child1.flex_direction = FlexDirection.Row
    root_child1.width = 500
    root_child1.height = 800
    root.add_child(root_child1, 1)

    root_child1_child0 = Node(config)
    root_child1_child0.flex_direction = FlexDirection.Column
    root_child1_child0.width = 500
    root_child1_child0.height = 500
    root_child1.add_child(root_child1_child0, 0)

    root_child1_child1 = Node(config)
    root_child1_child1.flex_direction = FlexDirection.Column
    root_child1_child1.width = 500
    root_child1_child1.height = 400
    root_child1_child1.is_reference_baseline = True
    root_child1.add_child(root_child1_child1, 1)

    root.calculate_layout(None, None, Direction.LTR)

    assert root_child0.layout_left == 0
    assert root_child0.layout_top == 0

    assert root_child1.layout_left == 500
    assert root_child1.layout_top == 200

    assert root_child1_child0.layout_left == 0
    assert root_child1_child0.layout_top == 0

    assert root_child1_child1.layout_left == 500
    assert root_child1_child1.layout_top == 0
