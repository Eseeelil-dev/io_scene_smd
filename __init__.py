bl_info = {
    "name": "Static model (.smd)",
    "author": "Universe",
    "version": (0, 0, 1),
    "blender": (2, 81, 6),
    "location": "File > Import-Export",
    "description": "Import-Export Static model (.smd)",
    "warning": "",
    "doc_url": "{BLENDER_MANUAL_URL}",
    "support": 'TESTING',
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, FloatProperty
from bpy_extras.io_utils import ExportHelper, path_reference_mode, orientation_helper, axis_conversion


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportSMD(bpy.types.Operator, ExportHelper):
    """Save Static model (.smd) file"""

    bl_idname = "export_scene.smd"
    bl_label = "Export SMD"
    bl_options = {'PRESET'}

    filename_ext = ".smd"
    filter_glob: StringProperty(default="*.smd", options={'HIDDEN'})

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
    )

    path_mode: path_reference_mode

    def execute(self, context):
        import importlib
        from . import export_smd
        importlib.reload(export_smd)
        from mathutils import Matrix

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob"))

        global_matrix = (Matrix.Scale(self.global_scale, 4) @
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix
        export_smd.save(context, **keywords)
        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportSMD.bl_idname, text="Static model (.smd)")


def register():
    bpy.utils.register_class(ExportSMD)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSMD)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
