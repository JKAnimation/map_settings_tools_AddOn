import bpy
import re
import os

addon_directory = os.path.dirname(__file__)
blend_file_path = os.path.join(addon_directory, "Map_basics.blend")

def join_objects(objects, new_name):
    """Join selected objects into a single mesh and rename it."""
    if not objects:
        return  # No objects to join

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select objects to join
    for obj in objects:
        if obj and obj.type == 'MESH':  # Ensure object is a mesh
            obj.select_set(True)

    if len(objects) > 0:
        # Set the active object to the first one in the list and join
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()

        # Rename the resulting object and its mesh data
        joined_obj = bpy.context.active_object
        if joined_obj:
            joined_obj.name = new_name
            joined_obj.data.name = new_name

def transform_and_convert_objects(objects):
    """Convert curves to meshes, scale, and rotate selected objects."""
    for obj in objects:
        if obj.type == 'CURVE':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            if obj.name!= "R_TransportPath":
                bpy.ops.object.convert(target='MESH')

        # Ensure mesh data name matches object name after conversion
        obj.data.name = obj.name

        bpy.context.view_layer.objects.active = obj
        bpy.ops.transform.resize(value=(400, 400, 400))
        bpy.ops.transform.rotate(value=3.14159, orient_axis='Z')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.select_set(False)

def group_objects_by_base_name(objects):
    """Group objects by base name, removing numeric suffixes."""
    grouped_objects = {}
    name_pattern = re.compile(r'(.+?)(?:\.\d+)?$')  # Pattern to remove numeric suffixes

    for obj in objects:
        if obj and obj.name in bpy.data.objects:  # Check if the object exists
            base_name = name_pattern.match(obj.name).group(1)
            if base_name not in grouped_objects:
                grouped_objects[base_name] = []
            grouped_objects[base_name].append(obj)

    return grouped_objects

def add_decimate_modifier_and_duplicate(obj):
    """Add a decimation modifier and create duplicates of the object."""
    # Add decimation modifier
    mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
    mod.decimate_type = 'DISSOLVE'
    mod.angle_limit = 0.05  # Adjust angle if needed

    # Apply modifier
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # Create duplicates and rename them
    new_names = ["Street", "Special", "Green"]
    duplicates = []
    
    # Load the "Zone" node group if not already loaded
    if "Zone" not in bpy.data.node_groups:
        bpy.ops.wm.append(
            filepath=os.path.join(blend_file_path, "NodeTree", "Zone"),
            directory=os.path.join(blend_file_path, "NodeTree"),
            filename="Zone"
        )
    
    # Add the "Zone" node group to the object
    zone_modifier = obj.modifiers.new(name="Zone", type='NODES')
    zone_modifier.node_group = bpy.data.node_groups.get("Zone")



    for name in new_names:
        copy_obj = obj.copy()
        copy_obj.data = obj.data.copy()  # Also copy the mesh data
        bpy.context.collection.objects.link(copy_obj)
        copy_obj.name = name
        copy_obj.data.name = name  # Ensure mesh data name matches object name
        duplicates.append(copy_obj)
    
    
    # Rename the original object
    obj.name = "River"
    obj.data.name = "River"  # Ensure mesh data name matches object name

    # Create or find "Blocking" collection
    if "Blocking" not in bpy.data.collections:
        blocking_collection = bpy.data.collections.new(name="Blocking")
        bpy.context.scene.collection.children.link(blocking_collection)
    else:
        blocking_collection = bpy.data.collections["Blocking"]

    # Move all objects to the "Blocking" collection
    for o in [obj] + duplicates:
        for col in o.users_collection:
            col.objects.unlink(o)
        blocking_collection.objects.link(o)

def add_uv_map(obj):
    """Add a UV Map to the object if it doesn't have one."""
    if obj.type == 'MESH':
        uv_layers = obj.data.uv_layers
        if len(uv_layers) == 0:
            # Add a UV map if none exists
            uv_layers.new(name="UVMap")
        else:
            # Ensure the first UV map is active
            uv_layers.active = uv_layers[0]

