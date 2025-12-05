import bpy
import os
import subprocess
import tempfile
import shutil

from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty


# ----------------------------------------------------------
# PROPIEDADES
# ----------------------------------------------------------

class ActualizarFBXProps(PropertyGroup):

    ruta_blend: StringProperty(
        name="Archivo fuente (.blend)",
        subtype='FILE_PATH'
    )

    nombre_coleccion: StringProperty(
        name="Nombre de la colección"
    )


# ----------------------------------------------------------
# OPERADOR PRINCIPAL
# ----------------------------------------------------------

class OBJECT_OT_actualizar_coleccion_externa(Operator):
    bl_idname = "object.actualizar_coleccion_externa"
    bl_label = "Actualizar colección externa"
    bl_description = (
        "Actualiza una colección desde un archivo fuente .blend "
        "hacia un archivo destino 'Blocking_FBX' bloqueado"
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        props = context.scene.actualizar_fbx_props
        ruta_blend = bpy.path.abspath(props.ruta_blend)
        coleccion_nombre = props.nombre_coleccion

        # ------------------------------------------
        # Validar archivo fuente
        # ------------------------------------------
        if not os.path.exists(ruta_blend):
            self.report({'ERROR'}, "Archivo .blend fuente no encontrado.")
            return {'CANCELLED'}

        # Archivo actual
        archivo_actual = bpy.path.abspath(bpy.data.filepath)
        nombre_archivo = os.path.basename(archivo_actual)

        if not nombre_archivo.endswith("_Cutter.blend"):
            self.report({'ERROR'}, "El archivo actual debe terminar en '_Cutter.blend'")
            return {'CANCELLED'}

        # Archivo destino
        nombre_destino = nombre_archivo.replace("_Cutter.blend", "_Blocking_FBX.blend")
        carpeta_destino = r"I:\Unidades compartidas\EDITABLES ALPHAVERSE\FANZONES\16 Blocking_FBX"
        target_blend = os.path.join(carpeta_destino, nombre_destino)

        if not os.path.exists(target_blend):
            self.report(
                {'ERROR'},
                f"El archivo destino no existe:\n{target_blend}"
            )
            return {'CANCELLED'}

        # ------------------------------------------
        # Crear directorio temporal
        # ------------------------------------------
        temp_dir = tempfile.mkdtemp()
        fbx_path = os.path.join(temp_dir, "temp_export.fbx")
        blender_path = bpy.app.binary_path

        # ------------------------------------------
        # SCRIPT DE EXPORTACIÓN
        # ------------------------------------------
        export_script = os.path.join(temp_dir, "export_script.py")

        with open(export_script, "w") as f:
            f.write(f"""
import bpy
import sys

coleccion = bpy.data.collections.get('{coleccion_nombre}')

if not coleccion:
    print('ERROR: colección no encontrada')
    sys.exit(1)

# Deseleccionar todo
for obj in bpy.data.objects:
    obj.select_set(False)

# Seleccionar objetos de la colección
for obj in coleccion.objects:
    obj.select_set(True)

if coleccion.objects:
    bpy.context.view_layer.objects.active = coleccion.objects[0]

    bpy.ops.export_scene.fbx(
        filepath=r'{fbx_path}',
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        bake_space_transform=True,
        object_types={{'MESH'}},
        path_mode='AUTO',
        axis_forward='-Z',
        axis_up='Y'
    )
else:
    print('ERROR: colección vacía')
    sys.exit(1)
""")

        subprocess.run([blender_path, ruta_blend, "--background", "--python", export_script])

        if not os.path.exists(fbx_path):
            self.report({'ERROR'}, "No se generó el archivo FBX.")
            shutil.rmtree(temp_dir)
            return {'CANCELLED'}

        # ------------------------------------------
        # SCRIPT DE IMPORTACIÓN
        # ------------------------------------------
        import_script = os.path.join(temp_dir, "import_script.py")

        with open(import_script, "w") as f:
            f.write(f"""
import bpy
import sys

fbx_path = r'{fbx_path}'
coleccion_nombre = '{coleccion_nombre}'
coleccion_padre = 'Blocking'

# Eliminar colección previa
if coleccion_nombre in bpy.data.collections:
    col = bpy.data.collections[coleccion_nombre]
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(col)

# Purga profunda
bpy.ops.outliner.orphans_purge(
    do_local_ids=True,
    do_linked_ids=True,
    do_recursive=True
)

# Importar FBX
bpy.ops.import_scene.fbx(filepath=fbx_path)

# Crear colección destino
new_col = bpy.data.collections.new(coleccion_nombre)

if coleccion_padre in bpy.data.collections:
    parent_col = bpy.data.collections[coleccion_padre]
else:
    parent_col = bpy.data.collections.new(coleccion_padre)
    bpy.context.scene.collection.children.link(parent_col)

parent_col.children.link(new_col)

# Mover objetos importados
for obj in bpy.context.selected_objects:
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    new_col.objects.link(obj)

# Guardar archivo
bpy.ops.wm.save_mainfile()
""")

        subprocess.run([blender_path, target_blend, "--background", "--python", import_script])

        # ------------------------------------------
        # Limpieza final
        # ------------------------------------------
        shutil.rmtree(temp_dir)

        self.report(
            {'INFO'},
            f"Colección '{coleccion_nombre}' actualizada correctamente en:\n{target_blend}"
        )

        return {'FINISHED'}


# ----------------------------------------------------------
# REGISTRO PARA EL INIT
# ----------------------------------------------------------

classes = (
    ActualizarFBXProps,
    OBJECT_OT_actualizar_coleccion_externa,
)
