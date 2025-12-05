import bpy
import bmesh
import csv
from mathutils.bvhtree import BVHTree
from mathutils import Vector

class OBJECT_OT_generar_resumen_barrios(bpy.types.Operator):
    """Genera un CSV con la información de barrios, edificios y entradas"""
    bl_idname = "object.generar_resumen_barrios"
    bl_label = "Generar Resumen Barrios"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Prefijos que se consideran
            prefijos = ("R_Apt", "S_Area", "R_Ch", "R_Num", "R_Pub", "R_Wall", "R_BR")

            # Limpieza de objetos que no empiecen con los prefijos
            for obj in list(bpy.data.objects):
                if not obj.name.startswith(prefijos):
                    bpy.data.objects.remove(obj, do_unlink=True)

            # Conversión a malla y escalado
            for obj in bpy.data.objects:
                if obj.type != 'MESH':
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.convert(target='MESH')
                obj.scale = (400, 400, 400)
            bpy.context.view_layer.update()

            # Funciones internas
            def get_bvhtree(obj):
                mesh = obj.data
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.verts.ensure_lookup_table()
                bm.faces.ensure_lookup_table()
                bm.normal_update()
                bm.transform(obj.matrix_world)
                tree = BVHTree.FromBMesh(bm)
                bm.free()
                return tree

            def is_inside(point, tree, samples=6, max_dist=1e6):
                count = 0
                directions = [
                    Vector((1,0,0)), Vector((0,1,0)), Vector((0,0,1)),
                    Vector((-1,0,0)), Vector((0,-1,0)), Vector((0,0,-1))
                ]
                for direction in directions[:samples]:
                    location, normal, index, distance = tree.ray_cast(point, direction, max_dist)
                    if location is not None:
                        count += 1
                return count % 2 == 1

            def get_largest_edge_length(obj):
                mesh = obj.data
                max_len = 0
                for edge in mesh.edges:
                    v1 = obj.matrix_world @ mesh.vertices[edge.vertices[0]].co
                    v2 = obj.matrix_world @ mesh.vertices[edge.vertices[1]].co
                    max_len = max(max_len, (v1 - v2).length)
                return max_len

            # Agrupar objetos
            barrios = [o for o in bpy.data.objects if o.name.startswith("R_BR")]
            edificios = [o for o in bpy.data.objects if o.name.startswith("S_Area")]
            numeros = [o for o in bpy.data.objects if o.name.startswith("R_Num")]
            entradas = [o for o in bpy.data.objects if o.name.startswith(("R_Apt", "R_Ch", "R_Pub", "R_Wall"))]

            # Construir BVHTrees
            bvhs_barrios = {o.name: get_bvhtree(o) for o in barrios}
            bvhs_edificios = {o.name: get_bvhtree(o) for o in edificios}

            data = []
            landmarks = []

            # Procesar barrios y edificios
            for barrio in barrios:
                barrio_tree = bvhs_barrios[barrio.name]
                edificios_en_barrio = [e for e in edificios if is_inside(e.location, barrio_tree)]

                for edificio in edificios_en_barrio:
                    edificio_tree = bvhs_edificios[edificio.name]

                    nums = [n for n in numeros if is_inside(n.location, edificio_tree)]
                    nums_sorted = sorted(nums, key=lambda n: get_largest_edge_length(n))

                    entradas_en_edificio = [e for e in entradas if is_inside(e.location, edificio_tree)]
                    tipo_count = {"R_Apt": 0, "R_Ch": 0, "R_Pub": 0, "R_Wall": 0}
                    for ent in entradas_en_edificio:
                        for tipo in tipo_count:
                            if ent.name.startswith(tipo):
                                tipo_count[tipo] += 1

                    largest_num = nums_sorted[0] if nums_sorted else None
                    size = get_largest_edge_length(largest_num) if largest_num else 0

                    idx = 1  # número del edificio dentro del barrio (puedes ajustarlo si necesitas orden)
                    row = [
                        barrio.name,
                        edificio.name,
                        idx,
                        sum(tipo_count.values()),
                        tipo_count["R_Apt"],
                        tipo_count["R_Ch"],
                        tipo_count["R_Pub"],
                        tipo_count["R_Wall"]
                    ]
                    data.append(row)

            # Detectar entradas que no están en ningún edificio
            edificio_trees = list(bvhs_edificios.values())
            for entrada in entradas:
                if not any(is_inside(entrada.location, tree) for tree in edificio_trees):
                    landmarks.append(entrada)

            # Guardar CSV
            output_path = bpy.path.abspath("//resumen_barrios.csv")
            with open(output_path, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Barrio", "Edificio", "NumeroEdificio", "EntradasTotal", "R_Apt", "R_Ch", "R_Pub", "R_Wall"])
                writer.writerows(data)

            self.report({'INFO'}, f"Archivo CSV guardado en: {output_path}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error al generar resumen: {e}")
            return {'CANCELLED'}

# ------------------------------------------------------------
# Lista de clases exportadas por este módulo
# ------------------------------------------------------------
classes = (
    OBJECT_OT_generar_resumen_barrios,
)
