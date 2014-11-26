from tests import BaseTestCase


class TestRectFrame(BaseTestCase):

    """ Test of rectangle frame """

    # Constructor params
    CORNER = (10, 20)  # Corner coordinates
    SIZES = (350, 250)  # Sizes (WIDTH x HEIGHT)
    WALL_WIDTH = 25
    # Hatching / filling params
    ANGLE = 30
    DISTANCE = 5
    WIDTH = 2
    COLOR = "black"

    @classmethod
    def setUpClass(cls):
        from planner.frame import RectFrame
        cls.RectFrame = RectFrame

    def setUp(self):
        self.rect_frame = self.RectFrame(self.CORNER[0], self.CORNER[1], self.SIZES[0], self.SIZES[1], self.WALL_WIDTH)

    def test_draw(self):
        """ Test frame drawing. Should create correct SVG objects. """
        svg_objects = self.rect_frame._draw()
        self.assertLength(svg_objects, 2)
        outer, inner = svg_objects
        from svgwrite import shapes, mm
        self.assertIsInstance(outer, shapes.Rect)
        self.assertIsInstance(inner, shapes.Rect)
        # Check sizes and coordinates
        self.assertAttrib(outer, 'x', self.CORNER[0] * mm)
        self.assertAttrib(outer, 'y', self.CORNER[1] * mm)
        self.assertAttrib(outer, 'width', self.SIZES[0] * mm)
        self.assertAttrib(outer, 'height', self.SIZES[1] * mm)
        self.assertAttrib(inner, 'x', (self.CORNER[0] + self.WALL_WIDTH) * mm)
        self.assertAttrib(inner, 'y', (self.CORNER[1] + self.WALL_WIDTH) * mm)
        self.assertAttrib(inner, 'width', (self.SIZES[0] - 2 * self.WALL_WIDTH) * mm)
        self.assertAttrib(inner, 'height', (self.SIZES[1] - 2 * self.WALL_WIDTH) * mm)

    def test_additional_attribs(self):
        """
        Should accept additional attributes for outer rectangle
        """
        attribs = {'opacity': 0.5, 'fill': "#55FF66"}
        rect_frame = self.RectFrame(
            self.CORNER[0], self.CORNER[1], self.SIZES[0], self.SIZES[1], self.WALL_WIDTH, **attribs)
        svg_objects = rect_frame._draw()
        outer_rect = svg_objects[0]
        for attr, value in attribs.items():
            self.assertAttrib(outer_rect, attr, value)

    def test_hatching(self):
        """
        Test that hatching appends to frame
        """
        self.rect_frame.add_hatching(self.ANGLE, self.DISTANCE, self.WIDTH, self.COLOR)
        svg_objects = self.rect_frame._draw()
        self.assertEqual(self.rect_frame.hatch, svg_objects[0])
        self.assertStyle(svg_objects[1], 'fill', 'url(#{})'.format(self.rect_frame._hatching_id))

    def test_filling(self):
        """
        Test that filling appends to frame
        """
        self.rect_frame.add_filling(self.COLOR)
        svg_objects = self.rect_frame._draw()
        self.assertAttrib(svg_objects[0], 'fill', self.COLOR)

    def test_add_aperture_coordinates_validation(self):
        """
        Test aperture coordinates validation
        """
        with self.assertRaisesRegex(ValueError, "not located on the wall border"):
            self.rect_frame.add_aperture(0, 0, 50)

    def test_add_aperture_with_correct_coordinates(self):
        """
        Test apperture with correct coordinates
        """
        try:
            self.rect_frame.add_aperture(10, 50, 50)  # left
            self.rect_frame.add_aperture(55, 20, 50)  # top
            self.rect_frame.add_aperture(335, 60, 50)  # right
            self.rect_frame.add_aperture(45, 245, 50)  # bottom
        except ValueError as err:
            self.fail('Should not throw any exceptions on correct coordinates and width. Error message: {}'.format(str(err)))

    def test_wrong_width_validation(self):
        """
        Test validation of aperture with (should not exceed wall sizes)
        """
        # left
        with self.assertRaisesRegex(ValueError, "Aperture width exceed wall sizes"):
            self.rect_frame.add_aperture(10, 50, 250)
        # top
        with self.assertRaisesRegex(ValueError, "Aperture width exceed wall sizes"):
            self.rect_frame.add_aperture(55, 20, 350)
        # right
        with self.assertRaisesRegex(ValueError, "Aperture width exceed wall sizes"):
            self.rect_frame.add_aperture(335, 60, 250)
        # bottom
        with self.assertRaisesRegex(ValueError, "Aperture width exceed wall sizes"):
            self.rect_frame.add_aperture(45, 245, 350)

    def test_aperture_draw(self):
        """
        Test that added aperture correctly drawed
        """
        from svgwrite import shapes, mm
        # left
        self.rect_frame.add_aperture(10, 50, 50)
        svg_objects = self.rect_frame._draw()
        self.assertLength(svg_objects, 3)
        aperture = svg_objects[2]
        self.assertIsInstance(aperture, shapes.Rect)
        self.assertAttrib(aperture, 'x', 10 * mm)
        self.assertAttrib(aperture, 'y', 50 * mm)
        self.assertAttrib(aperture, 'width', self.WALL_WIDTH * mm)
        self.assertAttrib(aperture, 'height', 50 * mm)
        # top
        self.rect_frame.add_aperture(55, 20, 50)
        svg_objects = self.rect_frame._draw()
        self.assertLength(svg_objects, 4)
        aperture = svg_objects[3]
        self.assertIsInstance(aperture, shapes.Rect)
        self.assertAttrib(aperture, 'x', 55 * mm)
        self.assertAttrib(aperture, 'y', 20 * mm)
        self.assertAttrib(aperture, 'width', 50 * mm)
        self.assertAttrib(aperture, 'height', self.WALL_WIDTH * mm)