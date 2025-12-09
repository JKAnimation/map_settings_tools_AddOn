import bpy

class OBJECT_UL_custom_list(bpy.types.UIList):
    """UI List to manually add and reorder objects"""
    bl_idname = "OBJECT_UL_custom_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.object_ref
        if obj:
            layout.prop(obj, "name", text="", emboss=False, icon='OBJECT_DATAMODE')

class ObjectListItem(bpy.types.PropertyGroup):
    object_ref: bpy.props.PointerProperty(type=bpy.types.Object)

class OBJECT_OT_add_to_list(bpy.types.Operator):
    """Add selected object to the list"""
    bl_idname = "object.add_to_list"
    bl_label = "Add Selected Object to List"
    
    def execute(self, context):
        obj = context.view_layer.objects.active
        if not obj:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        item = context.scene.my_objects.add()
        item.object_ref = obj

        return {'FINISHED'}

class OBJECT_OT_remove_from_list(bpy.types.Operator):
    """Remove selected object from the list"""
    bl_idname = "object.remove_from_list"
    bl_label = "Remove Object from List"
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.my_objects) > 0
        
    def execute(self, context):
        index = context.scene.my_objects_index
        context.scene.my_objects.remove(index)
        context.scene.my_objects_index = min(max(0, index - 1), len(context.scene.my_objects) - 1)
        return {'FINISHED'}

class OBJECT_OT_move_item(bpy.types.Operator):
    """Move an item in the list"""
    bl_idname = "object.move_item"
    bl_label = "Move an item in the list"
    
    direction: bpy.props.EnumProperty(items=[('UP', 'Up', ''), ('DOWN', 'Down', '')])

    @classmethod
    def poll(cls, context):
        return len(context.scene.my_objects) > 1
    
    def execute(self, context):
        index = context.scene.my_objects_index
        if self.direction == 'UP' and index > 0:
            context.scene.my_objects.move(index, index - 1)
            context.scene.my_objects_index -= 1
        elif self.direction == 'DOWN' and index < len(context.scene.my_objects) - 1:
            context.scene.my_objects.move(index, index + 1)
            context.scene.my_objects_index += 1
        return {'FINISHED'}

class OBJECT_OT_apply_order(bpy.types.Operator):
    """Apply the order, duplicate, and rename objects in a new collection"""
    bl_idname = "object.apply_order"
    bl_label = "Apply Order, Duplicate, and Rename in New Collection"
    
    def execute(self, context):
        # Crear una nueva colección
        new_collection = bpy.data.collections.new("Duplicated_Objects")
        context.scene.collection.children.link(new_collection)
        
        objects_in_order = context.scene.my_objects

        for i, item in enumerate(objects_in_order):
            obj = item.object_ref
            
            # Crear una copia del objeto
            obj_copy = obj.copy()
            obj_copy.data = obj.data.copy() if obj.data else None
            new_collection.objects.link(obj_copy)
            
            # Renombrar el objeto basado en el orden
            new_name = f"{i:02d}.{obj.name}"
            obj_copy.name = new_name
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_UL_custom_list)
    bpy.utils.register_class(ObjectListItem)
    bpy.utils.register_class(OBJECT_OT_add_to_list)
    bpy.utils.register_class(OBJECT_OT_remove_from_list)
    bpy.utils.register_class(OBJECT_OT_move_item)
    bpy.utils.register_class(OBJECT_OT_apply_order)
    bpy.types.Scene.my_objects = bpy.props.CollectionProperty(type=ObjectListItem)
    bpy.types.Scene.my_objects_index = bpy.props.IntProperty()

def unregister():
    bpy.utils.unregister_class(OBJECT_UL_custom_list)
    bpy.utils.unregister_class(ObjectListItem)
    bpy.utils.unregister_class(OBJECT_OT_add_to_list)
    bpy.utils.unregister_class(OBJECT_OT_remove_from_list)
    bpy.utils.unregister_class(OBJECT_OT_move_item)
    bpy.utils.unregister_class(OBJECT_OT_apply_order)
    del bpy.types.Scene.my_objects
    del bpy.types.Scene.my_objects_index
