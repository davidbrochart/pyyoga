from pyyoga import Node, Align, FlexDirection, Direction, Config

def test_dirtied():
    root = Node()
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100

    root.calculate_layout(None, None, Direction.LTR)

    dirtied = [0]
    def on_dirtied(node):
        dirtied[0] += 1
    
    root.set_dirtied_func(on_dirtied)

    # only nodes with a measure function can be marked dirty
    root.set_measure_func(lambda w, wm, h, hm: (0, 0))

    assert dirtied[0] == 0

    # dirtied func MUST be called in case of explicit dirtying.
    root.mark_dirty()
    assert dirtied[0] == 1

    # dirtied func MUST be called ONCE.
    root.mark_dirty()
    assert dirtied[0] == 1

def test_dirtied_propagation():
    root = Node()
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100

    root_child0 = Node()
    root_child0.align_items = Align.FlexStart
    root_child0.width = 50
    root_child0.height = 20
    root_child0.set_measure_func(lambda w, wm, h, hm: (0, 0))
    root.add_child(root_child0, 0)

    root_child1 = Node()
    root_child1.align_items = Align.FlexStart
    root_child1.width = 50
    root_child1.height = 20
    root.add_child(root_child1, 0)

    root.calculate_layout(None, None, Direction.LTR)

    dirtied = [0]
    def on_dirtied(node):
        dirtied[0] += 1
    
    root.set_dirtied_func(on_dirtied)

    assert dirtied[0] == 0

    # dirtied func MUST be called for the first time.
    root_child0.mark_dirty()
    assert dirtied[0] == 1

    # dirtied func must NOT be called for the second time.
    root_child0.mark_dirty()
    assert dirtied[0] == 1

def test_dirtied_hierarchy():
    root = Node()
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100

    root_child0 = Node()
    root_child0.align_items = Align.FlexStart
    root_child0.width = 50
    root_child0.height = 20
    root_child0.set_measure_func(lambda w, wm, h, hm: (0, 0))
    root.add_child(root_child0, 0)

    root_child1 = Node()
    root_child1.align_items = Align.FlexStart
    root_child1.width = 50
    root_child1.height = 20
    root_child0.set_measure_func(lambda w, wm, h, hm: (0, 0))
    root.add_child(root_child1, 0)

    root.calculate_layout(None, None, Direction.LTR)

    dirtied = [0]
    def on_dirtied(node):
        dirtied[0] += 1
    
    root_child0.set_dirtied_func(on_dirtied)

    assert dirtied[0] == 0

    # dirtied func must NOT be called for descendants.
    # NOTE: nodes without a measure function cannot be marked dirty manually,
    # but nodes with a measure function can not have children.
    # Update the width to dirty the node instead.
    root.width = 110
    assert dirtied[0] == 0

    # dirtied func MUST be called in case of explicit dirtying.
    root_child0.mark_dirty()
    assert dirtied[0] == 1

def test_dirtied_reset():
    root = Node()
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100
    root.set_measure_func(lambda w, wm, h, hm: (0, 0))

    root.calculate_layout(None, None, Direction.LTR)

    dirtied = [0]
    def on_dirtied(node):
        dirtied[0] += 1
    
    root.set_dirtied_func(on_dirtied)

    assert dirtied[0] == 0

    # dirtied func MUST be called in case of explicit dirtying.
    root.mark_dirty()
    assert dirtied[0] == 1

    # recalculate so the root is no longer dirty
    root.calculate_layout(None, None, Direction.LTR)

    root.reset()
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100
    root.set_measure_func(lambda w, wm, h, hm: (0, 0))

    root.mark_dirty()

    # dirtied func must NOT be called after reset.
    root.mark_dirty()
    assert dirtied[0] == 1
