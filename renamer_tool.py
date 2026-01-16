import bpy
from bpy.types import PropertyGroup, Operator, UIList
from bpy.props import StringProperty, IntProperty, CollectionProperty, PointerProperty

class RenameItem(PropertyGroup):
    """Almacena el nombre actual y el nuevo nombre de un objeto"""
    old_name: StringProperty()  # Nombre actual (solo lectura)
    new_name: StringProperty()  # Nuevo nombre (editable)
    obj_ref: PointerProperty(type=bpy.types.Object)  # Referencia al objeto

class RENAMER_UL_items(UIList):
    """Muestra la lista de objetos a renombrar"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.old_name, icon='OBJECT_DATA')
        row.prop(item, "new_name", text="", emboss=True)

class RENAMER_OT_find_replace(Operator):
    """Buscar y reemplazar texto en los nombres de la lista"""
    bl_idname = "renamer.find_replace"
    bl_label = "Find & Replace"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        find = scene.renamer_find.strip()
        replace = scene.renamer_replace
        
        if not find:
            self.report({'WARNING'}, "No se especificó texto a buscar")
            return {'CANCELLED'}
            
        replaced = 0
        for item in scene.renamer_items:
            if find in item.new_name:
                item.new_name = item.new_name.replace(find, replace)
                replaced += 1
                
        self.report({'INFO'}, f"Reemplazado en {replaced} nombres")
        return {'FINISHED'}

class RENAMER_OT_autofill(Operator):
    """Auto-completar nombres con un prefijo y sufijo"""
    bl_idname = "renamer.autofill"
    bl_label = "Auto-fill Names"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        base_name = scene.renamer_base_name
        prefix = scene.renamer_prefix
        suffix = scene.renamer_suffix
        start_number = scene.renamer_start_number
        
        for i, item in enumerate(scene.renamer_items, start_number):
            current_base = base_name if base_name.strip() else item.old_name
            item.new_name = f"{prefix}{current_base}{suffix}"
            
            if len(scene.renamer_items) > 1:
                item.new_name = f"{prefix}{current_base}{suffix}_{i:03d}"
                
        return {'FINISHED'}

class RENAMER_OT_execute(Operator):
    """Aplicar los cambios de nombre"""
    bl_idname = "renamer.execute_rename"
    bl_label = "Apply Rename"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        renamed = 0
        
        for item in scene.renamer_items:
            if item.obj_ref and item.new_name and item.obj_ref.name != item.new_name:
                item.obj_ref.name = item.new_name
                if item.obj_ref.data:
                    item.obj_ref.data.name = item.new_name
                renamed += 1
                
        self.report({'INFO'}, f"Renombrados {renamed} objetos")
        return {'FINISHED'}

class RENAMER_OT_populate(Operator):
    """Llenar la lista con los objetos seleccionados"""
    bl_idname = "renamer.populate"
    bl_label = "Update Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        scene = context.scene
        if scene.renamer_clear_on_populate:
            scene.renamer_items.clear()
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':  # Solo agregar objetos de malla
                item = scene.renamer_items.add()
                item.old_name = obj.name
                item.new_name = obj.name
                item.obj_ref = obj
                
        self.report({'INFO'}, f"Agregados {len(scene.renamer_items)} objetos")
        return {'FINISHED'}

class RENAMER_OT_populate_from_collection(Operator):
    """Llenar la lista con objetos de una colección"""
    bl_idname = "renamer.populate_collection"
    bl_label = "Add from Collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    collection_name: StringProperty(name="Collection")
    
    @classmethod
    def poll(cls, context):
        return True  # Siempre permitir, verificaremos en execute
    
    def execute(self, context):
        scene = context.scene
        collection = bpy.data.collections.get(self.collection_name)
        
        if not collection:
            self.report({'WARNING'}, f"Colección no encontrada: {self.collection_name}")
            return {'CANCELLED'}
            
        if scene.renamer_clear_on_populate:
            scene.renamer_items.clear()
            
        added = 0
        for obj in collection.all_objects:
            if obj.type == 'MESH':  # Solo agregar objetos de malla
                item = scene.renamer_items.add()
                item.old_name = obj.name
                item.new_name = obj.name
                item.obj_ref = obj
                added += 1
                
        self.report({'INFO'}, f"Agregados {added} objetos de la colección")
        return {'FINISHED'}

class RENAMER_OT_move_item(Operator):
    """Mover un ítem en la lista"""
    bl_idname = "renamer.move_item"
    bl_label = "Move Item"
    bl_options = {'REGISTER', 'UNDO'}
    
    direction: bpy.props.EnumProperty(
        items=[
            ('UP', "Up", ""),
            ('DOWN', "Down", "")
        ]
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.renamer_items
    
    def execute(self, context):
        scene = context.scene
        index = scene.renamer_items_index
        list_length = len(scene.renamer_items) - 1
        
        new_index = index + (-1 if self.direction == 'UP' else 1)
        
        if 0 <= new_index <= list_length:
            scene.renamer_items.move(index, new_index)
            scene.renamer_items_index = new_index
            
        return {'FINISHED'}

class RENAMER_OT_apply_prefix_suffix(Operator):
    """Aplicar prefijo y sufijo a los nombres seleccionados"""
    bl_idname = "renamer.apply_prefix_suffix"
    bl_label = "Apply Prefix/Suffix"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        prefix = scene.renamer_prefix
        suffix = scene.renamer_suffix
        
        for item in scene.renamer_items:
            base_name = item.old_name
            if prefix and item.old_name.startswith(prefix):
                base_name = item.old_name[len(prefix):]
            if suffix and item.old_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                
            item.new_name = f"{prefix}{base_name}{suffix}"
            
        return {'FINISHED'}

# Lista de clases para registrar
classes = (
    RenameItem,
    RENAMER_UL_items,
    RENAMER_OT_find_replace,
    RENAMER_OT_autofill,
    RENAMER_OT_execute,
    RENAMER_OT_populate,
    RENAMER_OT_populate_from_collection,
    RENAMER_OT_move_item,
    RENAMER_OT_apply_prefix_suffix
)

# Propiedades
renamer_properties = {
    'renamer_items': bpy.props.CollectionProperty(type=RenameItem),
    'renamer_items_index': bpy.props.IntProperty(),
    'renamer_find': bpy.props.StringProperty(name="Find"),
    'renamer_replace': bpy.props.StringProperty(name="Replace"),
    'renamer_base_name': bpy.props.StringProperty(name="Base Name", default=""),
    'renamer_prefix': bpy.props.StringProperty(name="Prefix", default=""),
    'renamer_suffix': bpy.props.StringProperty(name="Suffix", default=""),
    'renamer_start_number': bpy.props.IntProperty(name="Start Number", default=1, min=0),
    'renamer_collection': bpy.props.StringProperty(name="Collection"),
    'renamer_clear_on_populate': bpy.props.BoolProperty(
        name="Clear List First", 
        default=True,
        description="Clear the list before populating with new items"
    )
}