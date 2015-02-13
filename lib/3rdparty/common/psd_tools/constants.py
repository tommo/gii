# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class Enum(object):

    _attributes_cache = None
    _values_dict_cache = None

    @classmethod
    def _attributes(cls):
        if cls._attributes_cache is None:
            attrs = [name for name in dir(cls)
                    if name.isupper() and not name.startswith('_')]
            cls._attributes_cache = attrs
        return cls._attributes_cache

    @classmethod
    def _values_dict(cls):
        if cls._values_dict_cache is None:
            cls._values_dict_cache = dict([
                (getattr(cls, name), name)
                for name in cls._attributes()
            ])
        return cls._values_dict_cache

    @classmethod
    def is_known(cls, value):
        return value in cls._values_dict()

    @classmethod
    def name_of(cls, value):
        return cls._values_dict().get(value, "<unknown>")


class ColorMode(Enum):
    BITMAP = 0
    GRAYSCALE = 1
    INDEXED = 2
    RGB = 3
    CMYK = 4
    MULTICHANNEL = 7
    DUOTONE = 8
    LAB = 9

class ChannelID(Enum):
    TRANSPARENCY_MASK = -1
    USER_LAYER_MASK = -2
    REAL_USER_LAYER_MASK = -3

class ImageResourceID(Enum):
    OBSOLETE1 = 1000
    MAC_PRINT_MANAGER_INFO = 1001
    OBSOLETE2 = 1003
    RESOLUTION_INFO = 1005
    ALPHA_NAMES_PASCAL = 1006
    DISPLAY_INFO_OBSOLETE = 1007
    CAPTION_PASCAL = 1008
    BORDER_INFO = 1009
    BACKGROUND_COLOR = 1010
    PRINT_FLAGS = 1011
    GRAYSCALE_HALFTONING_INFO = 1012
    COLOR_HALFTONING_INFO = 1013
    DUOTONE_HALFTONING_INFO = 1014
    GRAYSCALE_TRANSFER_FUNCTION = 1015
    COLOR_TRANSFER_FUNCTION = 1016
    DUOTONE_TRANSFER_FUNCTION = 1017
    DUOTONE_IMAGE_INFO = 1018
    EFFECTIVE_BW = 1019
    OBSOLETE3 = 1020
    EPS_OPTIONS = 1021
    QUICK_MASK_INFO = 1022
    OBSOLETE4 = 1023
    LAYER_STATE_INFO = 1024
    WORKING_PATH = 1025
    LAYER_GROUP_INFO = 1026
    OBSOLETE5 = 1027
    IPTC_NAA = 1028
    IMAGE_MODE_RAW = 1029
    JPEG_QUALITY = 1030
    GRID_AND_GUIDES_INFO = 1032
    THUMBNAIL_RESOURCE_PS4 = 1033
    COPYRIGHT_FLAG = 1034
    URL = 1035
    THUMBNAIL_RESOURCE = 1036
    GLOBAL_ANGLE_OBSOLETE = 1037
    COLOR_SAMPLERS_RESOURCE_OBSOLETE = 1038
    ICC_PROFILE = 1039
    WATERMARK = 1040
    ICC_UNTAGGED_PROFILE = 1041
    EFFECTS_VISIBLE = 1042
    SPOT_HALFTONE = 1043
    IDS_SEED_NUMBER = 1044
    ALPHA_NAMES_UNICODE = 1045
    INDEXED_COLOR_TABLE_COUNT = 1046
    TRANSPARENCY_INDEX = 1047
    GLOBAL_ALTITUDE = 1049
    SLICES = 1050
    WORKFLOW_URL = 1051
    JUMP_TO_XPEP = 1052
    ALPHA_IDENTIFIERS = 1053
    URL_LIST = 1054
    VERSION_INFO = 1057
    EXIF_DATA_1 = 1058
    EXIF_DATA_3 = 1059
    XMP_METADATA = 1060
    CAPTION_DIGEST = 1061
    PRINT_SCALE = 1062
    PIXEL_ASPECT_RATIO = 1064
    LAYER_COMPS = 1065
    ALTERNATE_DUOTONE_COLORS = 1066
    ALTERNATE_SPOT_COLORS = 1067
    LAYER_SELECTION_IDS = 1069
    HDR_TONING_INFO = 1070
    PRINT_INFO_CS2 = 1071
    LAYER_GROUPS_ENABLED_ID = 1072
    COLOR_SAMPLERS_RESOURCE = 1073
    MEASURMENT_SCALE = 1074
    TIMELINE_INFO = 1075
    SHEET_DISCLOSURE = 1076
    DISPLAY_INFO = 1077
    ONION_SKINS = 1078
    COUNT_INFO = 1080
    PRINT_INFO_CS5 = 1082
    PRINT_STYLE = 1083
    MAC_NSPRINTINFO = 1084
    WINDOWS_DEVMODE = 1085
    AUTO_SAVE_FILE_PATH = 1086
    AUTO_SAVE_FORMAT = 1087
    PATH_SELECTION_STATE = 1088

    # PATH_INFO = 2000...2997
    PATH_INFO_0 = 2000
    PATH_INFO_LAST = 2997
    CLIPPING_PATH_NAME = 2999
    ORIGIN_PATH_INFO = 3000

    # PLUGIN_RESOURCES = 4000..4999
    PLUGIN_RESOURCES_0 = 4000
    PLUGIN_RESOURCES_LAST = 4999

    IMAGE_READY_VARIABLES = 7000
    IMAGE_READY_DATA_SETS = 7001
    LIGHTROOM_WORKFLOW = 8000
    PRINT_FLAGS_INFO = 10000

    @classmethod
    def is_known(cls, value):
        path_info = cls.PATH_INFO_0 <= value <= cls.PATH_INFO_LAST
        plugin_resource = cls.PLUGIN_RESOURCES_0 <= value <= cls.PLUGIN_RESOURCES_LAST
        return super(ImageResourceID, cls).is_known(value) or path_info or plugin_resource

    @classmethod
    def name_of(cls, value):
        if cls.PATH_INFO_0 < value < cls.PATH_INFO_LAST:
            return "PATH_INFO_%d" % (value - cls.PATH_INFO_0)
        if cls.PLUGIN_RESOURCES_0 < value < cls.PLUGIN_RESOURCES_LAST:
            return "PLUGIN_RESOURCES_%d" % (value - cls.PLUGIN_RESOURCES_0)
        return super(ImageResourceID, cls).name_of(value)



