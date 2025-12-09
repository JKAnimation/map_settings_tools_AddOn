import bpy

class OBJECT_OT_clean_building_collections(bpy.types.Operator):
    bl_idname = "object.clean_building_collections"
    bl_label = "Clean Building Collections"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Elimina todos los objetos en las colecciones para exportar y limpia los datos huérfanos"

    @classmethod
    def poll(cls, context):
        # Verifica si hay objetos en al menos una de las colecciones especificadas
        collection_names = ["Buildings_Exp", "Facades_Exp", "Letters_Exp", "Plates_Exp", "Bases_Exp", "Stairs_Exp", "Numbers_Exp"]
        for name in collection_names:
            collection = bpy.data.collections.get(name)
            if collection and len(collection.objects) > 0:
                return True
        return False

    def execute(self, context):
        # Nombres de las colecciones a limpiar
        collection_names = ["Buildings_Exp", "Facades_Exp", "Letters_Exp", "Plates_Exp", "Bases_Exp", "Stairs_Exp", "Numbers_Exp"]

        for name in collection_names:
            collection = bpy.data.collections.get(name)
            if collection is not None:
                # Iterar sobre los objetos en la colección y eliminarlos
                for obj in collection.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                self.report({'INFO'}, f"Objetos eliminados en la colección {name}")
            else:
                self.report({'WARNING'}, f"La colección {name} no existe")

        # Limpieza de datos huérfanos
        # Buscar y eliminar datos no utilizados manualmente
        def remove_unused_data(data_collection):
            for data_block in data_collection:
                if not data_block.users:
                    data_collection.remove(data_block)

        # Limpiar los datos huérfanos en diferentes tipos de datos
        remove_unused_data(bpy.data.meshes)
        remove_unused_data(bpy.data.materials)
        remove_unused_data(bpy.data.textures)
        remove_unused_data(bpy.data.lights)
        remove_unused_data(bpy.data.cameras)
        remove_unused_data(bpy.data.curves)
        remove_unused_data(bpy.data.images)
        remove_unused_data(bpy.data.node_groups)
        remove_unused_data(bpy.data.particles)
        remove_unused_data(bpy.data.speakers)

        self.report({'INFO'}, "Data limpia de objetos no utilizados.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_clean_building_collections)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_clean_building_collections)

if __name__ == "__main__":
    register()
