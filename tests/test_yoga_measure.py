from pyyoga import Node, Direction, FlexDirection, Align

def test_dont_measure_single_grow_shrink_child():
    root = Node()
    root.width = 100
    root.height = 100

    measure_count = [0]
    def measure(w, wm, h, hm):
        measure_count[0] += 1
        return (100, 100)

    root_child0 = Node()
    root_child0.set_measure_func(measure)
    root_child0.flex_grow = 1
    root_child0.flex_shrink = 1
    root.add_child(root_child0, 0)
    root.calculate_layout(None, None, Direction.LTR)

    assert measure_count[0] == 0

def test_dont_fail_with_incomplete_measure_dimensions():
    root = Node()
    root.width = 100
    root.height = 100

    count1 = [0]
    def height_only(w, wm, h, hm):
        count1[0] += 1
        return {"height": 10}

    count2 = [0]
    def width_only(w, wm, h, hm):
        count2[0] += 1
        return {"width": 10}

    count3 = [0]
    def empty_callback(w, wm, h, hm):
        count3[0] += 1
        return {}

    node1 = Node()
    node2 = Node()
    node3 = Node()

    root.add_child(node1)
    root.add_child(node2)
    root.add_child(node3)

    node1.set_measure_func(height_only)
    node2.set_measure_func(width_only)
    node3.set_measure_func(empty_callback)

    root.calculate_layout(None, None, Direction.LTR)

    assert count1[0] == 1
    assert count2[0] == 1
    assert count3[0] == 1

    assert node1.layout_width == 100
    assert node1.layout_height == 10

    assert node2.layout_width == 100
    assert node2.layout_height == 0

    assert node3.layout_width == 100
    assert node3.layout_height == 0

def test_measure_once_single_flexible_child():
    root = Node()
    root.flex_direction = FlexDirection.Row
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100

    count = [0]
    def measure(width, width_mode, height, height_mode):
        count[0] += 1
        # Match getMeasureCounterMax logic
        # 0: Undefined, 1: Exactly, 2: AtMost
        measured_width = 10 if width_mode == 0 else width
        measured_height = 10 if height_mode == 0 else height
        return (measured_width, measured_height)

    root_child0 = Node()
    root_child0.set_measure_func(measure)
    root_child0.flex_grow = 1
    root.add_child(root_child0, 0)

    root.calculate_layout(None, None, Direction.LTR)

    assert count[0] == 1
