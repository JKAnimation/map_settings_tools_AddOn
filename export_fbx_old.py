import bpy
import os

class OBJECT_OT_export_fbx(bpy.types.Operator):
    bl_idname = "object.export_fbx"
    bl_label = "Export FBX"
    bl_description = "Exporta FBX separando por colecciones usando la colección activa, pero ¡solo funciona en archivos de set dressing!"

    @classmethod
    def poll(cls, context):
        # Obtener la ruta del archivo actual
        current_file_path = bpy.data.filepath
        
        # Verificar si hay un archivo guardado
        if current_file_path:
            # Extraer el nombre del archivo sin la extensión
            base_name = os.path.splitext(os.path.basename(current_file_path))[0]
            # Verificar si el nombre base NO empieza con "BUILDINGS"
            return not base_name.lower().startswith("buildings")
        
        return False
    
    def execute(self, context):
        # Obtener la ruta de exportación seleccionada por el usuario
        export_path = context.scene.export_folder

        # Asegurarse de que la carpeta existe
        if not os.path.exists(export_path):
            self.report({'ERROR'}, "La carpeta seleccionada no existe")
            return {'CANCELLED'}

        # Definir la colección grande activa
        main_collection = bpy.context.view_layer.active_layer_collection.collection

        # Opciones de exportación
        export_options = {
            "check_existing": True,
            "use_selection": True,
            "global_scale": 1,
            "apply_unit_scale": True,
            "apply_scale_options": 'FBX_SCALE_NONE',
            "use_space_transform": True,
            "bake_space_transform": True,
            "object_types": {'MESH'},
            "use_mesh_modifiers": True,
            "mesh_smooth_type": 'EDGE',
            "path_mode": 'AUTO',
            "axis_forward": '-Z',
            "axis_up": 'Y'
        }

        def export_collection(collection):
            """ Exporta los objetos de una colección si no está vacía """
            # Obtener objetos de la colección
            objetos_exportar = [obj for obj in bpy.context.scene.objects if obj.name in collection.objects]

            # Si la colección tiene objetos, exportar
            if objetos_exportar:
                bpy.ops.object.select_all(action='DESELECT')

                for obj in objetos_exportar:
                    obj.select_set(True)
                    obj.data.materials.clear()  # Elimina materiales antes de exportar

                export_filename = os.path.join(export_path, collection.name + ".fbx")
                bpy.ops.export_scene.fbx(filepath=export_filename, **export_options)
                print(f"Exportado: {export_filename}")

        # Exportar la colección activa si no tiene subcolecciones
        if not main_collection.children:
            export_collection(main_collection)
        else:
            # Exportar cada subcolección solo si tiene objetos
            for sub_collection in main_collection.children:
                export_collection(sub_collection)

        self.report({'INFO'}, "Exportación completada")
        return {'FINISHED'}
