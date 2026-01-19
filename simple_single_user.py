import bpy

# Seleccionar la colección activa
active_layer = bpy.context.view_layer.active_layer_collection
if not active_layer:
    print("Error: No hay una colección activa")
else:
    collection = active_layer.collection
    processed_count = 0
    
    print(f"Procesando colección: {collection.name}")
    
    # Deseleccionar todo primero
    bpy.ops.object.select_all(action='DESELECT')
    
    # Seleccionar todos los objetos MESH en la colección
    mesh_objects = [obj for obj in collection.objects if obj.type == 'MESH' and obj.data]
    
    for obj in mesh_objects:
        obj.select_set(True)
    
    if mesh_objects:
        # Hacer single user de los datos (equivalente al botón Single User + Copy)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
        
        # Resetear escala
        bpy.ops.object.scale_clear()
        
        print(f"  - Single user aplicado a {len(mesh_objects)} objetos")
        processed_count = len(mesh_objects)
        
        # Deseleccionar todo al final
        bpy.ops.object.select_all(action='DESELECT')
    
    print(f"Completado: {processed_count} objetos procesados en '{collection.name}'")
