import bpy
import re
import math
import mathutils
from mathutils import Vector


def clean_duplicates(collection, tolerance=0.01):
    unique_positions = {}
    for obj in collection.objects:
        position = obj.location  # Ya es un Vector
        frozen_position = position.copy()  # Crear una copia del vector
        frozen_position.freeze()  # Congelar el vector para que sea inmutable
        found_duplicate = False
        
        # Compara la distancia con los objetos previamente guardados
        for existing_pos, existing_obj in unique_positions.items():
            # Calcular la distancia usando la longitud del vector de la diferencia
            distance = (position - existing_pos).length
            if distance <= tolerance:
                # Si está dentro de la tolerancia, se considera duplicado y se elimina el objeto
                bpy.data.objects.remove(obj, do_unlink=True)
                found_duplicate = True
                break
        
        # Si no se encontró duplicado, se guarda la posición y el objeto
        if not found_duplicate:
            unique_positions[frozen_position] = obj



def expand_volume(container, expansion):
    """Expandir el volumen del contenedor añadiendo un margen de expansión"""
    bbox_corners = [Vector(corner) for corner in container.bound_box]
    min_corner = Vector([min(corner[i] for corner in bbox_corners) for i in range(3)])
    max_corner = Vector([max(corner[i] for corner in bbox_corners) for i in range(3)])
    expanded_min = min_corner - expansion
    expanded_max = max_corner + expansion
    return expanded_min, expanded_max

def is_point_inside_expanded_volume(expanded_min, expanded_max, point):
    return all(expanded_min[i] <= point[i] <= expanded_max[i] for i in range(3))

def is_point_inside_volume(container, point, expansion=Vector((0.01, 0.01, 0.01))):
    expanded_min, expanded_max = expand_volume(container, expansion)
    inv_mat = container.matrix_world.inverted()
    local_point = inv_mat @ point
    return is_point_inside_expanded_volume(expanded_min, expanded_max, local_point)

def clean_objects():
    facades_collection = bpy.data.collections.get("Facades_Exp")
    plates_collection = bpy.data.collections.get("Plates_Exp")
    letters_collection = bpy.data.collections.get("Letters_Exp")
    
    wall_collections = [
        bpy.data.collections.get("Walls_1x1"),
        bpy.data.collections.get("Walls_2x1"),
        bpy.data.collections.get("Walls_2x2")
    ]
    
    # Verifica si las colecciones existen
    if not facades_collection or not plates_collection or not letters_collection:
        print("Faltan colecciones necesarias.")
        return

    # Combinar los objetos de las colecciones de "Walls"
    walls_objects = []
    for wall_collection in wall_collections:
        if wall_collection:
            walls_objects.extend([obj for obj in wall_collection.objects if obj.type == 'MESH'])
    
    if not walls_objects:
        print("No se encontraron objetos de pared.")
        return
    
    walls_names = {obj.name.split(".")[0] for obj in walls_objects}
    facades_to_check = [f for f in facades_collection.objects if f.type == 'MESH' and f.name.split(".")[0] in walls_names]
    
    if not facades_to_check:
        print("No se encontraron fachadas coincidentes.")
        return

    plates_to_remove = set()
    letters_to_remove = set()
    
    for facade in facades_to_check:
        # Usar el pivote de la fachada para verificar las placas dentro del área
        plates_inside = [p for p in plates_collection.objects if p.type == 'MESH' and is_point_inside_volume(facade, p.location)]
        for plate in plates_inside:
            plates_to_remove.add(plate)
            
            # Encontrar letras dentro de cada placa
            letters_inside = [l for l in letters_collection.objects if l.type == 'FONT' and is_point_inside_volume(plate, l.location)]
            letters_to_remove.update(letters_inside)
    
    # Eliminar las placas y letras encontradas
    for plate in plates_to_remove:
        bpy.data.objects.remove(plate, do_unlink=True)
    
    for letter in letters_to_remove:
        bpy.data.objects.remove(letter, do_unlink=True)
    
    print(f"Placas y letras eliminadas. {len(plates_to_remove)} placas y {len(letters_to_remove)} letras.")


def find_building_number(building, numbers_collection):
    for obj in numbers_collection.objects:
        if obj.type == 'FONT' and is_point_inside_volume(building, obj.location):
            match = re.match(r'(\d+)', obj.name)
            if match:
                return match.group(1)
    return None

def find_letter_A_in_building(building, letters_collection):
    for letter in letters_collection.objects:
        if letter.type == 'FONT' and is_point_inside_volume(building, letter.location):
            if letter.data.body.startswith("A"):
                return letter
    return None

def get_angle_from_center(obj, center):
    vec = obj.location - center
    return math.atan2(vec.y, vec.x)

def sort_letters_ccw(letters, center):
    return sorted(letters, key=lambda l: get_angle_from_center(l, center))

def update_text_content(obj):
    duplicated_obj = obj.copy()
    duplicated_obj.data = obj.data.copy()
    duplicated_obj.animation_data_clear()
    duplicated_obj.location = obj.location
    duplicated_obj.rotation_euler = obj.rotation_euler
    duplicated_obj.scale = obj.scale
    duplicated_obj.name = obj.name.split(".")[0]
    duplicated_obj.data.body = obj.name.split(".")[0]
    bpy.context.collection.objects.link(duplicated_obj)
    return duplicated_obj

