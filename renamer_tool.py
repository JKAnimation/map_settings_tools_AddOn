import bpy
from bpy.types import PropertyGroup, UIList, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty, PointerProperty, CollectionProperty

class RenamerItem(PropertyGroup):
    obj_ref: PointerProperty(type=bpy.types.Object)
    old_name: StringProperty()
    new_name: StringProperty()

class RENAMER_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "obj_ref", text="", emboss=False, icon='OBJECT_DATA')
            row.prop(item, "new_name", text="", emboss=True)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OBJECT_DATA')

class RENAMER_OT_populate(Operator):
    bl_idname = "renamer.populate"
    bl_label = "Populate List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if scene.renamer_clear_on_populate:
            scene.renamer_items.clear()
        
        for obj in context.selected_objects:
            item = scene.renamer_items.add()
            item.obj_ref = obj
            item.old_name = obj.name
            item.new_name = obj.name
        return {'FINISHED'}

class RENAMER_OT_clear(Operator):
    bl_idname = "renamer.clear"
    bl_label = "Clear List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.renamer_items.clear()
        return {'FINISHED'}

class RENAMER_OT_find_replace(Operator):
    bl_idname = "renamer.find_replace"
    bl_label = "Find & Replace"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        find = scene.renamer_find
        replace = scene.renamer_replace
        
        if not find:
            return {'CANCELLED'}
            
        for item in scene.renamer_items:
            if item.obj_ref:
                item.new_name = item.obj_ref.name.replace(find, replace)
        return {'FINISHED'}

class RENAMER_OT_apply_prefix_suffix(Operator):
    bl_idname = "renamer.apply_prefix_suffix"
    bl_label = "Apply Prefix/Suffix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        for item in scene.renamer_items:
            if not item.obj_ref:
                continue
                
            name = item.obj_ref.name
            if scene.renamer_preserve_base and '_' in name:
                base = name.split('_')[-1]
            else:
                base = name
                
            new_name = f"{scene.renamer_prefix}{'_' if scene.renamer_auto_underscore and scene.renamer_prefix else ''}"
            new_name += f"{base}"
            new_name += f"{'_' if scene.renamer_auto_underscore and scene.renamer_suffix else ''}{scene.renamer_suffix}"
            item.new_name = new_name
        return {'FINISHED'}

class RENAMER_OT_autofill(Operator):
    bl_idname = "renamer.autofill"
    bl_label = "Auto-fill Names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        base_name = scene.renamer_base_name
        start_num = scene.renamer_start_number
        padding = scene.renamer_zero_padding
        
        for i, item in enumerate(scene.renamer_items, start=start_num):
            item.new_name = f"{base_name}{i:0{padding}d}"
            
        return {'FINISHED'}

class RENAMER_OT_execute(Operator):
    bl_idname = "renamer.execute"
    bl_label = "Apply Rename"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        renamed = 0
        
        for item in scene.renamer_items:
            if item.obj_ref and item.new_name and item.obj_ref.name != item.new_name:
                # Make sure the object is in the current view layer
                if item.obj_ref.name not in context.view_layer.objects:
                    context.view_layer.active_layer_collection.collection.objects.link(item.obj_ref)
                
                # Rename the object and its data
                item.obj_ref.name = item.new_name
                if hasattr(item.obj_ref, 'data') and item.obj_ref.data:
                    item.obj_ref.data.name = item.new_name
                renamed += 1
                
        self.report({'INFO'}, f"Renamed {renamed} objects")
        return {'FINISHED'}

class RENAMER_OT_move_item(Operator):
    bl_idname = "renamer.move_item"
    bl_label = "Move Item"
    bl_options = {'REGISTER', 'UNDO'}
    
    direction: bpy.props.EnumProperty(
        items=[
            ('UP', "Up", "Move item up"),
            ('DOWN', "Down", "Move item down")
        ]
    )
    
    def execute(self, context):
        scene = context.scene
        idx = scene.renamer_active_index
        items = scene.renamer_items
        item_count = len(items)
        
        if self.direction == 'UP':
            next_idx = idx - 1
        else:
            next_idx = idx + 1
            
        if 0 <= next_idx < item_count:
            items.move(idx, next_idx)
            scene.renamer_active_index = next_idx
            
        return {'FINISHED'}

# Solo exportamos las clases, sin funciones de registro
classes = (
    RenamerItem,
    RENAMER_UL_items,
    RENAMER_OT_populate,
    RENAMER_OT_clear,
    RENAMER_OT_find_replace,
    RENAMER_OT_apply_prefix_suffix,
    RENAMER_OT_autofill,
    RENAMER_OT_execute,
    RENAMER_OT_move_item
)