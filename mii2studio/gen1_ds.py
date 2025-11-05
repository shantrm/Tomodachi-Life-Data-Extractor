# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (
        kaitaistruct.__version__))


class CoreDataDs(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.favorite = self._io.read_bits_int_le(1) != 0
        self.favorite_color = self._io.read_bits_int_le(4)
        self.birth_day = self._io.read_bits_int_le(5)
        self.birth_month = self._io.read_bits_int_le(4)
        self.gender = self._io.read_bits_int_le(1) != 0
        self.unknown_1 = self._io.read_bits_int_le(1) != 0
        self._io.align_to_byte()
        self.mii_name = (self._io.read_bytes(20)).decode(u"utf-16le")
        self.body_height = self._io.read_u1()
        self.body_weight = self._io.read_u1()
        self.avatar_id = [None] * (4)
        for i in range(4):
            self.avatar_id[i] = self._io.read_u1()

        self.client_id = [None] * (4)
        for i in range(4):
            self.client_id[i] = self._io.read_u1()

        self.downloaded = self._io.read_bits_int_le(1) != 0
        self.unknown_2 = self._io.read_bits_int_le(1) != 0
        self.mingle = self._io.read_bits_int_le(1) != 0
        self.unknown_3 = self._io.read_bits_int_le(3)
        self.facial_feature = self._io.read_bits_int_le(4)
        self.face_color = self._io.read_bits_int_le(3)
        self.face_type = self._io.read_bits_int_le(3)
        self.unknown_4 = self._io.read_bits_int_le(5)
        self.hair_flip = self._io.read_bits_int_le(1) != 0
        self.hair_color = self._io.read_bits_int_le(3)
        self.hair_type = self._io.read_bits_int_le(7)
        self.unknown_5 = self._io.read_bits_int_le(6)
        self.eyebrow_rotation = self._io.read_bits_int_le(4)
        self.unknown_6 = self._io.read_bits_int_le(1) != 0
        self.eyebrow_type = self._io.read_bits_int_le(5)
        self.eyebrow_horizontal = self._io.read_bits_int_le(4)
        self.eyebrow_vertical = self._io.read_bits_int_le(5)
        self.eyebrow_size = self._io.read_bits_int_le(4)
        self.eyebrow_color = self._io.read_bits_int_le(3)
        self.eye_vertical = self._io.read_bits_int_le(5)
        self.eye_rotation = self._io.read_bits_int_le(3)
        self.unknown_7 = self._io.read_bits_int_le(2)
        self.eye_type = self._io.read_bits_int_le(6)
        self.unknown_8 = self._io.read_bits_int_le(5)
        self.eye_horizontal = self._io.read_bits_int_le(4)
        self.eye_size = self._io.read_bits_int_le(3)
        self.unknown_9 = self._io.read_bits_int_le(1) != 0
        self.eye_color = self._io.read_bits_int_le(3)
        self.unknown_10 = self._io.read_bits_int_le(3)
        self.nose_vertical = self._io.read_bits_int_le(5)
        self.nose_size = self._io.read_bits_int_le(4)
        self.nose_type = self._io.read_bits_int_le(4)
        self.mouth_vertical = self._io.read_bits_int_le(5)
        self.mouth_size = self._io.read_bits_int_le(4)
        self.mouth_color = self._io.read_bits_int_le(2)
        self.mouth_type = self._io.read_bits_int_le(5)
        self.glasses_vertical = self._io.read_bits_int_le(5)
        self.glasses_size = self._io.read_bits_int_le(3)
        self.unknown_11 = self._io.read_bits_int_le(1) != 0
        self.glasses_color = self._io.read_bits_int_le(3)
        self.glasses_type = self._io.read_bits_int_le(4)
        self.facial_hair_vertical = self._io.read_bits_int_le(5)
        self.facial_hair_size = self._io.read_bits_int_le(4)
        self.facial_hair_color = self._io.read_bits_int_le(3)
        self.facial_hair_beard = self._io.read_bits_int_le(2)
        self.facial_hair_mustache = self._io.read_bits_int_le(2)
        self.unknown_12 = self._io.read_bits_int_le(1) != 0
        self.mole_horizontal = self._io.read_bits_int_le(5)
        self.mole_vertical = self._io.read_bits_int_le(5)
        self.mole_size = self._io.read_bits_int_le(4)
        self.mole_enable = self._io.read_bits_int_le(1) != 0
        self._io.align_to_byte()
        self.creator_name = (self._io.read_bytes(20)).decode(u"utf-16le")
