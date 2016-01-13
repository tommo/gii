# Copyright (c) 2014 Johnnie Walker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math

##
# Define an affine transform.
#
# @def AffineTransform(matrix)
# @param matrix A 6-tuple (<i>a, b, c, d, e, f</i>) containing
#    the first two rows from an affine transform matrix.

class AffineTransform:
    """an affine matrix transform"""
    def __init__(self, matrix=(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)):
        self.m = list(matrix)

    def __repr__(self):
        return str(self.m)
        
    def __eq__(self, other):
        if type(other) == type(self):
            return self.m == other.m
        return False

    def __copy__(self):
        c = AffineTransform()
        c.m = self.m
        return c

    def multiply(self, t):
        m11 = (self.m[0] * t.m[0]) + (self.m[1] * t.m[2])
        m12 = (self.m[0] * t.m[1]) + (self.m[1] * t.m[3])
    
        m21 = (self.m[2] * t.m[0]) + (self.m[3] * t.m[2])
        m22 = (self.m[2] * t.m[1]) + (self.m[3] * t.m[3])
    
        dx = (self.m[4] * t.m[0]) + (self.m[5] * t.m[2]) + t.m[4]
        dy = (self.m[4] * t.m[1]) + (self.m[5] * t.m[3]) + t.m[5]

        self.m[0] = m11
        self.m[1] = m12
        self.m[2] = m21
        self.m[3] = m22
        self.m[4] = dx
        self.m[5] = dy
        
    def invert(self):
        d = 1 / (self.m[0] * self.m[3] - self.m[1] * self.m[2])
        m0 = self.m[3] * d
        m1 = -self.m[1] * d
        m2 = -self.m[2] * d
        m3 = self.m[0] * d
        m4 = d * (self.m[2] * self.m[5] - self.m[3] * self.m[4])
        m5 = d * (self.m[1] * self.m[4] - self.m[0] * self.m[5])

        self.m[0] = m0
        self.m[1] = m1
        self.m[2] = m2
        self.m[3] = m3
        self.m[4] = m4
        self.m[5] = m5

    def rotate(self, radians):
        c = math.cos(radians);
        s = math.sin(radians);
        m11 = (self.m[0] * c) + (self.m[2] * s)
        m12 = (self.m[1] * c) + (self.m[3] * s)
        m21 = (self.m[0] * -s) + (self.m[2] * c)
        m22 = (self.m[1] * -s) + (self.m[3] * c)

        self.m[0] = m11
        self.m[1] = m12
        self.m[2] = m21
        self.m[3] = m22

    def translate(self, x, y):
        self.m[4] += self.m[0] * x + self.m[2] * y
        self.m[5] += self.m[1] * x + self.m[3] * y

    def scale(self, sx, sy):
        self.m[0] *= sx
        self.m[1] *= sx
        self.m[2] *= sy
        self.m[3] *= sy
        
    ##
    # Apply the matrix transform to a point
    #
    # A point is never scaled, as it has no size
    #
    # @def transformPoint(x, y)
    # @return a tuple representing the transformed point (x, y)
    ##
        
    def transformPoint(self, x, y):
        return ((x * self.m[0]) + (y * self.m[2]) + self.m[4], (x * self.m[1]) + (y * self.m[3]) + self.m[5])
        
    ##
    # Apply the matrix transform to a point
    #
    # A size is never translated, as it has no origin
    # @def transformSize(width, height)
    # @return a tuple representing the transformed size (width, height)
    ##
        
    def transformSize(self, width, height):
        return ((width * self.m[0]) + (height * self.m[2]), (width * self.m[1]) + (height * self.m[3]))
        
    ##
    # Transform an othogonal rectangle
    #
    # Each of the four points defining `r` are transformed
    # as `transformPoint`. The returned rectangle is the smallest 
    # rect containing the transformed points
    #
    # @def transformRect(x, y, width, height)
    # @param x the x origin of the rectangle
    # @param y the y origin of the rectangle
    # @param width the width of the rectangle
    # @param height the height of the rectangle            
    # @return a tuple contain
    ##
        
    def transformRect(self, x, y, width, height):
        rp1 = self.transformPoint(x, y)
        rp2 = self.transformPoint(x+width, y)
        rp3 = self.transformPoint(x+width, y+height)
        rp4 = self.transformPoint(x, y+height)	
        arr =  [rp2, rp3, rp4]
        minX = rp1[0]
        minY = rp1[1]
        maxX = rp1[0]
        maxY = rp1[1]
        for rp in arr:
            minX = min(minX, rp[0])
            minY = min(minY, rp[1])
            maxX = max(maxX, rp[0])
            maxY = max(maxY, rp[1])

    	return (minX, minY, maxX - minX, maxY - minY);
        