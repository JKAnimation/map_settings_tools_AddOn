import bpy

# ===============================
# UI List y Property Group
# ===============================
class OBJECT_UL_custom_list(bpy.types.UIList):
    bl_idname = "OBJECT_UL_custom_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.object_ref
        if obj:
            layout.prop(obj, "name", text="", emboss=False, icon='OBJECT_DATAMODE')


class ObjectListItem(bpy.types.PropertyGroup):
    object_ref: bpy.props.PointerProperty(type=bpy.types.Object)


# ===============================
# Operadores
# ===============================
class OBJECT_OT_add_to_list(bpy.types.Operator):
    bl_idname = "object.add_to_list"
    bl_label = "Add Selected Object"
    
    def execute(self, context):
        obj = context.view_layer.objects.active
        if not obj:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        item = context.scene.my_objects.add()
        item.object_ref = obj
        context.scene.my_objects_index = len(context.scene.my_objects) - 1
        return {'FINISHED'}


class OBJECT_OT_remove_from_list(bpy.types.Operator):
    bl_idname = "object.remove_from_list"
    bl_label = "Remove Selected Object"
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.my_objects) > 0
        
    def execute(self, context):
        index = context.scene.my_objects_index
        context.scene.my_objects.remove(index)
        context.scene.my_objects_index = min(max(0, index - 1), len(context.scene.my_objects) - 1)
        return {'FINISHED'}


class OBJECT_OT_move_item(bpy.types.Operator):
    bl_idname = "object.move_item"
    bl_label = "Move Object"
    
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
    bl_idname = "object.apply_order"
    bl_label = "Apply Order & Duplicate"
    
    def execute(self, context):
        objects_in_order = context.scene.my_objects
        if not objects_in_order:
            self.report({'WARNING'}, "No objects in list")
            return {'CANCELLED'}

        new_collection = bpy.data.collections.new("Duplicated_Objects")
        context.scene.collection.children.link(new_collection)

        for i, item in enumerate(objects_in_order):
            obj = item.object_ref
            if not obj:
                continue
            obj_copy = obj.copy()
            obj_copy.data = obj.data.copy() if obj.data else None
            new_collection.objects.link(obj_copy)
            obj_copy.name = f"{i:02d}.{obj.name}"

        self.report({'INFO'}, "Objects duplicated and renamed in 'Duplicated_Objects'")
        return {'FINISHED'}


# ===============================
# Panel
# ===============================
class OBJECT_PT_custom_list_panel(bpy.types.Panel):
    bl_label = "Object Order Manager"
    bl_idname = "OBJECT_PT_custom_list_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # UI List
        row = layout.row()
        row.template_list(
            "OBJECT_UL_custom_list", "", 
            scene, "my_objects", 
            scene, "my_objects_index",
            rows=5
        )

        # Botones
        col = layout.column(align=True)
        col.operator("object.add_to_list", text="Add Selected")
        col.operator("object.remove_from_list", text="Remove Selected")
        
        row = layout.row(align=True)
        row.operator("object.move_item", text="Move Up").direction = 'UP'
        row.operator("object.move_item", text="Move Down").direction = 'DOWN'

        layout.separator()
        layout.operator("object.apply_order", text="Apply Order & Duplicate", icon='OUTLINER_OB_COLLECTION')


# ===============================
# Registro
# ===============================
classes = [
    OBJECT_UL_custom_list,
    ObjectListItem,
    OBJECT_OT_add_to_list,
    OBJECT_OT_remove_from_list,
    OBJECT_OT_move_item,
    OBJECT_OT_apply_order,
    OBJECT_PT_custom_list_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_objects = bpy.props.CollectionProperty(type=ObjectListItem)
    bpy.types.Scene.my_objects_index = bpy.props.IntProperty(default=0)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_objects
    del bpy.types.Scene.my_objects_index

if __name__ == "__main__":
    register()
