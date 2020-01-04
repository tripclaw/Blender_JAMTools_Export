#bl_info = {
#    "name": "JAM Tools",
#    "category": "Mesh",
#    "author": "JAM",
#    "description": "export",
#    "version": (0, 1),
#    "location": "Side Panel",
#    "blender": (2, 80, 0),
#    "tracker_url": "",
#    "wiki_url": "" ,
#}

import bpy
import os

class JAMExportSettings(bpy.types.PropertyGroup):
    file_path: bpy.props.StringProperty(name="File path",
                                        description="File path to export to",
                                        default="",
                                        maxlen=1024,
                                        subtype="FILE_PATH")

class JAMExport_PT_panel(bpy.types.Panel):
    bl_label = "JAM"
    bl_category = "JAM"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        export_prop = context.scene.jam_export
        row.prop(export_prop, "file_path")

        row = layout.row()
        export = layout.operator('export_scene.fbx', text='Export', icon='EXPORT')
        export.filepath = export_prop.file_path + bpy.context.view_layer.active_layer_collection.name
        # default settings
        export.use_selection = False
        export.use_active_collection = True
        export.bake_space_transform = True
        export.object_types = {'ARMATURE', 'EMPTY', 'MESH', 'OTHER'}
        export.use_tspace = True
        export.bake_anim = False        

        # preset_path = bpy.utils.preset_paths('operator/export_scene.fbx/')
        # print (preset_path)
        # presets = os.listdir(preset_path[0])
        # print (presets)


def register():    
    bpy.utils.register_class(JAMExportSettings)
    bpy.utils.register_class(JAMExport_PT_panel)
    
    bpy.types.Scene.jam_export = bpy.props.PointerProperty(type=JAMExportSettings)


def unregister():
    bpy.utils.unregister_class(JAMExportSettings)
    bpy.utils.unregister_class(JAMExport_PT_panel)
    
    del bpy.types.Scene.jam_export

if __name__ == "__main__":
    register()