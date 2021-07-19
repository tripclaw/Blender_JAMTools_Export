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

class JAM_EXPORT_PT_panel(bpy.types.Panel):
    bl_label = "Export Settings"
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
        
        # sublayout = layout.box()    
        # sublayout.label(text='Active')

        # self.layout_item_box(context, sublayout, bpy.context.view_layer.active_layer_collection, True, True)

        # sublayout = layout.box()        
        # sublayout.label(text='Export Collections')

        # scn = context.scene
        # idx = scn.jam_export_sel_index
        # item = scn.jam_export_collections[idx]   

        # for c in scn.jam_export_collections:
        #    is_active_collection = c.export_collection.name == bpy.context.view_layer.active_layer_collection.name
        #    self.layout_item_box(context, sublayout, c.export_collection, is_active_collection, False)


    def layout_item_box(self, context, sublayout, collection, is_active_collection, show_export_button):

        if is_active_collection:
            sublayout = sublayout.box()

        file_icon='PLUS'
        allow_export = True;

        does_file_exist = False

        # check if file exists
        export_data = context.scene.jam_export_data
        if not export_data.file_path:
                file_icon = 'PLUS'                    
        else:
            abspath = bpy.path.abspath(export_data.file_path)
            full_filename = os.path.join(abspath, collection.name + ".fbx")
            if os.path.isfile(full_filename):
                file_icon = 'FILE' #CHECKMARK
                does_file_exist  = True  
            else:
                file_icon = 'PLUS' #'FILE_NEW'   

        if bpy.context.view_layer.active_layer_collection.name == 'Master Collection': 
                file_icon = 'CANCEL'
                does_file_exist  = False  
                allow_export = False;

        row = sublayout.row()

        status_icon = 'DECORATE_ANIMATE'
        
        # if is_active_collection:
        #    status_icon = 'KEYTYPE_MOVING_HOLD_VEC'
        collection_name = collection.name
        
        if does_file_exist:
            status_icon = 'DECORATE_KEYFRAME'
            collection_name = collection.name + ".fbx"
        
        row.label(text='', icon=status_icon)
                  
        if is_active_collection:
            if not show_export_button:
                op = row.operator('collection.set_active_collection', text=collection_name)        
                export = row.operator('export.quick_fbx', text='', icon='EXPORT')
                export.directory = "[[DEFAULT]]"
                # sel_box = row.box();
#               # row.heading
                # row.split(factor=0.0, align=False)
                # row.label(text=collection_name)                
                # row.enabled = False
            else:
                row.label(text=collection_name) # icon=file_icon
        else:
            op = row.operator('collection.set_active_collection', text=collection_name)        
            op.collection_name = collection.name
            # op.collection_to_activate = collection


        if show_export_button:

            row = sublayout.row()

            if not does_file_exist and is_active_collection:
                export = row.operator('export.quick_fbx', text='New Export', icon='FILE_NEW')
                export.directory = "[[DEFAULT]]"
                
                if not allow_export: 
                    row.enabled = False # gray out export if on Master Collection (root scene collection)
                
            if does_file_exist and is_active_collection:
                export = row.operator('export.quick_fbx', text='Export', icon='EXPORT')        
                export.directory = "[[DEFAULT]]"
                
                if not allow_export: 
                    row.enabled = False # gray out export if on Master Collection (root scene collection)


