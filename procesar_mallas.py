import bpy
import re

class ProcesarDuplicadorProps(bpy.types.PropertyGroup):
    coleccion_target: bpy.props.StringProperty(name="Colección Target")
    usar_mesh_activa: bpy.props.BoolProperty(name="Usar Mesh Activa", default=True)


def procesar_con_malla_base(obj_malla, coleccion_origen, nombre_export):
    coleccion_origen.name = nombre_export + ".001"

    for i, obj in enumerate(coleccion_origen.objects):
        if obj != obj_malla and obj.type == 'MESH':
            obj.data = obj_malla.data
            obj.name = f"{nombre_export}_{str(i).zfill(2)}.001"

    if "Exporter" not in bpy.data.collections:
        coleccion_exporter = bpy.data.collections.new("Exporter")
        bpy.context.scene.collection.children.link(coleccion_exporter)
    else:
        coleccion_exporter = bpy.data.collections["Exporter"]

    coleccion_duplicada = bpy.data.collections.new(name=nombre_export)
    coleccion_exporter.children.link(coleccion_duplicada)

    objetos_originales = [obj for obj in coleccion_origen.objects if obj.type == 'MESH']
    nombres_originales = {obj.name for obj in objetos_originales}

    bpy.ops.object.select_all(action='DESELECT')
    for obj in objetos_originales:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target='MESH')
        obj.select_set(False)

    nuevos_objs = [obj for obj in bpy.context.selected_objects if obj.name not in nombres_originales]

    for obj in nuevos_objs:
        nombre_base_obj = re.sub(r'\.\d{3}$', '', obj.name)
        obj.name = nombre_base_obj
        if obj.data:
            obj.data.name = nombre_base_obj + "_Mesh"

        for col in obj.users_collection:
            col.objects.unlink(obj)
        coleccion_duplicada.objects.link(obj)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    for obj in list(coleccion_origen.objects):
        if obj.name not in nombres_originales:
            coleccion_origen.objects.unlink(obj)

    print(f"✅ Procesado '{nombre_export}' -> Exportado en 'Exporter/{coleccion_duplicada.name}'")


def obtener_meshes_recursivamente(coleccion):
    objetos_mesh = []

    def recorrer(col):
        for obj in col.objects:
            if obj.type == 'MESH':
                objetos_mesh.append(obj)
        for subcol in col.children:
            recorrer(subcol)

    recorrer(coleccion)
    return objetos_mesh


class OBJECT_OT_procesar_desde_coleccion(bpy.types.Operator):
    bl_idname = "object.procesar_desde_coleccion"
    bl_label = "Procesar Mesh o Colección"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(col for col in bpy.data.collections if col.color_tag == 'COLOR_04')

    def execute(self, context):
        props = context.scene.procesar_coleccion_props

        coleccion_origen = next((col for col in bpy.data.collections if col.color_tag == 'COLOR_04'), None)
        if not coleccion_origen:
            self.report({'ERROR'}, "No se encontró una colección con color_tag 'COLOR_04'.")
            return {'CANCELLED'}

        if props.usar_mesh_activa:
            obj_malla = context.active_object
            if not obj_malla or obj_malla.type != 'MESH':
                self.report({'ERROR'}, "Selecciona una mesh activa.")
                return {'CANCELLED'}
            if coleccion_origen in obj_malla.users_collection:
                self.report({'ERROR'}, "La mesh activa está en la colección de origen.")
                return {'CANCELLED'}
            if any(mod.type == 'NODES' for mod in obj_malla.modifiers):
                self.report({'ERROR'}, "La mesh activa tiene Geometry Nodes.")
                return {'CANCELLED'}

            nombre_export = re.sub(r'\.\d{3}$', '', obj_malla.name)
            bpy.context.view_layer.objects.active = obj_malla
            procesar_con_malla_base(obj_malla, coleccion_origen, nombre_export)

        else:
            coleccion_target = bpy.data.collections.get(props.coleccion_target)
            if not coleccion_target:
                self.report({'ERROR'}, "No se encontró la colección seleccionada.")
                return {'CANCELLED'}

            objetos_mesh = obtener_meshes_recursivamente(coleccion_target)
            if not objetos_mesh:
                self.report({'ERROR'}, "No se encontraron meshes en la colección seleccionada.")
                return {'CANCELLED'}

            for obj_malla in objetos_mesh:
                nombre_export = re.sub(r'\.\d{3}$', '', obj_malla.name)
                bpy.context.view_layer.objects.active = obj_malla
                procesar_con_malla_base(obj_malla, coleccion_origen, nombre_export)

        self.report({'INFO'}, "🎉 Proceso completado.")
        return {'FINISHED'}
