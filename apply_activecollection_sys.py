import bpy

class OBJECT_OT_apply_activecollection_sys(bpy.types.Operator):
    bl_idname = "object.apply_activecollection_sys"
    bl_label = "Split C-C"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convierte instancias en objetos reales de la colección activa en la colección objetivo"

    @classmethod
    def poll(cls, context):
        # Verificar si la colección activa tiene objetos
        return context.view_layer.active_layer_collection.collection.objects

    def execute(self, context):
        # Desactivar el modificador "Realize Instances"
        disable_realize_modifiers()

        # Nombre de la colección donde se guardarán las instancias reales
        exp_collection_name = context.scene.split_collection.name

        # Crear o encontrar la colección "SetDressing_Exp"
        if exp_collection_name not in bpy.data.collections:
            exp_collection = bpy.data.collections.new(exp_collection_name)
            bpy.context.scene.collection.children.link(exp_collection)
        else:
            exp_collection = bpy.data.collections[exp_collection_name]

        # Obtener la colección activa
        active_collection = bpy.context.view_layer.active_layer_collection.collection

        # Iterar sobre los objetos en la colección activa
        for obj in active_collection.objects:
            # Seleccionar el objeto antes de hacer que las instancias sean reales
            bpy.ops.object.select_all(action='DESELECT')  # Deseleccionar todo
            obj.select_set(True)  # Seleccionar el objeto actual
            bpy.context.view_layer.objects.active = obj  # Activar el objeto

            # Hacer reales las instancias
            bpy.ops.object.duplicates_make_real()

            # Obtener los objetos generados (que estarán seleccionados)
            generated_objects = bpy.context.selected_objects

            # Mover solo los objetos generados a la colección "SetDressing_Exp"
            for new_obj in generated_objects:
                if new_obj.name.startswith("_")==False:
                    exp_collection.objects.link(new_obj)  # Añadir el objeto generado a la colección "SetDressing_Exp"
                    active_collection.objects.unlink(new_obj)  # Desvincular el objeto de la colección activa
                    self.report({'INFO'}, f"Objeto {new_obj.name} movido a la colección {exp_collection_name}")

            # Deseleccionar los objetos generados
            bpy.ops.object.select_all(action='DESELECT')

        # Volver a activar el modificador "Realize Instances"
        enable_realize_modifiers()

        self.report({'INFO'}, "Instancias convertidas y movidas a la colección 'SetDressing_Exp'.")
        return {'FINISHED'}

def disable_realize_modifiers():
    # Obtener la colección activa
    active_collection = bpy.context.view_layer.active_layer_collection.collection

    # Iterar sobre los objetos en la colección activa
    for obj in active_collection.objects:
        # Buscar el modificador "Realize Instances"
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                if mod.show_viewport:
                    mod.show_viewport = False
                print(f"Modificador 'Realize Instances' desactivado en {obj.name}")

    # Actualizar la vista para reflejar los cambios
    bpy.context.view_layer.update()

def enable_realize_modifiers():
    # Obtener la colección activa
    active_collection = bpy.context.view_layer.active_layer_collection.collection

    # Iterar sobre los objetos en la colección activa
    for obj in active_collection.objects:
        # Buscar el modificador "Realize Instances"
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                if not mod.show_viewport:
                    mod.show_viewport = True
                print(f"Modificador 'Realize Instances' activado en {obj.name}")

    # Actualizar la vista para reflejar los cambios
    bpy.context.view_layer.update()

def register():
    bpy.utils.register_class(OBJECT_OT_apply_activecollection_sys)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_apply_activecollection_sys)

if __name__ == "__main__":
    register()
