import bpy

def join_objects(object_names, new_name):
    """Une los objetos en un solo mesh y lo renombra."""
    if not object_names:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    
    valid_objects = [bpy.data.objects[name] for name in object_names if name in bpy.data.objects]

    for obj in valid_objects:
        if obj and obj.type == 'MESH':
            obj.select_set(True)

    if valid_objects:
        bpy.context.view_layer.objects.active = valid_objects[0]
        bpy.ops.object.join()

        joined_obj = bpy.context.active_object
        if joined_obj:
            joined_obj.name = new_name
            joined_obj.data.name = new_name
            return joined_obj.name  # Devuelve el nombre del nuevo objeto unido
    return None

def add_uv_map(obj_name):
    """Añade un UV Map si no tiene uno."""
    obj = bpy.data.objects.get(obj_name)
    if obj and obj.type == 'MESH':
        uv_layers = obj.data.uv_layers
        if len(uv_layers) == 0:
            uv_layers.new(name="UVMap")

def join_objects_by_prefix(object_names, prefix_map):
    """Une objetos en grupos según su prefijo."""
    
    processed_names = set()
    
    for prefix, new_name in prefix_map.items():
        objs_to_join = [name for name in object_names if name.startswith(prefix) and name not in processed_names]

        if objs_to_join:
            joined_name = join_objects(objs_to_join, new_name=new_name)
            if joined_name:
                processed_names.update(objs_to_join)
                processed_names.add(joined_name)

class OBJECT_OT_standard_settings(bpy.types.Operator):
    bl_idname = "object.standard_settings"
    bl_label = "Apply Standard Settings"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Une objetos con el mismo prefijo en la colección activa y aplica UV a 'R_Limit_Barrier'."

    def execute(self, context):
        active_collection = context.collection
        if not active_collection:
            self.report({'ERROR'}, "No hay una colección activa.")
            return {'CANCELLED'}

        # Obtener nombres de los objetos en la colección
        object_names = [obj.name for obj in active_collection.objects if obj.type == 'MESH' and obj.name in bpy.data.objects]

        # Definir los grupos de prefijos
        prefix_groups = {
            "R_LimitBD": "R_LimitBD",
            "R_WFame": "WallFame",
            "R_WOF_STOP": "WOF_STOPS",
            "R_Bus": "R_Bus",
            "R_Screen": "Billboards",
            "R_SB": "Special_BD",
            "R_Mini_Games": "Minigames",
            "R_Base_Streets":"R_Base_Streets"
        }

        # Unir objetos según prefijo
        join_objects_by_prefix(object_names, prefix_groups)

        # Unir edificios completos en "FullBuilding"
        full_building_prefixes = ["R_Ch", "R_Loc", "R_Pub", "R_Wall", "R_Build", "R_Apt", "R_Num"]
        full_building_objects = [name for name in object_names if any(name.startswith(prefix) for prefix in full_building_prefixes)]

        if full_building_objects:
            join_objects(full_building_objects, new_name="FullBuilding")

        # Aplicar UVMap a "R_Limit_Barrier"
        add_uv_map("R_Limit_Barrier")

        self.report({'INFO'}, f"Se aplicaron configuraciones a la colección '{active_collection.name}'.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_standard_settings)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_standard_settings)

if __name__ == "__main__":
    register()
