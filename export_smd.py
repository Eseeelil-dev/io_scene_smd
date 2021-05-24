import importlib
from . import smd
import bpy
importlib.reload(smd)
import time


class TimePrint:
    def __init__(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = time.time()

    @property
    def tm(self):
        return round(time.time() - self.start_time, 5)

    def info(self, *a, **kwargs):
        print('[{:.5f}]'.format(self.tm), '[INFO]', *a, **kwargs)

    def warn(self, *a, **kwargs):
        print('[{:.5f}]'.format(self.tm), '[WARN]', *a, **kwargs)


log = TimePrint()


def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def get_mesh_data(**kwargs):
    from bpy_extras import node_shader_utils
    mesh_data, materials = [], []

    def get_tex_path(mat_wrap, key):
        tex_wrap = getattr(mat_wrap, key, None)
        if tex_wrap is None:
            return None
        image = tex_wrap.image
        if image is None:
            return None
        return image.name

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    for mesh_object in mesh_objects:
        data = {
            'name': mesh_object.name,
            'num_verts': 0,
            'num_st': 0,
            'num_normals': 0,
            'vertices': [],
            'st': [],
            'normals': [],
        }
        me = mesh_object.to_mesh()

        if 'global_matrix' in kwargs:
            res = kwargs.get('global_matrix') @ mesh_object.matrix_world
            print('global_matrix enabled: transform')
            print(res)
            me.transform(res)

        # mesh_triangulate(me)
        uv_layer = me.uv_layers.active.data
        for poly in me.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                data['vertices'].append(me.vertices[me.loops[loop_index].vertex_index].co[:])
                data['normals'].append(me.vertices[me.loops[loop_index].vertex_index].normal[:])
                data['st'].append(uv_layer[loop_index].uv[:])

        data['num_verts'] = len(data['vertices'])
        data['num_normals'] = len(data['normals'])
        data['num_st'] = len(data['st'])

        mesh_data.append(data)
        if not len(me.materials):
            mat_data = {
                'name': 'DefaultMaterial',
                'spec_exp': 0.5,
                'ambient': (1.0, 1.0, 1.0),
                'diffuse': (0.7, 0.7, 0.7),
                'specular': (0.5, 0.5, 0.5),
                'diffuse_texture': '',
                'normal_texture': '',
            }
        else:
            mat = node_shader_utils.PrincipledBSDFWrapper(me.materials[0])
            mat_data = {
                'name': me.materials[0].name,
                'spec_exp': mat.roughness,
                'ambient': (1.0, 1.0, 1.0),
                'diffuse': mat.base_color[:3],
                'specular': (mat.specular, mat.specular, mat.specular),
                'diffuse_texture': get_tex_path(mat, 'base_color_texture') or '',
                'normal_texture': get_tex_path(mat, 'normalmap_texture') or '',
            }

        materials.append(mat_data)
        mesh_data[-1]['index'] = len(materials)
    log.info(f'Processed {len(mesh_data)} mesh data and {len(materials)} material(-s)')
    return mesh_data, materials


def save(context, **kwargs):
    log.reset()
    log.info(kwargs)
    meshes, materials = get_mesh_data(**kwargs)
    with open(kwargs['filepath'], 'wb') as file:
        header = {
            'magic': b'SMD0',
            'version': 1,
            'num_meshes': len(meshes),
            'num_materials': len(materials),
        }
        file.write(smd.Header.pack(
            magic=header['magic'],
            version=header['version'],
            num_meshes=header['num_meshes'],
            num_materials=header['num_materials'],
        ))
        for mesh in meshes:
            file.write(smd.Mesh.pack(
                name=mesh['name'],
                index=mesh['index'],
                num_verts=mesh['num_verts'],
                num_st=mesh['num_st'],
                num_normals=mesh['num_normals'],
            ))
            for vertex in mesh['vertices']:
                file.write(smd.Vertex.pack(*vertex))
            for normal in mesh['normals']:
                file.write(smd.Vertex.pack(*normal))
            for st in mesh['st']:
                file.write(smd.ST.pack(*st))

        for material in materials:
            file.write(smd.Material.pack(
                name=material['name'],
                spec_exp=material['spec_exp'],
                ambient=material['ambient'],
                diffuse=material['diffuse'],
                specular=material['specular'],
                diffuse_texture=material['diffuse_texture'],
                normal_texture=material['normal_texture'],
            ))


def save_old(context, filename, **kwargs):
    with open(filename, 'wb') as file:
        header = kwargs.get('header')
        file.write(smd.Header.pack(
            magic=header['magic'],
            version=header['version'],
            num_meshes=header['num_meshes'],
            num_materials=header['num_materials'],
        ))

        for mesh in kwargs.get('meshes'):
            file.write(smd.Mesh.pack(
                name=mesh['name'],
                index=mesh['index'],
                num_verts=mesh['num_verts'],
                num_st=mesh['num_st'],
                num_normals=mesh['num_normals'],
            ))
            for vertex in mesh['verts']:
                file.write(smd.Vertex.pack(
                    *vertex
                ))
            for st in mesh['st']:
                file.write(smd.ST.pack(
                    *st
                ))
            for normal in mesh['normals']:
                file.write(smd.Vertex.pack(
                    *normal
                ))

        for material in kwargs.get('materials'):
            file.write(smd.Material.pack(
                name=material['name'],
                spec_exp=material['spec_exp'],
                ambient=material['ambient'],
                diffuse=material['diffuse'],
                specular=material['specular'],
                diffuse_texture=material['diffuse_texture'],
                normal_texture=material['normal_texture'],
            ))


if __name__ == '__main__':
    args = {
        'header': {
            'magic': b'SMD0',
            'version': 1,
            'num_meshes': 1,
            'num_materials': 1
        },
        'meshes': [
            {
                'name': 'mesh-root',
                'index': 1,
                'num_verts': 4,
                'num_st': 4,
                'num_normals': 4,
                'verts': [(1.1, 1.1, 1.1), (1.1, 1.1, 1.1), (1.1, 1.1, 1.1), (1.1, 1.1, 1.1)],
                'st': [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)],
                'normals': [(0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)],
            }
        ],
        'materials': [
            {
                'name': 'material-root',
                'spec_exp': 0.5,
                'ambient': (0.5, 0.5, 0.5),
                'diffuse': (1.0, 1.0, 1.0),
                'specular': (0.1, 0.1, 0.1),
                'diffuse_texture': 'texture/material-root-diff.tga',
                'normal_texture': 'texture/material-root-bump.tga',
            }
        ]
    }
    # save({}, filename='E:/first.smd', **args)