class BlendMode(Enum):
    PASS_THROUGH = 'pass'
    NORMAL = 'norm'
    DISSOLVE = 'diss'
    DARKEN = 'dark'
    MULTIPLY = 'mul '
    COLOR_BURN = 'idiv'
    LINEAR_BURN = 'lbrn'
    DARKER_COLOR = 'dkCl'
    LIGHTEN = 'lite'
    SCREEN = 'scrn'
    COLOR_DODGE = 'div '
    LINEAR_DODGE = 'lddg'
    LIGHTER_COLOR = 'lgCl'
    OVERLAY = 'over'
    SOFT_LIGHT = 'sLit'
    HARD_LIGHT = 'hLit'
    VIVID_LIGHT = 'vLit'
    LINEAR_LIGHT = 'lLit'
    PIN_LIGHT = 'pLit'
    HARD_MIX = 'hMix'
    DIFFERENCE = 'diff'
    EXCLUSION = 'smud'
    SUBTRACT = 'fsub'
    DIVIDE = 'fdiv'
    HUE = 'hue '
    SATURATION = 'sat '
    COLOR = 'colr'
    LUMINOSITY = 'lum '


class Clipping(Enum):
    BASE = 0
    NON_BASE = 1


class GlobalLayerMaskKind(Enum):
    COLOR_SELECTED = 0
    COLOR_PROTECTED = 1
    PER_LAYER = 128
    # others options are possible in beta versions.


