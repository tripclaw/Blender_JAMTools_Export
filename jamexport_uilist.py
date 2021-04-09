import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

# ############################################
#   Operators
# ############################################

class JAMEXPORT_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Add, remove and move export collection"
    bl_options = {'REGISTER'}

    # noinspection PyTypeChecker
    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
            ('EXPORT', "Export", ""))
    )

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.jam_export_sel_index

        try:
            item = scn.jam_export_collections[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.jam_export_collections) - 1:
                item_next = scn.jam_export_collections[idx+1].name
                scn.jam_export_collections.move(idx, idx+1)
                scn.jam_export_sel_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.jam_export_sel_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.jam_export_collections[idx-1].name
                scn.jam_export_collections.move(idx, idx-1)
                scn.jam_export_sel_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.jam_export_sel_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % item.name
                scn.jam_export_sel_index -= 1
                scn.jam_export_collections.remove(idx)
                self.report({'INFO'}, info)

            # elif self.action == 'EXPORT':
            #    info = 'Export "%s"' % item.name
            
                # Convert from Collection to LayerCollection type (to do: find a better way)
            #    layer_collection = bpy.context.view_layer.layer_collection.children[item.export_collection.name]
            #    bpy.context.view_layer.active_layer_collection = layer_collection
            
            #    bpy.ops.export.quick_fbx("INVOKE_DEFAULT", directory="[[DEFAULT]]")

            #    print(item.export_collection.name)
            #    self.report({'INFO'}, info)

        if self.action == 'ADD':
            act_coll = context.view_layer.active_layer_collection.collection
            if act_coll.name in [c[1].export_collection.name for c in scn.jam_export_collections.items()]:
                info = '"%s" already in the list. Change your active collection to add another.' % act_coll.name
            else:
                item = scn.jam_export_collections.add()
                item.export_layer_collection = context.view_layer.active_layer_collection
                item.export_collection = act_coll
                item.name = item.export_collection.name
                scn.jam_export_sel_index = (len(scn.jam_export_collections)-1)
                info = '%s added to list' % (item.name)

            self.report({'INFO'}, info)

        return {"FINISHED"}


class JAMEXPORT_OT_printItems(Operator):
    """Print all items and their properties to the console"""
    bl_idname = "custom.print_items"
    bl_label = "Debug Print"
    bl_description = "Print all items and their properties to the console"
    bl_options = {'REGISTER', 'UNDO'}

    reverse_order: BoolProperty(
        default=False,
        name="Reverse Order")

    @classmethod
    def poll(cls, context):
        return bool(context.scene.jam_export_collections)

    def execute(self, context):
        scn = context.scene
        print ("Collection Items")
        if self.reverse_order:
            for i in range(scn.jam_export_sel_index, -1, -1):        
                item = scn.jam_export_collections[i]
                print ("  ", item.export_collection.name)
        else:
            for item in scn.jam_export_collections:
                print ("  ", item.export_collection.name)
        return{'FINISHED'}


class JAMEXPORT_OT_clearList(Operator):
    """Remove all"""
    bl_idname = "custom.clear_list"
    bl_label = "Remove All"
    bl_description = "Clear all items from this scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.jam_export_collections)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.jam_export_collections):
            context.scene.jam_export_collections.clear()
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}


