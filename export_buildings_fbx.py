import bpy
import os

class OBJECT_OT_buildings_export_fbx(bpy.types.Operator):
    bl_idname = "object.buildings_export_fbx"
    bl_label = "Buildings Export FBX"
    bl_description = "Exporta edificios de la colección seleccionada en archivos FBX"
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------
    # Funciones internas
    # ------------------------
    def show_error_message(self, messages, title="Errores de Nomenclatura"):
        def draw(self, context):
            for msg in messages:
                self.layout.label(text=msg)
        bpy.context.window_manager.popup_menu(draw, title=title, icon='ERROR')

    def obtener_coleccion_seleccionada(self):
        vista_espacio = bpy.context.view_layer.active_layer_collection
        return vista_espacio.collection if vista_espacio else None

    def validar_nombres_y_renombrar(self, coleccion_seleccionada):
        errores = []
        for subcoleccion in coleccion_seleccionada.children:
            colpart = subcoleccion.name.split("_")
            tipo = colpart[1] if len(colpart) > 1 else ""
            for obj in subcoleccion.objects:
                partes = obj.name.split("_")
                if len(partes) < 4:
                    errores.append(f"Error en {obj.name}: nombre incompleto.")
                    continue
                if partes[0] != "S":
                    errores.append(f"Error en {obj.name}: debe iniciar con 'S'")
                if partes[1] != colpart[0]:
                    errores.append(f"Error en {obj.name}: prefijo incorrecto")
                if partes[2] != tipo:
                    errores.append(f"Error en {obj.name}: tipo incorrecto")
                if tipo in ("CH", "PUB", "APT") and partes[3] != "Entrance":
                    errores.append(f"Error en {obj.name}: debe ser 'Entrance'")
                if not errores:
                    obj.data.name = obj.name
        return len(errores) == 0, errores

    def guardar_materiales(self):
        return {obj.name: [slot.material for slot in obj.material_slots] for obj in bpy.data.objects if obj.type == 'MESH'}

    def limpiar_materiales(self):
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()

    def aplicar_transformaciones(self):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    def exportar_fbx(self, ruta):
        seleccionados = [obj for obj in bpy.context.selected_objects]
        bpy.ops.object.select_all(action='DESELECT')
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        for obj in meshes:
            obj.select_set(True)
        self.aplicar_transformaciones()
        if meshes:
            bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.export_scene.fbx(
            filepath=ruta,
            check_existing=True,
            use_selection=True,
            global_scale=1,
            apply_unit_scale=True,
            bake_space_transform=True,
            object_types={'MESH'},
            path_mode='AUTO',
            axis_forward='-Z',
            axis_up='Y'
        )
        bpy.ops.object.select_all(action='DESELECT')
        for obj in seleccionados:
            obj.select_set(True)

    def restaurar_materiales(self, materiales_objetos):
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.name in materiales_objetos:
                obj.data.materials.clear()
                for mat in materiales_objetos[obj.name]:
                    obj.data.materials.append(mat)

    # ------------------------
    # Método principal
    # ------------------------
    def execute(self, context):
        coleccion = self.obtener_coleccion_seleccionada()
        if not coleccion:
            self.report({'ERROR'}, "No hay una colección seleccionada.")
            return {'CANCELLED'}

        validado, errores = self.validar_nombres_y_renombrar(coleccion)
        if not validado:
            self.show_error_message(["❌ No se pudo exportar por errores de nomenclatura"] + errores)
            for er in errores:
                print(er)
            return {'CANCELLED'}

        export_folder = bpy.path.abspath(context.scene.export_folder)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        ruta_fbx = os.path.join(export_folder, f"{coleccion.name}.fbx")

        materiales_guardados = self.guardar_materiales()
        self.limpiar_materiales()
        self.exportar_fbx(ruta_fbx)
        self.restaurar_materiales(materiales_guardados)

        self.report({'INFO'}, f"✅ Exportación completada: {ruta_fbx}")
        return {'FINISHED'}


# ------------------------------------------------------------
# NUEVO: lista de clases que exporta este módulo
# ------------------------------------------------------------
classes = (
    OBJECT_OT_buildings_export_fbx,
)
