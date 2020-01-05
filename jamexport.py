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
from bpy.types import Panel, Operator
from bpy.props import EnumProperty

FBX_Presets_List = {}

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
        row.prop(context.scene, "FBX_Preset")

        layout.label(text=bpy.context.view_layer.active_layer_collection.name + ".fbx")

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
        # TO DO: Don't allow exporting from Scene Collection (root collection)
        return context.view_layer.active_layer_collection is not None
        # return context.object is not None

    def execute(self, context):

        if not os.path.exists(self.directory):
            self.report({'ERROR'}, 'Path does not exist: ' + self.directory)
            return {'CANCELLED'}

        context.scene.jam_export_data.file_path = self.directory

        full_filename = os.path.join(self.directory, bpy.context.view_layer.active_layer_collection.name + ".fbx")
        print('Preset: ' + context.scene.FBX_Preset)

        if context.scene.FBX_Preset.lower() != '(none)':
            args = self.getpreset(context.scene.FBX_Preset)
            print("----- args: ------")
            print(args)
        else:
            args = []
            print ("not using preset")
        #print('preset: ' + FBX_Presets_List[context.scene.FBX_Preset])
        #print("preset: " +  context.scene.FBX_Preset)
        
        if not args:
            print ("using default export")
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
        else:
            op = bpy.ops.export_scene.fbx('EXEC_DEFAULT', 
                filepath = full_filename, 
                use_selection = False,
                use_active_collection = True,
                **args # arguments from preset
                )            
        
        self.report({'INFO'}, 'Exported to ' + full_filename)
        
        return {'FINISHED'}

    def invoke(self, context, event):
        
        print("---- Export! ----")
        
        export_data = context.scene.jam_export_data
        if not export_data.file_path:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.directory = export_data.file_path
            return self.execute(context)

    def getpreset(self, preset):
        filename = "_".join(s.lower() for s in preset.split())
        preset_path = bpy.utils.preset_paths('operator\\export_scene.fbx\\')
        
        print("preset path[0]: " + preset_path[0])
        if preset_path:
            filepath = bpy.utils.preset_find(filename, 'operator\\export_scene.fbx\\')
            if filepath:
                class Container(object):
                    __slots__ = ('__dict__',)

                op = Container()
                file = open(filepath, 'r')

                for line in file.readlines()[3::]:
                    exec(line, globals(), locals())
                
                args = op.__dict__
                
                # remove unneeded entries (will override)
                if 'filepath' in args:
                    del args['filepath']
                if 'ui_tab' in args:
                    del args['ui_tab']
                if 'use_selection' in args:
                    del args['use_selection'];
                if 'use_active_collection' in args:
                    del args['use_active_collection'];
                return args
            else:
                print ('Preset doesn\'t exist: ' + preset)
            #else:
                #raise FileNotFoundError(preset_path[0] + preset + '.py')
        else:
            print ("error: preset path no good")

# Presets: 
class JAMExport_RefreshPresets(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.refresh_export_presets"
    bl_label = "Refresh"
    
    def execute(self, context):
        FBX_Presets_List = get_fbx_presets()
        return {'FINISHED'}
    
def get_fbx_presets():
    preset_path = bpy.utils.preset_paths('operator/export_scene.fbx/')
    presets = os.listdir(preset_path[0])
    print("get_fbx_presets: Refreshing project list " + str(len(presets)))
    
    # TODO: Ensure first key is unique, e.g. no duplicates or preset named '(None)'
    p = []
    p.append(('(None)', '(None)', 'Use default settings provided by JAMExport'))    
    for x in range(len(presets)):
        if (presets[x].endswith('.py')):
            p.append((removeEnding(presets[x], '.py'), removeEnding(presets[x], '.py'), presets[x]))
    return p;   

def preset_changed(self, context):
    print ("preset changed to " + context.scene.FBX_Preset)
    

def removeEnding(thestring, ending):
  if thestring.endswith(ending):
    return thestring[:-len(ending)]
  return thestring



def register():    
    bpy.utils.register_class(JAMExportSettings)
    bpy.utils.register_class(JAMExport_PT_panel)
    bpy.utils.register_class(JAMExport_Op)

    bpy.types.Scene.jam_export_data = bpy.props.PointerProperty(type=JAMExportSettings)

    # presets
    FBX_Presets_List = get_fbx_presets()
    bpy.types.Scene.FBX_Preset = EnumProperty(items=FBX_Presets_List, update=preset_changed, name="Preset")
    bpy.utils.register_class(JAMExport_RefreshPresets)



def unregister():
    bpy.utils.unregister_class(JAMExportSettings)
    bpy.utils.unregister_class(JAMExport_PT_panel)
    bpy.utils.unregister_class(JAMExport_Op)
    
    del bpy.types.Scene.jam_export_data

    # presets
    bpy.utils.unregister_class(RefreshPresets)
    del bpy.types.Scene.FBX_Preset


if __name__ == "__main__":
    register()