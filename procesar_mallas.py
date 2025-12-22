import bpy
import re


# ==============================================================
#   PROPIEDADES
# ==============================================================

class ProcesarDuplicadorProps(bpy.types.PropertyGroup):
    coleccion_target: bpy.props.StringProperty(name="Colección Target")
    usar_mesh_activa: bpy.props.BoolProperty(name="Usar Mesh Activa", default=True)



# ==============================================================
#   FUNCIONES AUXILIARES
# ==============================================================


def obtener_meshes_recursivamente(coleccion):
    objetos_mesh = []

    def recorrer(col):
        for obj in col.objects:
            if obj.type == 'MESH':
                objetos_mesh.append(obj)
        for sub in col.children:
            recorrer(sub)

    recorrer(coleccion)
    return objetos_mesh


def duplicar_coleccion_recursiva(origen, destino):
    """Clona estructura de subcolecciones (NO objetos aún)."""
    for sub in origen.children:
        nueva = bpy.data.collections.new(sub.name)
        destino.children.link(nueva)
        duplicar_coleccion_recursiva(sub, nueva)


def limpiar_sufijo(nombre):
    """Elimina sufijos .001, .002, etc."""
    return re.sub(r"\.\d{3}$", "", nombre)



# ==============================================================
#   PROCESAMIENTO PRINCIPAL SEGURO
# ==============================================================

def procesar_con_malla_base(obj_malla, coleccion_verde, nombre_export):

    # -----------------------------------------------------------
    # 1) Renombrar colección verde con sufijo .001
    # -----------------------------------------------------------
    coleccion_verde.name = nombre_export + ".001"

    # Copia de la mesh base
    data_base = obj_malla.data.copy()

    # -----------------------------------------------------------
    # 2) Renombrar meshes internas conservando sufijo .001
    # -----------------------------------------------------------
    for i, obj in enumerate(coleccion_verde.objects):
        if obj.type != 'MESH':
            continue

        obj.data = data_base.copy()
        obj.name = f"{nombre_export}_{str(i).zfill(2)}.001"
        obj.data.name = obj.name + "_Mesh"


    # -----------------------------------------------------------
    # 3) Crear colección Exporter si no existe
    # -----------------------------------------------------------
    if "Exporter" not in bpy.data.collections:
        coleccion_exporter = bpy.data.collections.new("Exporter")
        bpy.context.scene.collection.children.link(coleccion_exporter)
    else:
        coleccion_exporter = bpy.data.collections["Exporter"]


    # -----------------------------------------------------------
    # 4) Crear copia COMPLETA de la colección verde
    # -----------------------------------------------------------
    coleccion_final = bpy.data.collections.new(nombre_export)
    coleccion_exporter.children.link(coleccion_final)

    # Duplicar estructura interna sin objetos
    duplicar_coleccion_recursiva(coleccion_verde, coleccion_final)


    # -----------------------------------------------------------
    # 5) Duplicar objetos respetando subcolecciones
    # -----------------------------------------------------------
    def copiar_objetos(origen, destino):
        for obj in origen.objects:
            if obj.type == 'MESH':
                copia = obj.copy()
                copia.data = obj.data.copy()

                copia.name = copia.name.replace(".001", "")
                copia.data.name = copia.name

                destino.objects.link(copia)

        # Subcolecciones
        for sub_origen in origen.children:
            sub_destino = destino.children.get(sub_origen.name)
            copiar_objetos(sub_origen, sub_destino)

    copiar_objetos(coleccion_verde, coleccion_final)


    # -----------------------------------------------------------
    # 6) Aplicar modificadores SOLO en la copia
    # -----------------------------------------------------------
    bpy.context.view_layer.update()
    
    for obj in coleccion_final.all_objects:
        if obj.type != 'MESH':
            continue

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
        obj.name=obj.name.replace(".002","")
        obj.data.name=obj.name

        obj.select_set(False)


    print(f"✔ Procesado {nombre_export} -> Exportado en Exporter/{coleccion_final.name}")



# ==============================================================
#   OPERADOR PRINCIPAL
# ==============================================================

class OBJECT_OT_procesar_desde_coleccion(bpy.types.Operator):
    bl_idname = "object.procesar_desde_coleccion"
    bl_label = "Procesar Mesh o Colección"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(col for col in bpy.data.collections if col.color_tag == 'COLOR_04')

    def execute(self, context):
        props = context.scene.procesar_coleccion_props

        coleccion_verde = next((c for c in bpy.data.collections if c.color_tag == 'COLOR_04'), None)
        if not coleccion_verde:
            self.report({'ERROR'}, "No existe colección verde.")
            return {'CANCELLED'}

        # ======================================================
        # MODO: USAR SOLO LA MESH ACTIVA
        # ======================================================
        if props.usar_mesh_activa:
            obj_malla = context.active_object

            if not obj_malla or obj_malla.type != 'MESH':
                self.report({'ERROR'}, "Selecciona una mesh activa válida.")
                return {'CANCELLED'}

            if coleccion_verde in obj_malla.users_collection:
                self.report({'ERROR'}, "La mesh activa NO puede estar dentro de la colección verde.")
                return {'CANCELLED'}

            if any(m.type == 'NODES' for m in obj_malla.modifiers):
                self.report({'ERROR'}, "La mesh activa NO puede tener Geometry Nodes.")
                return {'CANCELLED'}

            nombre_export = limpiar_sufijo(obj_malla.name)

            procesar_con_malla_base(obj_malla, coleccion_verde, nombre_export)


        # ======================================================
        # MODO: PROCESAR TODA UNA COLECCIÓN
        # ======================================================
        else:

            coleccion_target = bpy.data.collections.get(props.coleccion_target)
            if not coleccion_target:
                self.report({'ERROR'}, "Colección destino no encontrada.")
                return {'CANCELLED'}

            objetos_mesh = obtener_meshes_recursivamente(coleccion_target)
            if not objetos_mesh:
                self.report({'ERROR'}, "No hay meshes dentro de la colección destino.")
                return {'CANCELLED'}

            for obj_malla in objetos_mesh:
                nombre_export = limpiar_sufijo(obj_malla.name)
                procesar_con_malla_base(obj_malla, coleccion_verde, nombre_export)


        self.report({'INFO'}, "Proceso completado correctamente.")
        return {'FINISHED'}