class Compression(Enum):
    RAW = 0
    PACK_BITS = 1
    ZIP = 2
    ZIP_WITH_PREDICTION = 3


class PrintScaleStyle(Enum):
    CENTERED = 0
    SIZE_TO_FIT = 1
    USER_DEFINED = 2


class TaggedBlock(Enum):

    _ADJUSTMENT_KEYS = set([
        'SoCo', 'GdFl', 'PtFl', 'brit', 'levl', 'curv', 'expA',
        'vibA', 'hue ', 'hue2', 'blnc', 'blwh', 'phfl', 'mixr',
        'clrL', 'nvrt', 'post', 'thrs', 'grdm', 'selc',
    ])

    SOLID_COLOR = 'SoCo'
    GRADIENT = 'GdFl'
    PATTERN = 'PtFl'
    BRIGHTNESS_CONTRAST = 'brit'
    LEVELS = 'levl'
    CURVES = 'curv'
    EXPOSURE = 'expA'
    VIBRANCE = 'vibA'
    HUE_SATURATION_4 = 'hue '
    HUE_SATURATION_5 = 'hue2'
    COLOR_BALANCE = 'blnc'
    BLACK_AND_WHITE = 'blwh'
    PHOTO_FILTER = 'phfl'
    CHANNEL_MIXER = 'mixr'
    COLOR_LOOKUP = 'clrL'
    INVERT = 'nvrt'
    POSTERIZE = 'post'
    THRESHOLD = 'thrs'
    GRADIENT_MAP = 'grdm'
    SELECTIVE_COLOR = 'selc'

    @classmethod
    def is_adjustment_key(cls, key):
        return key in cls._ADJUSTMENT_KEYS

    EFFECTS_LAYER = 'lrFX'
    TYPE_TOOL_INFO = 'tySh'
    UNICODE_LAYER_NAME = 'luni'
    LAYER_ID = 'lyid'
    OBJECT_BASED_EFFECTS_LAYER_INFO = 'lfx2'

    PATTERNS1 = 'Patt'
    PATTERNS2 = 'Pat2'
    PATTERNS3 = 'Pat3'

    ANNOTATIONS = 'Anno'
    BLEND_CLIPPING_ELEMENTS = 'clbl'
    BLEND_INTERIOR_ELEMENTS = 'infx'

    KNOCKOUT_SETTING = 'knko'
    PROTECTED_SETTING = 'lspf'
    SHEET_COLOR_SETTING = 'lclr'
    REFERENCE_POINT = 'fxrp'
    GRADIENT_SETTINGS = 'grdm'
    SECTION_DIVIDER_SETTING = 'lsct'
    NESTED_SECTION_DIVIDER_SETTING = 'lsdk'
    CHANNEL_BLENDING_RESTRICTIONS_SETTING = 'brst'
    SOLID_COLOR_SHEET_SETTING = 'SoCo'
    PATTERN_FILL_SETTING = 'PtFl'
    GRADIENT_FILL_SETTING = 'GdFl'
    VECTOR_MASK_SETTING1 = 'vmsk'
    VECTOR_MASK_SETTING2 = 'vsms'
    TYPE_TOOL_OBJECT_SETTING = 'TySh'
    FOREIGN_EFFECT_ID = 'ffxi'
    LAYER_NAME_SOURCE_SETTING = 'lnsr'
    PATTERN_DATA = 'shpa'
    METADATA_SETTING = 'shmd'
    LAYER_VERSION = 'lyvr'
    TRANSPARENCY_SHAPES_LAYER = 'tsly'
    LAYER_MASK_AS_GLOBAL_MASK = 'lmgm'
    VECTOR_MASK_AS_GLOBAL_MASK = 'vmgm'
    VECTOR_ORIGINATION_DATA = 'vogk'

    # XXX: these are duplicated
    BRIGHTNESS_AND_CONTRAST = 'brit'
    CHANNEL_MIXER = 'mixr'
    COLOR_LOOKUP = 'clrL'

    PLACED_LAYER_OBSOLETE1 = 'plLd'
    PLACED_LAYER_OBSOLETE2 = 'PlLd'

    LINKED_LAYER1 = 'lnkD'
    LINKED_LAYER2 = 'lnk2'
    LINKED_LAYER3 = 'lnk3'
    PHOTO_FILTER = 'phfl'
    BLACK_WHITE = 'blwh'
    CONTENT_GENERATOR_EXTRA_DATA = 'CgEd'
    TEXT_ENGINE_DATA = 'Txt2'
    VIBRANCE = 'vibA'
    UNICODE_PATH_NAME = 'pths'
    ANIMATION_EFFECTS = 'anFX'
    FILTER_MASK = 'FMsk'
    PLACED_LAYER_DATA = 'SoLd'

    VECTOR_STROKE_DATA = 'vscg'
    USING_ALIGNED_RENDERING = 'sn2P'
    SAVING_MERGED_TRANSPARENCY = 'Mtrn'
    SAVING_MERGED_TRANSPARENCY16 = 'Mt16'
    SAVING_MERGED_TRANSPARENCY32 = 'Mt32'
    USER_MASK = 'LMsk'
    EXPOSURE = 'expA'
    FILTER_EFFECTS1 = 'FXid'
    FILTER_EFFECTS2 = 'FEid'

    LAYER_16 = "Lr16"
    LAYER_32 = "Lr32"
    LAYER = "Layr"


