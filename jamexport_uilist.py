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
    bl_idname = "jamexport.list_action"
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
            ('EXPORT', "Export", ""),
            ('SELECT_OBJECTS', "Select Objects", ""))
    )

    @classmethod
    def poll(cls, context):
        return len(context.scene.jam_export_collections) > 0

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
                if scn.jam_export_collections[idx].export_collection is not None:
                    scn.jam_export_collections[idx].export_collection.color_tag = 'NONE'
                scn.jam_export_sel_index -= 1
                scn.jam_export_collections.remove(idx)
                self.report({'INFO'}, info)

            elif self.action == 'SELECT_OBJECTS':
                info = 'Selecting "%s"' % item.name
                col = scn.jam_export_collections[idx].export_collection
                if col is not None:
                    
                    layer_collection = find_layer_collection(col.name)                    
                    
                    if layer_collection is not None:
                        
                        bpy.ops.object.select_all(action='DESELECT')
                        for obj in col.all_objects:
                            obj.select_set(True)

                        bpy.context.view_layer.active_layer_collection = layer_collection

        if self.action == 'ADD':

            bpy.ops.wm.call_menu(name=JAMEXPORT_MT_AddCollectionMenu.bl_idname)

            # ## Old way: Add current active collection
            # act_coll = context.view_layer.active_layer_collection.collection
            # if act_coll.name in [c[1].export_collection.name for c in scn.jam_export_collections.items()]:
            #    info = '"%s" already in the list. Change your active collection to add another.' % act_coll.name
            # else:
            #    item = scn.jam_export_collections.add()
            #    item.export_layer_collection = context.view_layer.active_layer_collection
            #    item.export_collection = act_coll
            #    item.name = item.export_collection.name
            #    scn.jam_export_sel_index = (len(scn.jam_export_collections)-1)
            #    info = '%s added to list' % (item.name)

            # self.report({'INFO'}, info)

        return {"FINISHED"}


class JAMEXPORT_OT_call_add_collection_menu(Operator):
    """Adds a collection to export list"""
    bl_idname = "jamexport.call_add_collection_menu"
    bl_label = "Add Collection..."
    bl_description = "Add Collection to list of exports"
    bl_options = {'REGISTER'}

    def execute(self, context):
       bpy.ops.wm.call_menu(name=JAMEXPORT_MT_AddCollectionMenu.bl_idname)
       return {'FINISHED'}

