import bpy

class OBJECT_OT_apply_activecollection_sys(bpy.types.Operator):
    bl_idname = "object.apply_activecollection_sys"
    bl_label = "Split C-C"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convierte instancias en objetos reales de la colección activa en la colección destino"

    @classmethod
    def poll(cls, context):
        col = context.view_layer.active_layer_collection.collection
        return col and len(col.objects) > 0

    def execute(self, context):
        disable_realize_modifiers()

        exp_collection_name = context.scene.split_collection.name

        if exp_collection_name not in bpy.data.collections:
            exp_collection = bpy.data.collections.new(exp_collection_name)
            context.scene.collection.children.link(exp_collection)
        else:
            exp_collection = bpy.data.collections[exp_collection_name]

        active_collection = context.view_layer.active_layer_collection.collection

        for obj in list(active_collection.objects):
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            before = set(bpy.data.objects)

            try:
                bpy.ops.object.duplicates_make_real()
            except Exception as e:
                self.report({'WARNING'}, f"No se pudo hacer real {obj.name}: {e}")
                continue

            after = set(bpy.data.objects)
            new_objects = list(after - before)

            if not new_objects:
                new_objects = [obj]

            for new_obj in new_objects:
                if new_obj.name.startswith("_"):
                    continue
                if exp_collection not in new_obj.users_collection:
                    exp_collection.objects.link(new_obj)
                for col in list(new_obj.users_collection):
                    if col != exp_collection:
                        col.objects.unlink(new_obj)

            bpy.ops.object.select_all(action='DESELECT')

        enable_realize_modifiers()

        self.report({'INFO'}, f"Instancias convertidas y movidas a '{exp_collection_name}'.")
        return {'FINISHED'}


def disable_realize_modifiers():
    active_collection = bpy.context.view_layer.active_layer_collection.collection
    for obj in active_collection.objects:
        for mod in obj.modifiers:
            if mod.type == "NODES" and mod.node_group and mod.node_group.name == "Realize":
                mod.show_viewport = False
    bpy.context.view_layer.update()


def enable_realize_modifiers():
    active_collection = bpy.context.view_layer.active_layer_collection.collection
    for obj in active_collection.objects:
        for mod in obj.modifiers:
            if mod.type == "NODES" and mod.node_group and mod.node_group.name == "Realize":
                mod.show_viewport = True
    bpy.context.view_layer.update()


# --- REGISTRO UNIFICADO ---
classes = (
    OBJECT_OT_apply_activecollection_sys,
)
