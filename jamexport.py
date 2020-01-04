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
    file_path: bpy.props.StringProperty(name="Path",
                                        description="Path to export to",
                                        default="",
                                        maxlen=1024,
                                        subtype="DIR_PATH")

class JAMExport_PT_panel(bpy.types.Panel):
    bl_label = "JAM"
    bl_category = "JAM"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        export_data = context.scene.jam_export_data
        row.prop(export_data, "file_path")

        row = layout.row()

        export = layout.operator('export.quick_fbx', text='Export', icon='EXPORT')

        # preset_path = bpy.utils.preset_paths('operator/export_scene.fbx/')
        # print (preset_path)
        # presets = os.listdir(preset_path[0])
        # print (presets)

class JAMExport_Op(bpy.types.Operator):
    """Export fbx to saved path"""
    bl_idname = "export.quick_fbx"
    bl_label = "Export FBX to a stored path"

    #filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(
        name="Outdir Path",
        description="Where I will save my stuff"
        # subtype='DIR_PATH'
        )
    
    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):

        # TODO: Check if valid path

        if not os.path.exists(self.directory):
            self.report({'ERROR'}, 'Path does not exist: ' + self.directory)
            return {'CANCELLED'}

        context.scene.jam_export_data.file_path = self.directory

        full_filename = os.path.join(self.directory, bpy.context.view_layer.active_layer_collection.name + ".fbx")
        self.report({'INFO'}, 'Exporting to ' + full_filename)

        op = bpy.ops.export_scene.fbx('EXEC_DEFAULT',
            filepath = full_filename,
            check_existing = False, 
            use_selection = False,
            use_active_collection = True,
            bake_space_transform = True,
            object_types = {'ARMATURE', 'EMPTY', 'MESH', 'OTHER'},
            use_tspace = True,
            bake_anim = False
        )
        
        
        return {'FINISHED'}

    def invoke(self, context, event):
        
        export_data = context.scene.jam_export_data
        if not export_data.file_path:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.directory = export_data.file_path
            return self.execute(context)


def register():    
    bpy.utils.register_class(JAMExportSettings)
    bpy.utils.register_class(JAMExport_PT_panel)
    bpy.utils.register_class(JAMExport_Op)
    
    bpy.types.Scene.jam_export_data = bpy.props.PointerProperty(type=JAMExportSettings)


def unregister():
    bpy.utils.unregister_class(JAMExportSettings)
    bpy.utils.unregister_class(JAMExport_PT_panel)
    bpy.utils.unregister_class(JAMExport_Op)
    
    del bpy.types.Scene.jam_export_data

if __name__ == "__main__":
    register()