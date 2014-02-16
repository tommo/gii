# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

import logging
import collections
import weakref              # FIXME: there should be weakrefs in this module
import psd_tools.reader
import psd_tools.decoder
from psd_tools.constants import TaggedBlock, SectionDivider, BlendMode, TextProperty
from psd_tools.user_api.layers import group_layers
from psd_tools.user_api import pymaging_support
from psd_tools.user_api import pil_support

logger = logging.getLogger(__name__)

class BBox(collections.namedtuple('BBox', 'x1, y1, x2, y2')):
    @property
    def width(self):
        return self.x2-self.x1

    @property
    def height(self):
        return self.y2-self.y1


class TextData(object):
    def __init__(self, tagged_blocks):
        text_data = dict(tagged_blocks.text_data.items)
        self.text = text_data[TextProperty.TXT].value


class _RawLayer(object):
    """
    Layer groups and layers are internally both 'layers' in PSD;
    they share some common properties.
    """

    parent = None
    _psd = None
    _index = None

    @property
    def name(self):
        """ Layer name (as unicode). """
        return self._tagged_blocks.get(
            TaggedBlock.UNICODE_LAYER_NAME,
            self._info.name
        )

    @property
    def visible(self):
        """ Layer visibility. Doesn't take group visibility in account. """
        return self._info.flags.visible

    @property
    def visible_global(self):
        """ Layer visibility. Takes group visibility in account. """
        return self.visible and self.parent.visible

    @property
    def layer_id(self):
        return self._tagged_blocks.get(TaggedBlock.LAYER_ID)

    @property
    def opacity(self):
        return self._info.opacity

    @property
    def blend_mode(self):
        return self._info.blend_mode

    @property
    def _info(self):
        return self._psd._layer_info(self._index)

    @property
    def _tagged_blocks(self):
        return dict(self._info.tagged_blocks)


class Layer(_RawLayer):
    """ PSD layer wrapper """

    def __init__(self, parent, index):
        self.parent = parent
        self._psd = parent._psd
        self._index = index

    def as_PIL(self):
        """ Returns a PIL image for this layer. """
        return self._psd._layer_as_PIL(self._index)

    def as_pymaging(self):
        """ Returns a pymaging.Image for this PSD file. """
        return self._psd._layer_as_pymaging(self._index)

    @property
    def bbox(self):
        """ BBox(x1, y1, x2, y2) namedtuple with layer bounding box. """
        info = self._info
        return BBox(info.left, info.top, info.right, info.bottom)

    @property
    def text_data(self):
        tagged_blocks = self._tagged_blocks.get(TaggedBlock.TYPE_TOOL_OBJECT_SETTING)
        if tagged_blocks:
            return TextData(tagged_blocks)

    def __repr__(self):
        bbox = self.bbox
        return "<psd_tools.Layer: %r, size=%dx%d, x=%d, y=%d>" % (
            self.name, bbox.width, bbox.height, bbox.x1, bbox.y1)


class Group(_RawLayer):
    """ PSD layer group wrapper """

    def __init__(self, parent, index, layers):
        self.parent = parent
        self._psd = parent._psd
        self._index = index
        self.layers = layers

    @property
    def closed(self):
        divider = self._tagged_blocks.get(TaggedBlock.SECTION_DIVIDER_SETTING, None)
        if divider is None:
            return
        return divider.type == SectionDivider.CLOSED_FOLDER

    @property
    def bbox(self):
        """
        BBox(x1, y1, x2, y2) namedtuple with a bounding box for
        all layers in this group; None if a group has no children.
        """
        return combined_bbox(self.layers)


    def as_PIL(self):
        """
        Returns a PIL image for this group.
        This is highly experimental.
        """
        return merge_layers(self.layers, respect_visibility=True)

    def _add_layer(self, child):
        self.layers.append(child)

    def __repr__(self):
        return "<psd_tools.Group: %r, layer_count=%d>" % (
            self.name, len(self.layers))



