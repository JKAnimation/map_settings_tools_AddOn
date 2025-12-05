import bpy
import csv
from mathutils import Vector

class OBJECT_OT_generate_csv_report(bpy.types.Operator):
    bl_idname = "object.generate_csv_report"
    bl_label = "Generate CSV Report"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Funciones auxiliares
        def expand_volume(container, expansion):
            bbox_corners = [Vector(corner) for corner in container.bound_box]
            min_corner = Vector([min(corner[i] for corner in bbox_corners) for i in range(3)])
            max_corner = Vector([max(corner[i] for corner in bbox_corners) for i in range(3)])
            expanded_min = min_corner - expansion
            expanded_max = max_corner + expansion
            return expanded_min, expanded_max

        def is_point_inside_expanded_volume(expanded_min, expanded_max, point):
            return all(expanded_min[i] <= point[i] <= expanded_max[i] for i in range(3))

        def is_point_inside_volume(container, point, expansion=Vector((0.05, 0.05, 0.05))):
            expanded_min, expanded_max = expand_volume(container, expansion)
            inv_mat = container.matrix_world.inverted()
            local_point = inv_mat @ point
            return is_point_inside_expanded_volume(expanded_min, expanded_max, local_point)

        def get_base_name(name):
            return name.split(".")[0]

        def get_type_from_name(entry_name):
            collections_prefixes = ["CHS", "Walls", "Pubs", "Apts"]
            entry_name_base = get_base_name(entry_name)
            for collection_prefix in collections_prefixes:
                for collection in bpy.data.collections:
                    if collection.name.startswith(collection_prefix):
                        for obj in collection.objects:
                            obj_name_base = get_base_name(obj.name)
                            if entry_name_base == obj_name_base:
                                return collection_prefix
            return "Desconocido"

        # Obtener el gráfico de evaluación
        depsgraph = bpy.context.evaluated_depsgraph_get()

        # Inicializar contadores
        entries_count_by_type = {"CHS": 0, "Walls": 0, "Pubs": 0, "Apts": 0}
        building_types_by_neighborhood = {}
        output_data = []

        # Recorrer barrios y edificios
        buildings = [obj for obj in bpy.data.collections["Buildings_Exp"].objects if obj.type == 'MESH']
        for obj in bpy.data.objects:
            if obj.name.startswith("R_BR_"):
                neighborhood_name = obj.name[5:]
                neighborhood_eval = obj.evaluated_get(depsgraph)

                matching_buildings = []
                building_types_by_neighborhood[neighborhood_name] = {"1x1": 0, "2x1": 0, "2x2": 0, "Errores": []}

                for building in buildings:
                    building_origin = building.matrix_world.translation
                    success, location, normal, poly_index = neighborhood_eval.ray_cast(building_origin, Vector((0, 0, -1)))
                    if not success:
                        continue

                    facades_collection = bpy.data.collections.get("Facades_Exp")
                    if not facades_collection:
                        continue

                    facades_inside = [facade for facade in facades_collection.objects if facade.type == 'MESH' and is_point_inside_volume(building, facade.location)]
                    entry_count = len(facades_inside)

                    if entry_count == 4:
                        building_types_by_neighborhood[neighborhood_name]["1x1"] += 1
                    elif entry_count == 6:
                        building_types_by_neighborhood[neighborhood_name]["2x1"] += 1
                    elif entry_count == 8:
                        building_types_by_neighborhood[neighborhood_name]["2x2"] += 1
                    else:
                        building_types_by_neighborhood[neighborhood_name]["Errores"].append(building.name)

                    # Construir fila para el CSV
                    building_row = [neighborhood_name, building.name]
                    for facade in facades_inside:
                        entry_type = get_type_from_name(facade.name)
                        nomenclature = None
                        letters_collection = bpy.data.collections.get("Letters_Exp")
                        if letters_collection:
                            for letter in letters_collection.objects:
                                if letter.type == 'MESH' and is_point_inside_volume(facade, letter.location):
                                    nomenclature = letter.name.split('.')[0]
                                    break
                        building_row.extend([entry_type, facade.name, nomenclature or "N/A"])
                        if entry_type in entries_count_by_type:
                            entries_count_by_type[entry_type] += 1

                    # Rellenar columnas faltantes con "N/A"
                    while len(building_row) < 34:  # Máximo de 10 entradas (3 columnas por entrada)
                        building_row.extend(["N/A", "N/A", "N/A"])

                    output_data.append(building_row)

        # Escribir datos en archivo CSV
        csv_filepath = bpy.path.abspath(context.scene.export_csv_path + "reporte_entradas.csv")

        with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Sección 1: Detalle de edificios y entradas
            csv_writer.writerow(["Detalle de edificios y entradas"])
            headers = ["Barrio", "Edificio"]
            for i in range(1, 11):  # Máximo 10 entradas
                headers.extend([f"Tipo {i}", f"Nombre {i}", f"Placa {i}"])
            csv_writer.writerow(headers)
            for row in output_data:
                csv_writer.writerow(row)

            # Sección 2: Reporte general de las entradas por tipo
            csv_writer.writerow([])
            csv_writer.writerow(["Reporte general de las entradas por tipo"])
            csv_writer.writerow(["Tipo de Entrada", "Cantidad"])
            for entry_type, count in entries_count_by_type.items():
                csv_writer.writerow([entry_type, count])

            # Sección 3: Reporte de edificios por barrios
            csv_writer.writerow([])
            csv_writer.writerow(["Reporte de edificios por barrios"])
            csv_writer.writerow(["Barrio", "1x1", "2x1", "2x2", "Errores"])
            for neighborhood, types in building_types_by_neighborhood.items():
                error_count = len(types["Errores"])
                csv_writer.writerow([neighborhood, types["1x1"], types["2x1"], types["2x2"], error_count])

        self.report({'INFO'}, f"Archivo CSV generado: {csv_filepath}")
        return {'FINISHED'}
    
    # ------------------------------------------------------------
# NUEVO: lista de clases que exporta este módulo
# ------------------------------------------------------------
classes = (
    OBJECT_OT_generate_csv_report,
)