def apply_decimate_planar_to_letters():
    letters_collection = bpy.data.collections.get("Letters_Exp")
    
    if not letters_collection:
        print("La colección Letters_Exp no existe.")
        return
    
    for letter in letters_collection.objects:
        if letter.type != 'FONT':
            continue
        
        try:
            # Asegurar que el objeto esté seleccionado y activo
            bpy.context.view_layer.objects.active = letter
            letter.select_set(True)
            
            # Cambiar al modo objeto
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Convertir a mesh
            bpy.context.view_layer.objects.active = letter
            bpy.ops.object.convert(target='MESH')
            
            # Aplicar Decimate planar
            decimate_mod = letter.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_mod.decimate_type = 'DISSOLVE'
            decimate_mod.angle_limit = math.radians(1.0)
            
            # Aplicar el modificador
            bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
            
            # Deseleccionar el objeto después de aplicarle el decimate
            letter.select_set(False)
        
        except RuntimeError as e:
            print(f"Error al procesar el objeto '{letter.name}': {e}")
            continue

    print("Se ha aplicado Decimate planar a las letras en Letters_Exp.")



class OBJECT_OT_rename_plates(bpy.types.Operator):
    bl_idname = "object.rename_plates"
    bl_label = "Rename Plates"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Renombra las placas según Figma y limpia las placas que van en paredes"

    @classmethod
    def poll(cls, context):
        # Verifica si hay objetos en al menos una de las colecciones especificadas
        collection_names = ["Letters_Exp"]
        for name in collection_names:
            collection = bpy.data.collections.get(name)
            if collection and len(collection.objects) == 0:
                return True
        return True

    def execute(self, context):
        buildings_collection = bpy.data.collections.get("Buildings_Exp")
        facades_collection = bpy.data.collections.get("Facades_Exp")
        plates_collection = bpy.data.collections.get("Plates_Exp")
        numbers_collection = bpy.data.collections.get("Numbers_Exp")
        letters_collection = bpy.data.collections.get("Letters_Exp")
        
        if not buildings_collection or not facades_collection or not plates_collection or not numbers_collection or not letters_collection:
            self.report({'ERROR'}, "Collections Buildings_Exp, Facades_Exp, Plates_Exp, Numbers_Exp, or Letters_Exp are missing")
            return {'CANCELLED'}
        
        clean_duplicates(letters_collection)
        
        try:
            for building in buildings_collection.objects:
                if building.type == 'MESH':
                    Ned = find_building_number(building, numbers_collection)
                    if not Ned:
                        self.report({'WARNING'}, f"No se encontró número para el edificio: {building.name}")
                        continue
                    
                    facades_inside = [facade for facade in facades_collection.objects if facade.type == 'MESH' and is_point_inside_volume(building, facade.location, expansion=Vector((0.01, 0.01, 0.01)))]
                    if not facades_inside:
                        self.report({'WARNING'}, f"No se encontraron fachadas dentro del edificio: {building.name}")
                        continue
                    
                    plates_inside = [plate for facade in facades_inside for plate in plates_collection.objects if plate.type == 'MESH' and is_point_inside_volume(facade, plate.location, expansion=Vector((0.01, 0.01, 0.01)))]
                    if not plates_inside:
                        self.report({'WARNING'}, f"No se encontraron placas dentro del edificio: {building.name}")
                        continue
                    
                    letters_inside = [letter for plate in plates_inside for letter in letters_collection.objects if letter.type == 'FONT' and is_point_inside_volume(plate, letter.location)]
                    
                    if not letters_inside:
                        letter_A = find_letter_A_in_building(building, letters_collection)
                        if not letter_A:
                            self.report({'WARNING'}, f"No se encontró la letra 'A' dentro del edificio: {building.name}")
                            continue
                        letters_inside.append(letter_A)
                    
                    center = building.matrix_world.translation
                    sorted_letters = sort_letters_ccw(letters_inside, center)
                    
                    start_index = None
                    for i, letter in enumerate(sorted_letters):
                        if letter.data.body.startswith("A"):
                            start_index = i
                            break
                        
                    if start_index is None:
                        self.report({'WARNING'}, f"No se encontró la letra 'A' dentro del edificio: {building.name}")
                        continue
                    
                    duplicated_letters = []
                    for i in range(len(sorted_letters)):
                        index = (start_index + i) % len(sorted_letters)
                        letter = sorted_letters[index]
                        new_name = f"{Ned}-{chr(65 + i)}"
                        letter.name = new_name
                        duplicated_obj = update_text_content(letter)
                        duplicated_letters.append(duplicated_obj)
                    
                    for letter in sorted_letters:
                        bpy.data.objects.remove(letter, do_unlink=True)
            
            clean_objects()
            
            # Al final, aplicar el Decimate planar a las letras
            apply_decimate_planar_to_letters()
            
            self.report({'INFO'}, "Placas renombradas y duplicadas exitosamente")
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Se produjo un error: {str(e)}")
            return {'CANCELLED'}



