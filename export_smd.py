from . import smd
import bpy


def get_scene_mesh_objects(prop=None):
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            yield obj if not prop else getattr(obj, prop)


def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def get_mesh_data():
    from bpy_extras import node_shader_utils
    mesh_data = []
    materials = []
    def get_tex_path(mat_wrap, key):
        tex_wrap = getattr(mat_wrap, key, None)
        if tex_wrap is None:
            return None
        image = tex_wrap.image
        if image is None:
            return None
        return image
    for mesh_object in get_scene_mesh_objects():
        data = {
            'name': mesh_object.name,
            'num_verts': 0,
            'num_st': 0,
            'num_normals': 0,
            'vertices': [],
            'st': [],
            'normals': [],
        }
        m = mesh_object.to_mesh()
        mesh_triangulate(m)
        list_of_indexes = [[v for v in p.vertices[:]] for p in m.polygons]
        list_of_indexes = [item for sublist in list_of_indexes for item in sublist]
        data['vertices'] = [m.vertices[i].co[:] for i in list_of_indexes]
        uv_layer = m.uv_layers.active.data[:]
        data['st'] = [layer.uv[:] for layer in uv_layer]
        data['normals'] = [m.vertices[i].normal[:] for i in list_of_indexes]
        data['num_verts'] = len(data['vertices'])
        data['num_st'] = len(data['st'])
        data['num_normals'] = len(data['normals'])
        mesh_data.append(data)
        mat = node_shader_utils.PrincipledBSDFWrapper(m.materials[0])
        mat_data = {
            'name': m.materials[0].name,
            'spec_exp': mat.roughness,
            'ambient': (1.0, 1.0, 1.0),
            'diffuse': mat.base_color[:3],
            'specular': (mat.specular, mat.specular, mat.specular),
            'diffuse_texture': get_tex_path(mat, 'base_color_texture') or '',
            'normal_texture': get_tex_path(mat, 'normalmap_texture') or '',
        }
        materials.append(mat_data)
        mesh_data[-1]['index'] = len(materials)
    return mesh_data, materials


def save(context, **kwargs):
    print(kwargs)
    meshes, materials = get_mesh_data()
    with open(kwargs.get('filename', 'E:\\first.smd'), 'wb') as file:
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
