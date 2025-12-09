import bpy

def join_objects(object_names, new_name):
    bpy.ops.object.select_all(action='DESELECT')
    valid_objects = [bpy.data.objects[name] for name in object_names if name in bpy.data.objects]

    for obj in valid_objects:
        obj.select_set(True)

    if valid_objects:
        bpy.context.view_layer.objects.active = valid_objects[0]
        bpy.ops.object.join()

        joined_obj = bpy.context.active_object
        if joined_obj:
            joined_obj.name = new_name
            joined_obj.data.name = new_name
            return joined_obj.name

    return None


def add_uv_map(obj_name):
    obj = bpy.data.objects.get(obj_name)
    if obj and obj.type == 'MESH':
        if len(obj.data.uv_layers) == 0:
            obj.data.uv_layers.new(name="UVMap")


def join_objects_by_prefix(object_names, prefix_map):
    processed = set()

    for prefix, new_name in prefix_map.items():
        objs = [name for name in object_names if name.startswith(prefix) and name not in processed]

        if objs:
            created = join_objects(objs, new_name)
            if created:
                processed.update(objs)
                processed.add(created)


class OBJECT_OT_standard_settings(bpy.types.Operator):
    bl_idname = "object.standard_settings"
    bl_label = "Apply Standard Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        col = context.collection

        if not col:
            self.report({'ERROR'}, "No hay colección activa.")
            return {'CANCELLED'}

        object_names = [obj.name for obj in col.objects if obj.type == 'MESH']

        prefix_groups = {
            "R_LimitBD": "R_LimitBD",
            "R_WFame": "WallFame",
            "R_WOF_STOP": "WOF_STOPS",
            "R_Bus": "R_Bus",
            "R_Screen": "Billboards",
            "R_SB": "Special_BD",
            "R_Mini_Games": "Minigames",
            "R_Base_Streets": "R_Base_Streets"
        }

        join_objects_by_prefix(object_names, prefix_groups)

        full_building_prefixes = ["R_Ch", "R_Loc", "R_Pub", "R_Wall", "R_Build", "R_Apt", "R_Num"]
        full_objects = [name for name in object_names if any(name.startswith(p) for p in full_building_prefixes)]

        if full_objects:
            join_objects(full_objects, "FullBuilding")

        add_uv_map("R_Limit_Barrier")

        return {'FINISHED'}
