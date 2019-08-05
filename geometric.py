import math

def square(x):
    return x * x

class Vector:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def scale(self, factor):
        return self.__class__(self.x * factor, self.y * factor)

    @property
    def perpendicular(self):
        return self.__class__(self.y, - self.x)

    @property
    def magnitude(self):
        return math.sqrt(square(self.x) + square(self.y))

    def __add__(self, v):
        return self.__class__(self.x + v.x, self.y + v.y)


class Point:

    def __init__(self, x, y, label=None, anchor=None):
        self.x = float(x)
        self.y = float(y)
        self.anchor = anchor
        self.label = label
        self.is_label_displayed = False

    def translate(self, v):
        return self.__class__(self.x + v.x, self.y + v.y)

    def vect_to(self, point):
        return Vector(point.x - self.x, point.y - self.y)

    def dist(self, point):
        return self.vect_to(point).magnitude

    def display(self):
        if self.is_label_displayed:
            return '({},{})'.format(self.x, self.y)
        else:
            anchor_str = '' if self.anchor is None else '[anchor={}] '.format(self.anchor)
            label_str = '' if self.label is None else ' node {}{{ {} }}'.format(anchor_str, self.label)
            self.is_label_displayed = True
            return '({},{}){}'.format(self.x, self.y, label_str)

    def line_to(self, point):
        return Line(self, self.vect_to(point))

    def draw(self):
        print('\\draw {};'.format(self.display()))


class Line:

    def __init__(self, anchor, vector):
        self.anchor = anchor
        self.vector = vector.scale(1 / vector.magnitude)

    def perpendicular(self, through):
        return self.__class__(through, self.vector.perpendicular)

    def find(self, factor):
        return self.anchor.translate(self.vector.scale(factor))


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = center.dist(radius) if isinstance(radius, Point) else float(radius)

    @property
    def diameter(self):
        return 2 * self.radius

    def find(self, vector):
        return self.center.translate(vector.scale(self.radius / vector.magnitude))

    def translate(self, vector):
        return self.__class__(self.center.translate(vector), self.radius)

    def draw(self, start=0, end=360):
        print('\draw {} arc ({}:{}:{});'.format(
            self.center.translate(Vector(self.radius, 0)).display(),
            start,
            end,
            self.radius
        ))


class Polygon:

    def __init__(self, *vertices):
        self.vertices = tuple(vertices)

    def translate(self, vector):
        return self.__class__(v.translate(vector) for v in self.vertices)

    def draw(self):
        print('\\draw {} -- cycle;'.format(' -- '.join(p.display() for p in self.vertices)))



def draw_lines(*points):
    print('\\draw {};'.format(' -- '.join(p.display() for p in points)))

def symmetral(a, b):
    segment = a.line_to(b)
    return segment.perpendicular(a.translate(segment.vector.scale(a.dist(b) / 2.0)))