class OSType(Enum):
    """
    Action descriptor type
    """
    REFERENCE = b'obj '
    DESCRIPTOR = b'Objc'
    LIST = b'VlLs'
    DOUBLE = b'doub'
    UNIT_FLOAT = b'UntF'
    STRING = b'TEXT'
    ENUMERATED = b'enum'
    INTEGER = b'long'
    BOOLEAN = b'bool'
    GLOBAL_OBJECT = b'GlbO'
    CLASS1 = b'type'
    CLASS2 = b'GlbC'
    ALIAS = b'alis'
    RAW_DATA = b'tdta'

class ReferenceOSType(Enum):
    """
    OS Type keys for Reference Structure
    """
    PROPERTY = b'prop'
    CLASS = b'Clss'
    ENUMERATED_REFERENCE = b'Enmr'
    OFFSET = b'rele'
    IDENTIFIER = b'Idnt'
    INDEX = b'indx'
    NAME = b'name'

class UnitFloatType(Enum):
    """
    Units the value is in (used in Unit float structure)
    """
    ANGLE = b'#Ang'  # base degrees
    DENSITY = b'#Rsl' # base per inch
    DISTANCE = b'#Rlt' # base 72ppi
    NONE = b'#Nne' # coerced
    PERCENT = b'#Prc' # unit value
    PIXELS = b'#Pxl' # tagged unit value
    POINTS = b'#Pnt' # points
    MILLIMETERS = b'#Mlm' # millimeters

class SectionDivider(Enum):
    OTHER = 0
    OPEN_FOLDER = 1
    CLOSED_FOLDER = 2
    BOUNDING_SECTION_DIVIDER = 3

class DisplayResolutionUnit(Enum):
    PIXELS_PER_INCH = 1
    PIXELS_PER_CM = 2

class DimensionUnit(Enum):
    INCH = 1
    CM = 2
    POINT = 3  # 72 points == 1 inch
    PICA = 4   # 6 pica == 1 inch
    COLUMN = 5

class TextProperty(Enum):
    TXT = 'Txt '
    ORIENTATION = 'Ornt'

class TextOrientation(Enum):
    HORIZONTAL = 'Hrzn'
