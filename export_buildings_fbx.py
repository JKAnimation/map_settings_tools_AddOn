import bpy
import os

class OBJECT_OT_buildings_export_fbx(bpy.types.Operator):
    bl_idname = "object.buildings_export_fbx"
    bl_label = "Buildings Export FBX"
    bl_description = "Exportar edificios de la colección seleccionada en archivos FBX"
    bl_options = {'REGISTER', 'UNDO'}

    def show_error_message(self, messages, title="Errores de Nomenclatura"):
        """Muestra un mensaje de error en un popup con múltiples líneas."""
        def draw(self, context):
            for msg in messages:
                self.layout.label(text=msg)
        bpy.context.window_manager.popup_menu(draw, title=title, icon='ERROR')

    def obtener_coleccion_seleccionada(self):
        """Obtiene la colección activa en el Outliner."""
        vista_espacio = bpy.context.view_layer.active_layer_collection
        return vista_espacio.collection if vista_espacio else None

    def validar_nombres_y_renombrar(self, coleccion_seleccionada):
        """Valida los nombres de los objetos en la colección seleccionada y renombra la data si no hay errores."""
        errores = []
        for subcoleccion in coleccion_seleccionada.children:
            colpart = subcoleccion.name.split("_")
            tipo = colpart[1] if len(colpart) > 1 else ""

            for obj in subcoleccion.objects:
                partes = obj.name.split("_")

                if len(partes) < 4:
                    errores.append(f"Error en {obj.name}: nombre incompleto.")
                    continue  # Saltar el resto de validaciones si el nombre es muy corto

                if partes[0] != "S":
                    errores.append(f"Error en {obj.name}: debe iniciar con 'S'")

                if partes[1] != colpart[0]:
                    errores.append(f"Error en {obj.name}: el prefijo debe ser {colpart[0]}")

                if partes[2] != tipo:
                    errores.append(f"Error en {obj.name}: esto es '{tipo}', no '{partes[2]}'")

                if tipo in ("CH", "PUB", "APT") and partes[3] != "Entrance":
                    errores.append(f"Error en {obj.name}: debe ser 'Entrance' en _{partes[3]}_")

                if len(partes) > (3 if tipo in ("Building", "Wall", "BLimit") else 4) and partes[3 if tipo in ("Building", "Wall", "BLimit") else 4].isdigit():
                    errores.append(f"Error en {obj.name}: el número debe ir acompañado de una letra")

                if len(partes) > (4 if tipo in ("Building", "Wall", "BLimit") else 5) and partes[-1] not in ("LOD1", "LOD2", "Coll"):
                    errores.append(f"Error en {obj.name}: sufijo '{partes[-1]}' no permitido")

                if not errores:
                    obj.data.name = obj.name  # Renombrar la data del objeto

        return len(errores) == 0, errores


    def guardar_materiales(self):
        """Guarda los materiales de cada objeto."""
        return {obj.name: [slot.material for slot in obj.material_slots] for obj in bpy.data.objects if obj.type == 'MESH'}

    def limpiar_materiales(self):
        """Elimina los materiales de los objetos."""
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()

    def aplicar_transformaciones(self):
        """Aplica la rotación y escala a todas las mallas."""
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    def exportar_fbx(self, ruta):
        """Exporta las mallas seleccionadas como un solo FBX."""
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
        """Restaura los materiales originales a los objetos."""
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.name in materiales_objetos:
                obj.data.materials.clear()
                for mat in materiales_objetos[obj.name]:
                    obj.data.materials.append(mat)

    def execute(self, context):
        coleccion = self.obtener_coleccion_seleccionada()
        if not coleccion:
            self.report({'ERROR'}, "No hay una colección seleccionada.")
            return {'CANCELLED'}

        validado, errores = self.validar_nombres_y_renombrar(coleccion)
        if not validado:
            self.show_error_message(["❌ No se pudo exportar por errores de nomenclatura"] + errores)
            for er in errores:
                print (er)
            return {'CANCELLED'}

        # Obtener la carpeta de exportación desde la escena
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