class JAMEXPORT_OT_add_collection(Operator):
    """Calls the Adds Collection menu"""
    bl_idname = "jamexport.add_collection"
    bl_label = "Add Collection"    
    bl_description = "Add..."
    bl_options = {'REGISTER'}

    # export_collection: bpy.props.PointerProperty(
    #    name="Export Collection",
    #    description="Collection to Export",
    #    type=bpy.types.Collection
    #)
    
    # collection passed as string for now, because I can't figure out how to pass a collection object at the moment...
    export_collection_name:  bpy.props.StringProperty(
        name="Export Collection",
        description="Collection to Export"
    )

    def invoke(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        scn = context.scene

        coll = bpy.context.scene.collection

        for c in traverse_tree(coll):

            # print(c.name)

            if c.name == self.export_collection_name:
                found = True
                act_coll = c
            
                if act_coll.name in [c[1].export_collection.name for c in scn.jam_export_collections.items()]:
                    info = '"%s" already in the list.' % act_coll.name
                    self.report({'INFO'}, info)
                else:
                    item = scn.jam_export_collections.add()
                    item.export_layer_collection = context.view_layer.active_layer_collection
                    item.export_collection = act_coll
                    act_coll.color_tag = 'COLOR_07'
                    item.name = item.export_collection.name
                    scn.jam_export_sel_index = (len(scn.jam_export_collections)-1)
                    info = '%s added to list' % (item.name)
                    self.report({'INFO'}, info)
                    break
                
        return {'FINISHED'}

class JAMEXPORT_OT_create_new_collection(Operator):
    """Creates a new collection and adds it to the export list"""
    bl_idname = "jamexport.new_collection"
    bl_label = "New Collection..."
    bl_description = "Creates a new collection and adds it to the list of exports"
    bl_options = {'REGISTER'}

    def execute(self, context):
        myCol = bpy.data.collections.new("New Collection")
        bpy.context.scene.collection.children.link(myCol)
        layer_collection = bpy.context.view_layer.layer_collection.children[myCol.name]
        bpy.ops.jamexport.add_collection(export_collection_name = myCol.name)
        # bpy.context.view_layer.active_layer_collection = layer_collection
        return {'FINISHED'}


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
    """Export Collections UIList Item"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        is_selected = index == context.scene.jam_export_sel_index
        is_active_collection = False
        item_name = "?"
        item_icon = "ERROR"
        
        if item.export_collection is not None:        
            item_name = item.export_collection.name
            is_active_collection = item_name == bpy.context.view_layer.active_layer_collection.name

            # if is_active_collection:
            #    split_factor = 0.8
            # else:
            #    split_factor = 1.0

            # split = layout.split(factor=split_factor)

            item_icon = 'OUTLINER_COLLECTION'

            layer_collection = find_layer_collection(item_name)

            if layer_collection is not None:

                # if is_active_collection:
                #    item_icon = 'OUTLINER_COLLECTION'

                if layer_collection.collection.color_tag != 'NONE':
                    item_icon = 'COLLECTION_' + layer_collection.collection.color_tag
        
        
            # if layer_collection == bpy.context.view_layer.active_layer_collection:
            #    item_icon = 'COLLECTION_NEW'
                #bpy.context.view_layer.active_layer_collection = layer_collection

            layout.prop(item.export_collection, "name", text="", emboss=False, icon=item_icon)
        
        else:
            
            layout.label(text="<Missing> " + item.name, icon="ERROR")

        # if is_selected: 
        #    export_op = split.operator("export.jam_quick_fbx", text="", icon="EXPORT")
        #    export_op.directory = "[[DEFAULT]]"
        #    export_op.export_collection_name = item.export_collection.name

        # if is_active_collection: 
        #    split.label(text="", icon="EXPORT")
    
        # split.label(text="[%d]" % (index))
        
    def invoke(self, context, event):
        pass

class JAMEXPORT_PT_objectList(Panel):
    """Export Collections - A list of exported collections from this scene"""
    bl_label = "Export Collections"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("JAMEXPORT_UL_items", "", scn, "jam_export_collections", scn, "jam_export_sel_index", rows=rows)

        col = row.column(align=True)
        col.operator("jamexport.call_add_collection_menu", icon='ADD', text="")
        col.separator()
        col.operator("jamexport.list_action", icon='TRASH', text="").action = 'REMOVE'
        col.separator()
        col.operator("jamexport.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("jamexport.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        col.separator()
        col.operator("jamexport.list_action", icon='RESTRICT_SELECT_OFF', text="").action = 'SELECT_OBJECTS'

        # row = layout.row()
        # col = row.column(align=True)
        # col.operator("custom.list_action", icon='EXPORT', text="EXPORT").action = 'EXPORT'
        box = layout.box()
        row = box.row()
        col = row.column(align=True)

        idx = max(min(scn.jam_export_sel_index, len(scn.jam_export_collections)-1), 0)

        # col.label(text=str(idx))
        
        if len(scn.jam_export_collections) > 0 and scn.jam_export_sel_index >= 0:
            item = scn.jam_export_collections[idx]    

            if item is not None and item.export_collection is not None:

                col.label(text=item.name + ".fbx", icon="FILE")
            
                col.separator()
        
                if len(item.export_collection.objects) == 0:
                    col.label(text="Empty collection", icon="ERROR")
                    col.enabled = False
                else:
                    export_op = col.operator("export.jam_quick_fbx", text="Export", icon="EXPORT")
                    export_op.directory = "[[DEFAULT]]"
                    export_op.export_collection_name = item.export_collection.name
            
        else:
            # col.label(text=bpy.context.view_layer.active_layer_collection.name, icon="FILE")
        
            col.separator()
            # col.operator("jamexport.list_action", icon='ADD', text="Add").action = 'ADD'


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
       
        
        col.separator()
        
        row = layout.row()    
    
        col = row.column(align=True)        
        if len(scn.jam_export_collections) > 0:
            export_all_op = col.operator("export.jam_quick_fbx_all", text="Export All", icon="EXPORT")



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
            # if item.export_collection:
                # Convert from Collection to LayerCollection type (to do: find a better way)
            #    layer_collection = bpy.context.view_layer.layer_collection.children[item.export_collection.name]
            #    bpy.context.view_layer.active_layer_collection = layer_collection
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
#   Menus
# ############################################

class JAMEXPORT_MT_AddCollectionMenu(bpy.types.Menu):
    bl_label = "Add Export Collection..."
    bl_idname = "OBJECT_MT_jam_add_export_collection"

    def draw(self, context):
        layout = self.layout

        # layout.label(text="Hello world!", icon='WORLD_DATA')

        scene_master_collection = bpy.context.scene.collection

        count = 0

        active_layer_collection = bpy.context.view_layer.active_layer_collection
        
        if active_layer_collection is not None:
            skip = False
            for it in context.scene.jam_export_collections:
                if it.export_collection.name == active_layer_collection.collection.name:
                    skip = True
                    break   
            if not skip:
                layout.operator("jamexport.add_collection", icon='OUTLINER_COLLECTION', text=active_layer_collection.collection.name).export_collection_name = active_layer_collection.collection.name
                layout.separator()
        
        for c in traverse_tree(scene_master_collection):

            skip = False

            if c is None:
                continue
            
            if c.name == "Master Collection":
                skip = True
            elif c.name == active_layer_collection.collection.name:
                skip = True
            else:
                for it in context.scene.jam_export_collections:
                    if it.export_collection.name == c.name:
                        skip = True                
            if not skip:
                layout.operator("jamexport.add_collection", icon='OUTLINER_COLLECTION', text=c.name).export_collection_name = c.name
                count += 1
    
        if count == 0:
            layout.label(text="Nothing else to add")
    
        layout.separator()
        
        layout.operator("jamexport.new_collection", icon='ADD', text='New Collection')
        # bpy.ops.outliner.collection_new(nested=True)
    
def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

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

# ############################################
#   Collection
# ############################################

class JAMEXPORT_objectCollection(PropertyGroup):
    export_collection: bpy.props.PointerProperty(name="Collection", type=bpy.types.Collection)

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
    JAMEXPORT_MT_AddCollectionMenu,
    JAMEXPORT_OT_add_collection,
    JAMEXPORT_OT_create_new_collection,
    JAMEXPORT_OT_call_add_collection_menu
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
