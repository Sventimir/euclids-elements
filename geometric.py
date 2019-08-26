import math
import itertools

def square(x):
    return x * x

def quadratic(a, b, c):
    delta = b ** 2 - 4 * a * c
    if delta < 0:
        return tuple()
    elif delta == 0:
        return ((-b) / (2 * a), )
    else:
        return ((d - b) / (2 * a) for d in (math.sqrt(delta), -math.sqrt(delta)))

def list_bind(l, f):
    itertools.chain(*(f(x) for x in l))

class Vector:

    @classmethod
    def from_polar(cls, r, theta):
        return cls(r * math.cos(theta), r * math.sin(theta))

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return '[{} {}]'.format(self.x, self.y)

    def __eq__(self, v):
        return self.x == v.x and self.y == v.y

    def __neg__(self):
        return self.scale(-1)

    def scale(self, factor):
        return self.__class__(self.x * factor, self.y * factor)

    @property
    def perpendicular(self):
        return self.__class__(self.y, - self.x)

    @property
    def magnitude(self):
        return math.sqrt(square(self.x) + square(self.y))

    @property
    def slope(self):
        try:
            return self.y / self.x
        except ZeroDivisionError:
            return float('nan')

    @property
    def angle(self): # angle agains x-axis
        slope = self.slope
        return math.pi / 2 if math.isnan(slope) else \
            math.atan(slope) if slope >= 0 else -math.atan(-slope)

    def __add__(self, v):
        return self.__class__(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return self.__class__(self.x - v.x, self.y - v.y)

    def by_matrix(self, m):
        return self.__class__(
            self.x * m.rows[0][0] + self.y * m.rows[0][1],
            self.x * m.rows[1][0] + self.y * m.rows[1][1]
        )


class Matrix:

    def __init__(self, *rows):
        self.rows = tuple(rows)

    def __repr__(self):
        return '[{} {}]\n[{} {}]'.format(*itertools.chain(*self.rows))

    @classmethod
    def identity(cls):
        return cls((1.0, 0.0), (0.0, 1.0))

    @property
    def determinant(self):
        return self.rows[0][0] * self.rows[1][1] - self.rows[0][1] * self.rows[1][0]

    @property
    def inverse(self):
        r1 = (self.rows[1][1], -self.rows[0][1])
        r2 = (-self.rows[1][0], self.rows[0][0])
        try:
            return self.__class__(r1, r2).scale(1.0 / self.determinant)
        except ZeroDivisionError:
            return None

    def scale(self, f):
        return self.__class__(*(tuple(x * f for x in r) for r in self.rows))

class Point:

    @classmethod
    def origin(cls):
        return cls(0, 0)

    def __init__(self, x, y, label=None, anchor=None):
        self.x = float(x)
        self.y = float(y)
        self.set_label(label, anchor)

    def __repr__(self):
        return 'Point({}{}, {})'.format(
            '' if self.label is None else self.label + ':',
            self.x,
            self.y
        )

    def set_label(self, label, anchor=None):
        self.anchor = anchor
        self.label = label
        self.is_label_displayed = False
        return self

    @property
    def vect(self):
        return Vector(self.x, self.y)

    def to_pair(self):
        return (self.x, self.y)

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

    def draw_dot(self, radius='0.75pt'):
        print('\\draw {} [fill=black] circle ({});'.format(self.display(), radius))


def draw_lines(*points):
    print('\\draw {};'.format(' -- '.join(p.display() for p in points)))


class Line:

    def __init__(self, anchor, vector):
        self.anchor = anchor
        self.vector = vector.scale(1 / vector.magnitude)

    def __repr__(self):
        return 'Line({} + s{})'.format(self.anchor.vect, self.vector)

    def perpendicular(self, through):
        return self.__class__(through, self.vector.perpendicular)

    def find(self, factor):
        return self.anchor.translate(self.vector.scale(factor))

    def intersection(self, line):
        '''Solve equations system for scales of both lines to the point of
           intersection if one does exist. Then find that point on the line.'''
        anchor = line.anchor.vect - self.anchor.vect
        m = Matrix(
            (self.vector.x, -line.vector.x),
            (self.vector.y, -line.vector.y)
        )
        try:
            scales = anchor.by_matrix(m.inverse)
            return self.find(scales.x)
        except AttributeError:
            return None

    def __int_circ_zero_vect(self, const_attr, z, circle):
        const_attr_val = getattr(z, const_attr)
        other_attr = 'x' if const_attr == 'y' else 'y'
        results = quadratic(1, 0, const_attr_val ** 2 - circle.radius ** 2)
        for r in results:
            v = Vector(0, 0)
            setattr(v, const_attr, -const_attr_val)
            setattr(v, other_attr, r)
            yield v

    def intersect_circle(self, circle):
        z = circle.center.vect - self.anchor.vect
        if self.vector.x == 0:
            rs = self.__int_circ_zero_vect('x', z, circle)
        elif self.vector.y == 0:
            rs = self.__int_circ_zero_vect('y', z, circle)
        else:
            t = (self.vector.y * z.x - self.vector.x * z.y) / self.vector.x
            a = (self.vector.y ** 2 / self.vector.x ** 2) + 1
            b = 2 * self.vector.y * t / self.vector.x
            c = t ** 2 - circle.radius ** 2
            xs = quadratic(a, b, c)
            rs = (Vector(x, (self.vector.y * x / self.vector.x) + b) for x in xs)
        return tuple(circle.center.translate(r) for r in rs)

    def draw(self, scale_up, scale_down):
        draw_lines(self.find(scale_down), self.find(scale_up))
        if self.anchor.label is not None:
            self.anchor.draw()


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
        if self.center.label is not None:
            self.center.draw_dot()
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
        return self.__class__(*(v.translate(vector) for v in self.vertices))

    def draw(self):
        print('\\draw {} -- cycle;'.format(' -- '.join(p.display() for p in self.vertices)))


# Constructions:
def symmetral(a, b):
    segment = a.line_to(b)
    return segment.perpendicular(a.translate(segment.vector.scale(a.dist(b) / 2.0)))

def circles_intersection(c1, c2):
    d = c1.center.vect_to(c2.center)
    dist = d.magnitude
    summa_radii = c1.radius + c2.radius
    differentia_radii = abs(c1.radius - c2.radius)
    if dist == summa_radii:
        return (c1.find(c1.center.vect_to(c2.center)), )
    elif dist == differentia_radii:
        return (c1.find(-c1.center.vect_to(c2.center)), )
    elif dist > summa_radii or dist < differentia_radii:
        return tuple()
    # it is important that vector points to increasing xs or increasing ys
    if d.x > 0 or (d.x == 0 and d.y > 0):
        left, right = c1, c2
    else:
        d = -d
        left, right = c2, c1
    lr, rr = left.radius, right.radius
    angle = math.acos((dist ** 2 + lr ** 2 - rr ** 2) / (2 * lr * dist))
    vs = (Vector.from_polar(lr, theta) for theta in (d.angle + angle, d.angle - angle))
    return tuple(left.center.translate(v) for v in vs)

def equilateral_triangle(a, b):
    ''' Given two points return all possible vertices of an equilateral triangle.'''
    ab = a.line_to(b)
    mid = a.translate(ab.vector.scale(a.dist(b) / 2.0))
    h = ab.perpendicular(mid)
    height = a.dist(b) * math.sqrt(3) / 2.0
    return (mid.translate(h.vector.scale(height)), mid.translate(h.vector.scale(-height)))
