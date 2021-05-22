from .utils import AnyStruct


def string_from_bytes(b):
    return b.rstrip(b'\0').decode('utf-8', errors='ignore')


def string_to_bytes(s):
    return s.encode('utf-8')


Header = AnyStruct('Header', (
    ('magic', '4s'),
    ('version', 'i'),
    ('num_meshes', 'i'),
    ('num_materials', 'i'),
))

Mesh = AnyStruct('Mesh', (
    ('name', '64s', 1, string_from_bytes, string_to_bytes),
    ('index', 'i'),
    ('num_verts', 'i'),
    ('num_st', 'i'),
    ('num_normals', 'i'),
))

Vertex = AnyStruct('Vertex', (
    ('x', 'f'),
    ('y', 'f'),
    ('z', 'f')
))

ST = AnyStruct('ST', (
    ('u', 'f'),
    ('v', 'f'),
))

Material = AnyStruct('Material', (
    ('name', '64s', 1, string_from_bytes, string_to_bytes),
    ('spec_exp', 'f'),
    ('ambient', '3f', 3),
    ('diffuse', '3f', 3),
    ('specular', '3f', 3),
    ('diffuse_texture', '64s', 1, string_from_bytes, string_to_bytes),
    ('normal_texture', '64s', 1, string_from_bytes, string_to_bytes),
))