class JAMEXPORT_OT_removeDuplicates(Operator):
    """Remove all duplicates"""
    bl_idname = "custom.remove_duplicates"
    bl_label = "Remove Duplicates"
    bl_description = "Remove all duplicates"
    bl_options = {'INTERNAL'}

    def find_duplicates(self, context):
        """find all duplicates by name"""
        name_lookup = {}
        for c, i in enumerate(context.scene.jam_export_collections):
            print(i.name)
            name_lookup.setdefault(i.name, []).append(c)
        duplicates = set()
        for name, indices in name_lookup.items():
            for i in indices[1:]:
                duplicates.add(i)
        return sorted(list(duplicates))

    @classmethod
    def poll(cls, context):
        return bool(context.scene.jam_export_collections)

    def execute(self, context):
        scn = context.scene
        removed_items = []
        # Reverse the list before removing the items
        for i in self.find_duplicates(context)[::-1]:
            scn.jam_export_collections.remove(i)
            removed_items.append(i)
        if removed_items:
            scn.jam_export_sel_index = len(scn.jam_export_collections)-1
            info = ', '.join(map(str, removed_items))
            self.report({'INFO'}, "Removed indices: %s" % (info))
        else:
            self.report({'INFO'}, "No duplicates")
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class JAMEXPORT_OT_updateData(Operator):
    """Update data from .custom to .jam_tools_export_data"""
    bl_idname = "custom.jam_tools_update_data"
    bl_label = "Update data"
    bl_description = "Update data from .custom to .jam_tools_export_data"
    bl_options = {'INTERNAL'}

    def has_data(self, context):
        """Has data or not"""
        return hasattr(context.scene, "custom")

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene

        if hasattr(context.scene, "custom") and len(context.scene.custom) > 0 :
            
            old_item_count = len(context.scene.custom)
            
            for c in context.scene.custom:
                
                if c is None:
                    self.report({'INFO'}, "Item is NoneType... skipping")
                elif c.export_collection is None:
                    self.report({'INFO'}, "Item.export_collection is NoneType... skipping")
                else:
                    # context.scene.jam_export_collections.append(c)            
                    item = context.scene.jam_export_collections.add()
                    item.name = c.name
                    item.export_collection = c.export_collection
                    
            bpy.ops.custom.remove_duplicates()

            context.scene.custom.clear()

            self.report({'INFO'}, "Converted old custom data (" + str(old_item_count) + ")")
                 
        else:
            self.report({'INFO'}, "No old custom data found")

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



# ############################################
#   UI
# ############################################

class JAMEXPORT_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        is_selected = index == context.scene.jam_export_sel_index
        if is_selected:
            split_factor = 0.8
        else:
            split_factor = 1.0

        split = layout.split(factor=split_factor)
        item_icon = 'FILE_BLANK'
        layer_collection = bpy.context.view_layer.layer_collection.children[item.export_collection.name]

        is_active_collection = item.export_collection.name == bpy.context.view_layer.active_layer_collection.name
        if is_active_collection:
            item_icon = 'FILE'

        # if layer_collection == bpy.context.view_layer.active_layer_collection:
        #    item_icon = 'COLLECTION_NEW'
            #bpy.context.view_layer.active_layer_collection = layer_collection

        split.prop(item.export_collection, "name", text="", emboss=False, icon=item_icon)

        if is_selected: 
            export_op = split.operator("export.quick_fbx", text="", icon="EXPORT")
            export_op.directory = "[[DEFAULT]]"
            export_op.export_collection_name = item.export_collection.name

        # split.label(text="[%d]" % (index))
        
    def invoke(self, context, event):
        pass

