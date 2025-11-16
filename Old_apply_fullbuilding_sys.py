import bpy

class OBJECT_OT_apply_fullbuilding_sys(bpy.types.Operator):
    bl_idname = "object.apply_fullbuilding_sys"
    bl_label = "Apply FullBuilding Sys"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convierte instancias en objetos reales y los organiza en colecciones"

    @classmethod
    def poll(cls, context):
        # Verifica si hay objetos en al menos una de las colecciones especificadas
        collection_names = ["Buildings_Exp", "Facades_Exp", "Letters_Exp", "Plates_Exp", "Bases_Exp", "Stairs_Exp", "Numbers_Exp"]
        for name in collection_names:
            collection = bpy.data.collections.get(name)
            if collection and len(collection.objects) == 0:
                return True
        return False

    def execute(self, context):
        # Desactivar el modificador "Realize Instances"
        disable_realize_modifiers()

        # Diccionario con los nombres de los objetos y sus colecciones correspondientes
        object_collection_map = {
            "00_Buildings": "Buildings_Exp",
            "01_Facades": "Facades_Exp",
            "03_Letters": "Letters_Exp",
            "04_Plates": "Plates_Exp",
            "05_Bases": "Bases_Exp",
            "06_Stairs": "Stairs_Exp",
            "02_Numbers": "Numbers_Exp"
        }

        # Obtener la colección "Master"
        master_collection = bpy.data.collections.get("Master")
        if master_collection is None:
            self.report({'ERROR'}, "La colección 'Master' no existe.")
            return {'CANCELLED'}

        # Iterar sobre los objetos en la colección "Master"
        for obj in master_collection.objects:
            if obj.name in object_collection_map:
                # Seleccionar el objeto antes de hacer que las instancias sean reales
                bpy.ops.object.select_all(action='DESELECT')  # Deseleccionar todo
                obj.select_set(True)  # Seleccionar el objeto actual
                bpy.context.view_layer.objects.active = obj  # Activar el objeto

                # Hacer reales las instancias
                bpy.ops.object.duplicates_make_real()

                # Obtener los objetos generados (que estarán seleccionados)
                generated_objects = bpy.context.selected_objects

                # Obtener o crear la colección destino
                collection_name = object_collection_map[obj.name]
                new_collection = bpy.data.collections.get(collection_name)
                if new_collection is None:
                    new_collection = bpy.data.collections.new(collection_name)
                    bpy.context.scene.collection.children.link(new_collection)
                    self.report({'INFO'}, f"Creada colección: {collection_name}")

                # Mover solo los objetos generados a la nueva colección
                for new_obj in generated_objects:
                    new_collection.objects.link(new_obj)  # Añadir el objeto generado a la nueva colección
                    master_collection.objects.unlink(new_obj)  # Desvincular el objeto de la colección 'Master'
                    self.report({'INFO'}, f"Objeto {new_obj.name} movido a la colección {collection_name}")

                # Deseleccionar los objetos generados
                bpy.ops.object.select_all(action='DESELECT')

        # Volver a activar el modificador "Realize Instances"
        enable_realize_modifiers()

        self.report({'INFO'}, "Modificadores 'Realize Instances' desactivados, objetos separados y modificadores reactivados.")
        return {'FINISHED'}

def disable_realize_modifiers():
    # Obtener la colección "Master"
    master_collection = bpy.data.collections.get("Master")
    if master_collection is None:
        print("La colección 'Master' no existe.")
        return

    # Iterar sobre los objetos en la colección "Master"
    for obj in master_collection.objects:
        # Buscar el modificador "Realize Instances"
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                if mod.show_viewport:
                    mod.show_viewport = False
                else:
                    mod.show_viewport = True
                print(f"Modificador 'Realize Instances' desactivado en {obj.name}")

    # Actualizar la vista para reflejar los cambios
    bpy.context.view_layer.update()

def enable_realize_modifiers():
    # Obtener la colección "Master"
    master_collection = bpy.data.collections.get("Master")
    if master_collection is None:
        print("La colección 'Master' no existe.")
        return

    # Iterar sobre los objetos en la colección "Master"
    for obj in master_collection.objects:
        # Buscar el modificador "Realize Instances"
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                if not mod.show_viewport:
                    mod.show_viewport = True
                print(f"Modificador 'Realize Instances' activado en {obj.name}")

    # Actualizar la vista para reflejar los cambios
    bpy.context.view_layer.update()

def register():
    bpy.utils.register_class(OBJECT_OT_apply_fullbuilding_sys)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_apply_fullbuilding_sys)

if __name__ == "__main__":
    register()