class OBJECT_OT_standard_settings(bpy.types.Operator):
    """Operator to scale and apply transformations to objects in the active collection, removing unnecessary ones and joining specific ones."""
    bl_idname = "object.standard_settings"
    bl_label = "Standard Settings"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Scales and applies transformations to objects in the active collection, removes unnecessary ones, and joins specific ones."

    def execute(self, context):
        # Get the active collection
        active_collection = context.collection
        if not active_collection:
            self.report({'ERROR'}, "No active collection")
            return {'CANCELLED'}


        # Filter objects to keep (start with "R_") and delete (don't start with "R_" or are not "R_Base_Streets")
        objects_to_keep = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_")]
        objects_to_delete = [obj for obj in active_collection.objects if obj and not obj.name.startswith("R_") and not obj.name.startswith("R_Base_Streets")]

        # Delete objects that don't start with "R_"
        for obj in objects_to_delete:
            if obj and obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Refresh the list of objects to keep after deletions
        objects_to_keep = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_")]

        # Convert all remaining objects to mesh and apply transformations
        transform_and_convert_objects(objects_to_keep)

        # Ensure all mesh data names match their object names
        for obj in objects_to_keep:
            if obj.type == 'MESH' and obj.name in bpy.data.objects:
                obj.data.name = obj.name
            if obj.name=="R_River" or "R_Green" or "R_Land":
                mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
                mod.decimate_type = 'DISSOLVE'
                mod.angle_limit = 0.05  # Adjust angle if needed
        
        # Locate the "R_Limit_Barrier" object
        r_limit_barrier = bpy.data.objects.get("R_Limit_Barrier")
        if r_limit_barrier:
            add_uv_map(r_limit_barrier)  # Add UV map to the object

        # Find and process objects with prefix "R_Blocking" after conversion and transformation
        blocking_objects = [obj for obj in objects_to_keep if obj and obj.name.startswith("R_Blocking")]

        for blocking_obj in blocking_objects:
            if blocking_obj:
                add_decimate_modifier_and_duplicate(blocking_obj)

        # Create list of objects to join for "FullBuilding"
        full_building_objects = [obj for obj in objects_to_keep if obj and any(obj.name.startswith(prefix) for prefix in ["R_Ch", "R_Loc", "R_Pub", "R_Wall", "R_Build", "R_Apt", "R_Num"])]
        if full_building_objects:
            join_objects(full_building_objects, new_name="FullBuilding")

        # Join objects that start with "R_Mini_Games"
        mini_game_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_Mini_Games")]
        if mini_game_objects:
            join_objects(mini_game_objects, new_name="Minigames")

        # Join objects that start with "R_Green"
        green_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_Green")]
        if green_objects:
            join_objects(green_objects, new_name="R_Green")

        # Join objects that start with "R_River"
        land_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_River")]
        if land_objects:
            join_objects(land_objects, new_name="R_River")

        
        # Join objects that start with "R_Land"
        land_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_Land")]
        if land_objects:
            join_objects(land_objects, new_name="R_Land")

        
        # Join objects that start with "R_WOF_STOPS"
        wof_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_WOF_STOP")]
        if wof_objects:
            join_objects(wof_objects, new_name="WOF_STOPS")
        
        # Join objects that start with "R_bus"
        bus_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_Bus")]
        if bus_objects:
            join_objects(bus_objects, new_name="R_Bus")

        # Join objects that start with "R_Screen"
        screen_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_Screen")]
        if screen_objects:
            join_objects(screen_objects, new_name="Billboards")
        
        # Join objects that start with "R_WFame"
        screen_objects = [obj for obj in active_collection.objects if obj and obj.name.startswith("R_WFame")]
        if screen_objects:
            join_objects(screen_objects, new_name="WallFame")
        

        # Group objects by base name to join those with the same name except for the suffix
        grouped_objects = group_objects_by_base_name(objects_to_keep)

        # Join the grouped objects by base name
        for base_name, objs in grouped_objects.items():
            if len(objs) > 1:
                join_objects(objs, new_name=base_name)
            else:
                if objs[0]:
                    objs[0].name = base_name  # Ensure the base name is retained

        # Apply location transformations to each remaining mesh object
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_keep:
            if obj and obj.type == 'MESH':
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Force view update
        bpy.context.view_layer.update()


        self.report({'INFO'}, f"Standard settings applied to collection '{active_collection.name}'")

        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_standard_settings)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_standard_settings)

if __name__ == "__main__":
    register()
