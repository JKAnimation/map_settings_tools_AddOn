import bpy
import bmesh
import csv
import os
from mathutils.bvhtree import BVHTree
from mathutils import Vector

# Limpieza de objetos que no empiecen con los prefijos deseados
prefijos = ("R_Apt", "S_Area", "R_Ch", "R_Num", "R_Pub", "R_Wall", "R_BR")
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

# Función para construir BVHTree
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

# Función para raycast
def is_inside(point, tree, samples=6, max_dist=1e6):
    count = 0
    directions = [Vector((1,0,0)), Vector((0,1,0)), Vector((0,0,1)), Vector((-1,0,0)), Vector((0,-1,0)), Vector((0,0,-1))]
    for direction in directions[:samples]:
        location, normal, index, distance = tree.ray_cast(point, direction, max_dist)
        if location is not None:
            count += 1
    return count % 2 == 1

# Función para medir el tamaño del número de edificio
def get_largest_edge_length(obj):
    mesh = obj.data
    max_len = 0
    for edge in mesh.edges:
        v1, v2 = obj.matrix_world @ mesh.vertices[edge.vertices[0]].co, obj.matrix_world @ mesh.vertices[edge.vertices[1]].co
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

# Datos para el CSV
data = []
landmarks = []

print("\n📦 RESUMEN DE DATOS:\n")
print("Barrio, Edificio, NumeroEdificio, EntradasTotal, R_Apt, R_Ch, R_Pub, R_Wall")
print("-" * 80)

for barrio in barrios:
    barrio_tree = bvhs_barrios[barrio.name]
    edificios_en_barrio = [e for e in edificios if is_inside(e.location, barrio_tree)]

    edificio_info = []

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

        edificio_info.append({
            "obj": edificio,
            "largest_num": largest_num.name if largest_num else "-",
            "size": size,
            "entradas": tipo_count,
            "entradas_list": entradas_en_edificio
        })

    edificio_info_sorted = sorted(edificio_info, key=lambda e: e["size"])

    for idx, info in enumerate(edificio_info_sorted, 1):
        e = info["obj"]
        entradas = info["entradas"]
        row = [
            barrio.name,
            e.name,
            idx,
            sum(entradas.values()),
            entradas["R_Apt"],
            entradas["R_Ch"],
            entradas["R_Pub"],
            entradas["R_Wall"]
        ]
        data.append(row)
        print(", ".join(str(item) for item in row))

        # Detalle por entrada
        for entrada in info["entradas_list"]:
            tipo = [t for t in tipo_count if entrada.name.startswith(t)]
            tipo_str = tipo[0] if tipo else "Desconocido"
            print(f"   ↳ Entrada: {entrada.name} (tipo: {tipo_str})")

# Detectar entradas que no están en ningún edificio
edificio_trees = list(bvhs_edificios.values())
for entrada in entradas:
    if not any(is_inside(entrada.location, tree) for tree in edificio_trees):
        landmarks.append(entrada)

print("\n🏛️ ENTRADAS SIN EDIFICIO (LANDMARKS):")
for entrada in landmarks:
    print(f"- {entrada.name}")

# Guardar CSV
output_path = bpy.path.abspath("//resumen_barrios.csv")
with open(output_path, "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Barrio", "Edificio", "NumeroEdificio", "EntradasTotal", "R_Apt", "R_Ch", "R_Pub", "R_Wall"])
    writer.writerows(data)

print(f"\n✅ Archivo CSV guardado en: {output_path}")