class PSDImage(object):
    """ PSD image wrapper """

    def __init__(self, decoded_data):
        self.header = decoded_data.header
        self.decoded_data = decoded_data

        # wrap decoded data to Layer and Group structures
        def fill_group(group, data):

            for layer in data['layers']:
                index = layer['index']

                if 'layers' in layer:
                    # group
                    sub_group = Group(group, index, [])
                    fill_group(sub_group, layer)
                    group._add_layer(sub_group)
                else:
                    # regular layer
                    group._add_layer(Layer(group, index))

        self._psd = self
        fake_root_data = {'layers': group_layers(decoded_data), 'index': None}
        root = _RootGroup(self, None, [])
        fill_group(root, fake_root_data)

        self._fake_root_group = root
        self.layers = root.layers


    @classmethod
    def load(cls, path, encoding='utf8'):
        """
        Returns a new :class:`PSDImage` loaded from ``path``.
        """
        with open(path, 'rb') as fp:
            return cls.from_stream(fp, encoding)

    @classmethod
    def from_stream(cls, fp, encoding='utf8'):
        """
        Returns a new :class:`PSDImage` loaded from stream ``fp``.
        """
        decoded_data = psd_tools.decoder.parse(
            psd_tools.reader.parse(fp, encoding)
        )
        return cls(decoded_data)


    def as_PIL(self):
        """
        Returns a PIL image for this PSD file.
        """
        return pil_support.extract_composite_image(self.decoded_data)

    def as_PIL_merged(self):
        """
        Returns a PIL image for this PSD file.
        Image is obtained by merging all layers.
        This is highly experimental.
        """
        bbox = BBox(0, 0, self.header.width, self.header.height)
        return merge_layers(self.layers, bbox=bbox)

    def as_pymaging(self):
        """
        Returns a pymaging.Image for this PSD file.
        """
        return pymaging_support.extract_composite_image(self.decoded_data)

    @property
    def bbox(self):
        """
        BBox(x1, y1, x2, y2) namedtuple with a bounding box for
        all layers in this image; None if there are no image layers.

        This may differ from the image dimensions
        (img.header.width and img.header.heigth).
        """
        return combined_bbox(self.layers)

    def _layer_info(self, index):
        layers = self.decoded_data.layer_and_mask_data.layers.layer_records
        return layers[index]

    def _layer_as_PIL(self, index):
        return pil_support.extract_layer_image(self.decoded_data, index)

    def _layer_as_pymaging(self, index):
        return pymaging_support.extract_layer_image(self.decoded_data, index)


class _RootGroup(Group):
    """ A fake group for holding all layers """

    @property
    def visible(self):
        return True

    @property
    def visible_global(self):
        return True


def combined_bbox(layers):
    """
    Returns a bounding box for ``layers`` or None if this is not possible.
    """
    bboxes = [layer.bbox for layer in layers if layer.bbox is not None]
    if not bboxes:
        return None

    lefts, tops, rights, bottoms = zip(*bboxes)
    return BBox(min(lefts), min(tops), max(rights), max(bottoms))


def merge_layers(layers, respect_visibility=True, skip_layer=lambda layer: False, bbox=None):
    """
    Merges layers together (the first layer is on top).

    By default hidden layers are not rendered;
    pass ``respect_visibility=False`` to render them.

    In order to skip some layers pass ``skip_layer`` function which
    should take ``layer` as an argument and return True or False.

    If ``crop_bbox`` is not None, it should be a 4-tuple with coordinates;
    returned image will be restricted to this rectangle.

    This is highly experimental.
    """

    # FIXME: this currently assumes PIL
    from PIL import Image

    if bbox is None:
        bbox = combined_bbox(layers)

    if bbox is None:
        return None

    result = Image.new(
        "RGBA",
        (bbox.width, bbox.height),
        color=(255, 255, 255, 0)  # fixme: transparency calculation is incorrect
    )

    for layer in reversed(layers):

        if layer is None:
            continue

        if skip_layer(layer):
            continue

        if not layer.visible and respect_visibility:
            continue

        if isinstance(layer, psd_tools.Group):
            layer_image = merge_layers(layer.layers, respect_visibility, skip_layer)
        else:
            layer_image = layer.as_PIL()

        layer_image = pil_support.apply_opacity(layer_image, layer.opacity)

        x, y = layer.bbox.x1 - bbox.x1, layer.bbox.y1 - bbox.y1
        w, h = layer_image.size

        if x < 0 or y < 0: # image doesn't fit the bbox
            x_overflow = - min(x, 0)
            y_overflow = - min(y, 0)
            logger.debug("cropping.. (%s, %s)", x_overflow, y_overflow)
            layer_image = layer_image.crop((x_overflow, y_overflow, w, h))
            x += x_overflow
            y += y_overflow

        if w+x > bbox.width or h+y > bbox.height:
            # FIXME
            logger.debug("cropping..")

        if layer.blend_mode == BlendMode.NORMAL:
            if layer_image.mode == 'RGBA':
                result.paste(layer_image, (x,y), layer_image)
            elif layer_image.mode == 'RGB':
                result.paste(layer_image, (x,y))
            else:
                logger.warning("layer image mode is unsupported for merging: %s", layer_image.mode)
                continue
        else:
            logger.warning("Blend mode is not implemented: %s", BlendMode.name_of(layer.blend_mode))
            continue

    return result
