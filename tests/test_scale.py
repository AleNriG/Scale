from src import scale


def test_find_scale_bar(qtbot):
    image = scale.Image("./test.bmp")
    assert image.scale_bar == 183
