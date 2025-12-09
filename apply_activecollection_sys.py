import bpy

class OBJECT_OT_apply_activecollection_sys(bpy.types.Operator):
    bl_idname = "object.apply_activecollection_sys"
    bl_label = "Split C-C"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convierte instancias en objetos reales de la colección activa en la colección objetivo"

    @classmethod
    def poll(cls, context):
        # Verificar si la colección activa tiene objetos
        layer_col = context.view_layer.active_layer_collection
        return layer_col and layer_col.collection.objects

    def execute(self, context):
        # Desactivar modificadores Realize
        disable_realize_modifiers()

        # Nombre de la colección donde se guardarán las instancias reales
        exp_collection_name = context.scene.split_collection.name

        # Crear o obtener la colección de destino
        if exp_collection_name not in bpy.data.collections:
            exp_collection = bpy.data.collections.new(exp_collection_name)
            context.scene.collection.children.link(exp_collection)
        else:
            exp_collection = bpy.data.collections[exp_collection_name]

        # Obtener colección activa
        active_collection = context.view_layer.active_layer_collection.collection

        # Procesar cada objeto
        for obj in active_collection.objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Convertir instancias a objetos reales
            bpy.ops.object.duplicates_make_real()

            # Objetos generados = seleccionados tras duplicates_make_real()
            generated_objects = context.selected_objects

            for new_obj in generated_objects:
                if not new_obj.name.startswith("_"):
                    exp_collection.objects.link(new_obj)
                    active_collection.objects.unlink(new_obj)
                    self.report({'INFO'}, f"Objeto {new_obj.name} movido a {exp_collection_name}")

            bpy.ops.object.select_all(action='DESELECT')

        # Reactivar modificadores Realize
        enable_realize_modifiers()

        self.report({'INFO'}, "Instancias convertidas y movidas correctamente.")
        return {'FINISHED'}


# --------------------------
# Funciones auxiliares
# --------------------------

def disable_realize_modifiers():
    active_collection = bpy.context.view_layer.active_layer_collection.collection

    for obj in active_collection.objects:
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                mod.show_viewport = False
                print(f"[INFO] Realize desactivado en {obj.name}")

    bpy.context.view_layer.update()


def enable_realize_modifiers():
    active_collection = bpy.context.view_layer.active_layer_collection.collection

    for obj in active_collection.objects:
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                mod.show_viewport = True
                print(f"[INFO] Realize activado en {obj.name}")

    bpy.context.view_layer.update()