class JAM_EXPORT_OT_export(bpy.types.Operator):
    """Export fbx to saved path"""
    bl_idname = "export.quick_fbx"
    bl_label = "Export FBX to a stored path (JAM Tools)"

    directory: bpy.props.StringProperty(
        name="Export Path",
        description="Path to Export To (Relative or Absolute)"
        # subtype='DIR_PATH'
        )

    # export_collection = bpy.props.PointerProperty(
    #    name="Export Collection",
    #    description="Collection to Export",
    #    type=bpy.types.Collection
    # subtype='DIR_PATH'

    export_collection_name:  bpy.props.StringProperty(
        name="Export Collection",
        description="Collection to Export"
    )
    
    @classmethod
    def poll(cls, context):
        # TO DO: Don't allow exporting from Scene Collection (root collection)
        # layer_collection = bpy.context.view_layer.layer_collection.children[self.export_collection_name]
        #active_col = context.view_layer.active_layer_collection
        # active_col = layer_collection
        # if active_col is None:
        #    return False
        # if len(active_col.collection.objects) == 0:
        #    return False
        # export_collection_name
        if bpy.context.scene.jam_export_sel_index == -1:
            return False

        return True
        # return context.object is not None

    def execute(self, context):

        abspath = bpy.path.abspath(self.directory)

        if not os.path.exists(abspath):
            self.report({'ERROR'}, 'Path does not exist: ' + abspath)
            return {'CANCELLED'}

        context.scene.jam_export_data.file_path = self.directory

        # Change active collection to export_collection propertiy  
        # TODO: Make default to active collection if none was given

        layer_collection = find_layer_collection(self.export_collection_name)
        
        if layer_collection is None:
        # if self.export_collection_name not in bpy.context.view_layer.layer_collection.children :
            self.report({'ERROR'}, 'Did not export. Could not find collection named ' + self.export_collection_name)
            return {'FINISHED'}
            
        # layer_collection = bpy.context.view_layer.layer_collection.children[self.export_collection_name]
        bpy.context.view_layer.active_layer_collection = layer_collection

        full_filename = os.path.join(abspath, bpy.context.view_layer.active_layer_collection.name + ".fbx")
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
            # print ("using default export")
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
        
        scn = context.scene
        idx = scn.jam_export_sel_index
        item = scn.jam_export_collections[idx]        
        try:
            item = scn.jam_export_collections[idx]
        except IndexError:
            pass
        else:
            act_coll = context.view_layer.active_layer_collection.collection
            if act_coll.name in [c[1].export_collection.name for c in scn.jam_export_collections.items()]:
                info = '"%s" already in the list' % (act_coll.name)
            else:
                item = scn.jam_export_collections.add()
                item.export_collection = act_coll
                item.name = item.export_collection.name
                scn.jam_export_sel_index = (len(scn.jam_export_collections)-1)
                info = '%s added to list' % (item.name)

            # self.report({'INFO'}, info)        
        # row.label(text=str(bpy.types.Scene.jam_export_sel_index))
        
        
        
        
        return {'FINISHED'}

    def invoke(self, context, event):
        
        print("---- Export! ----")
        
        export_data = context.scene.jam_export_data
        if not export_data.file_path:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            # print(self.directory)
            if self.directory == '[[DEFAULT]]':
                self.directory = export_data.file_path
                # print('using export_data.file_path')
                # print(export_data.file_path)
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


class JAMExport_SetActiveCollection(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "collection.set_active_collection"
    bl_label = "Set Active Collection"

    collection_name : bpy.props.StringProperty(
        name="Collection to Activate",
        description="..."
        )        

    # can't get this to work...
    # collection_to_activate : bpy.props.CollectionProperty(
    #    name="Collection to Activate",
    #    description="...",e
    #    type=bpy.types.LayerCollection
    #    )        
        
    def execute(self, context):
        # scene_collection = bpy.context.view_layer.layer_collection
        #bpy.context.view_layer.active_layer_collection = self.collection_to_activate
        coll = bpy.data.collections.get(self.collection_name)

        if coll:
            layer_collection = bpy.context.view_layer.layer_collection.children[coll.name]
            bpy.context.view_layer.active_layer_collection = layer_collection

        return {'FINISHED'}

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
    # print("get_fbx_presets: Refreshing project list " + str(len(presets)))
    
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


def get_all_layer_collections(layer_collection):
    for col in layer_collection.children:
        yield col
        yield from get_all_layer_collections(col)

def find_layer_collection(layer_collection_name):
    collections = get_all_layer_collections(bpy.context.view_layer.layer_collection)
    for col in collections:
        if col.name == layer_collection_name:
            return col
    return None    
    

def register():    
    bpy.utils.register_class(JAMExportSettings)
    bpy.utils.register_class(JAM_EXPORT_PT_panel)
    bpy.utils.register_class(JAM_EXPORT_OT_export)
    bpy.utils.register_class(JAMExport_SetActiveCollection)

    bpy.types.Scene.jam_export_data = bpy.props.PointerProperty(type=JAMExportSettings)


    # presets
    FBX_Presets_List = get_fbx_presets()
    bpy.types.Scene.FBX_Preset = EnumProperty(items=FBX_Presets_List, update=preset_changed, name="Preset")
    bpy.utils.register_class(JAMExport_RefreshPresets)



def unregister():
    bpy.utils.unregister_class(JAMExportSettings)
    bpy.utils.unregister_class(JAM_EXPORT_PT_panel)
    bpy.utils.unregister_class(JAM_EXPORT_OT_export)
    bpy.utils.unregister_class(JAMExport_SetActiveCollection)
    
    del bpy.types.Scene.jam_export_data

    # presets
    bpy.utils.unregister_class(JAMExport_RefreshPresets)
    del bpy.types.Scene.FBX_Preset


if __name__ == "__main__":
    register()