class JAMEXPORT_PT_objectList(Panel):
    """Export Collections - A list of exported collections from this scene"""
    bl_label = "Export Collections"
    bl_category = "JAM"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("JAMEXPORT_UL_items", "", scn, "jam_export_collections", scn, "jam_export_sel_index", rows=rows)

        col = row.column(align=True)
        col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("custom.list_action", icon='TRASH', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        # row = layout.row()
        # col = row.column(align=True)
        # col.operator("custom.list_action", icon='EXPORT', text="EXPORT").action = 'EXPORT'
        box = layout.box()
        row = box.row()
        col = row.column(align=True)

        idx = max(min(scn.jam_export_sel_index, len(scn.jam_export_collections)-1), 0)

        # col.label(text=str(idx))
        
        if len(scn.jam_export_collections) > 0:
            item = scn.jam_export_collections[idx]    

            if item is not None and item.export_collection is not None:

                col.label(text=item.name + ".fbx", icon="FILE")
            
                col.separator()
        
                export_op = col.operator("export.quick_fbx", text="Export", icon="EXPORT")
                export_op.directory = "[[DEFAULT]]"
                export_op.export_collection_name = item.export_collection.name
            
        else:
            col.label(text=bpy.context.view_layer.active_layer_collection.name, icon="FILE")
        
            col.separator()
            col.operator("custom.list_action", icon='ADD', text="Add").action = 'ADD'


        # if len(scn.jam_export_collections) == 0 or bpy.context.view_layer.layer_collection.collection != item.export_collection:

        #    box = layout.box()
        #    row = box.row()
        #    col = row.column(align=True)   
                         
        #    col.label(text=bpy.context.view_layer.active_layer_collection.name, icon="FILE")
        #    col.separator()
        #    col.operator("custom.list_action", icon='ADD', text="Add").action = 'ADD'
        

        row = layout.row()
        col = row.column(align=True)

        if hasattr(scn, "custom") and len(context.scene.custom) > 0:
            col.operator("custom.jam_tools_update_data", icon='TRIA_RIGHT', text="Update old data")


        # row = layout.row()
        # row.label(text='Debug')
        # row = layout.row()
        # col = row.column(align=True)
        # row = col.row(align=True)
        # row.operator("custom.print_items", icon="LINENUMBERS_ON") #LINENUMBERS_OFF, ANIM
        # row.operator("custom.remove_duplicates", icon="GHOST_ENABLED")
        ## row = col.row(align=True)
        ## row.operator("custom.clear_list", icon="X")

    def index_update(self, context):
        scn = context.scene
        idx = scn.jam_export_sel_index    
        try:
            item = scn.jam_export_collections[idx]
        except IndexError:
            pass
        else:
            #if item.export_collection:
                # Convert from Collection to LayerCollection type (to do: find a better way)
                #layer_collection = bpy.context.view_layer.layer_collection.children[item.export_collection.name]
                #bpy.context.view_layer.active_layer_collection = layer_collection
            # print("List item index update: [%d]" % idx, self)
            pass
        
    # subscribe to collection changes
    # owner = object()
    # # subscribe_to = bpy.context.view_layer.active_layer_collection.path_resolve("name", False)
    # # subscribe_to = bpy.types.LayerObjects, "active" # <-- works!
    # subscribe_to = bpy.types.ViewLayer, "active_layer_collection"  # <-- does not work
    #
    # def msgbus_callback(*args):
    #     # Something changed! (1, 2, 3)
    #     print("Collection changed!---------------------------------------", args)
    #     scn = bpy.context.scene
    #     scn.jam_export_sel_index = -1
    #     for i, c in enumerate(scn.jam_export_collections, 0):
    #         print("{}. {}  vs  layer: {}".format(i, c.export_collection.name, bpy.context.view_layer.active_layer_collection.name))
    #         if c.export_collection.name == bpy.context.view_layer.active_layer_collection.name:
    #             scn.jam_export_sel_index = i
    #             print("c.index = {} {}".format(i, c.export_collection.name))
    #             layer_collection = bpy.context.view_layer.layer_collection.children[c.export_collection.name]
    #             bpy.context.view_layer.active_layer_collection = layer_collection
    # print ("Yyyyyyyyyyyy")
    # print(subscribe_to)
    # bpy.msgbus.subscribe_rna(key=subscribe_to, owner=owner, args=(1, 2, 3), notify=msgbus_callback)



# ############################################
#   Collection
# ############################################

class JAMEXPORT_objectCollection(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    # export_layer_collection: bpy.props.PointerProperty(name="LayerCollection", type=bpy.types.LayerCollection)
    export_collection: bpy.props.PointerProperty(name="Collection", type=bpy.types.Collection)
    # export_path: bpy.props.StringProperty(name="Export Path")

# ############################################
#   Register & Unregister
# ############################################

classes = (
    JAMEXPORT_OT_actions,
    JAMEXPORT_OT_printItems,
    JAMEXPORT_OT_clearList,
    JAMEXPORT_OT_removeDuplicates,
    JAMEXPORT_OT_updateData,
    JAMEXPORT_UL_items,
    JAMEXPORT_PT_objectList,
    JAMEXPORT_objectCollection,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties

    bpy.types.Scene.jam_export_collections = CollectionProperty(type=JAMEXPORT_objectCollection)
    
    bpy.types.Scene.jam_export_sel_index = IntProperty(update=JAMEXPORT_PT_objectList.index_update)

    # THIS IS OBSOLETE BUT USED FOR BACKWARDS COMPATABILITY TO UPDATE SCENES
    # TODO: Remove once all scenes are using new jam_export_collections 
    bpy.types.Scene.custom = CollectionProperty(type=JAMEXPORT_objectCollection)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.jam_export_collections
    del bpy.types.Scene.jam_export_sel_index

    # THIS IS OBSOLETE BUT USED FOR BACKWARDS COMPATABILITY TO UPDATE SCENES
    # TODO: Remove once all scenes are using new jam_export_collections 
    del bpy.types.Scene.custom


if __name__ == "__main__":
    register()
