import bpy
import os

class OBJECT_OT_export_fbx(bpy.types.Operator):
    bl_idname = "object.export_fbx"
    bl_label = "Export FBX"
    bl_description = "Exporta FBX separando por colecciones usando la colección activa, solo si las mallas tienen vértices"

    @classmethod
    def poll(cls, context):
        current_file_path = bpy.data.filepath
        if current_file_path:
            base_name = os.path.splitext(os.path.basename(current_file_path))[0]
            return not base_name.lower().startswith("buildings")
        return False

    def execute(self, context):
        export_path = context.scene.export_folder

        if not os.path.exists(export_path):
            self.report({'ERROR'}, "La carpeta seleccionada no existe")
            return {'CANCELLED'}

        main_collection = bpy.context.view_layer.active_layer_collection.collection

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
            objetos_validos = [
                obj for obj in collection.objects
                if obj.type == 'MESH' and
                obj.data is not None and
                hasattr(obj.data, "vertices") and
                len(obj.data.vertices) > 0
            ]

            if objetos_validos:
                bpy.ops.object.select_all(action='DESELECT')

                for obj in objetos_validos:
                    obj.select_set(True)
                    obj.data.materials.clear()

                export_filename = os.path.join(export_path, collection.name + ".fbx")
                bpy.ops.export_scene.fbx(filepath=export_filename, **export_options)
                print(f"✅ Exportado: {export_filename}")
            else:
                print(f"⛔ Colección '{collection.name}' vacía o sin mallas válidas. No se exporta.")

        # Exportar la colección activa si no tiene subcolecciones
        if not main_collection.children:
            export_collection(main_collection)
        else:
            for sub_collection in main_collection.children:
                export_collection(sub_collection)

        self.report({'INFO'}, "Exportación completada")
        return {'FINISHED'}
