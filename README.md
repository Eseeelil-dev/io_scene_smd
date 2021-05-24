# smd file format specification

## version 1

SMD:

| Datatype | Name              | Description                    |
|----------|-------------------|--------------------------------|
| S32      | identifier        | Magic number "SMD0" 0x534D4430 |
| S32      | version           | SMD version number             |
| S32      | num_meshes        | Number of meshes               |
| S32      | num_materials     | Number of materials            |
| !        | (SMD_MESH)-es     | Array of smd meshes            |
| !        | (SMD_MATERIAL)-es | Array of smd materials         |


SMD_MESH:

| Datatype              | Name           | Description                    |
|-----------------------|----------------|--------------------------------|
| U8 * 64               | name           | Mesh name                      |
| S32                   | material_index | Index of material in this file |
| S32                   | num_vertices   | Number of vertices             |
| S32                   | num_normals    | Number of normals              |
| S32                   | num_tex_coords | Number of texture coordinates  |
| VEC3 * num_vertices   | vertices       | Vertices data                  |
| VEC3 * num_normals    | normals        | Normals data                   |
| VEC3 * num_tex_coords | tex_coords     | Texture coordinates data       |


SMD_MATERIAL:

| Datatype | Name            | Description            |
|----------|-----------------|------------------------|
| U8 * 64  | name            | Material name          |
| F32      | spec_exp        | Specular exponent      |
| VEC3     | ambient         | Ambient color          |
| VEC3     | diffuse         | Diffuse color          |
| VEC3     | specular        | Specular color         |
| U8 * 64  | diffuse_texture | Diffuse texture        |
| U8 * 64  | normal_texture  | Normal or bump texture |
