import bpy, os

OBJ_FILE = r"C:\Users\mitch\OneDrive\Desktop\van.obj"
OUTPUT_DIR = r"C:\Users\mitch\OneDrive\Desktop"

EXTERIOR_FACES = 150000

INTERIOR_KW = ['interior','door_front_left_panelling','door_front_R_panelling',
    'door_front_left_Box','door_front_R_Box','door_front_left_compactor',
    'door_front_R_compactor','door_front_left_lock','door_front_r_lock',
    'Brake_disk','nut0','Water tank','Counter-top','Splashback','BUSHMAN',
    'WA 1','WA 2','L door','R Door','L Door','attobj','Object00','level0',
    'Reflector','reflector','lamp1','lamp2']

SKIP_KW = ['Reflector','reflector','boot_light_glass_part',
    'MeshBody258','MeshBody272','MeshBody257','MeshBody259',
    'MeshBody263','MeshBody265','MeshBody273','MeshBody274',
    'gage_panel','indicator_panel','front_panel','steering',
    'seat_belt','boot_floor','boot_light']

def is_interior(n):
    for k in INTERIOR_KW:
        if k.lower() in n.lower():
            return True
    return False

def is_skip(n):
    for k in SKIP_KW:
        if k.lower() in n.lower():
            return True
    return False

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def imp():
    print("Importing...")
    bpy.ops.wm.obj_import(filepath=OBJ_FILE)
    print("Done: " + str(len(bpy.context.scene.objects)) + " objects")

def get_van_scale():
    # Measure the OBJ van to get scale reference
    box_min = [9999,9999,9999]
    box_max = [-9999,-9999,-9999]
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            for v in o.bound_box:
                wv = o.matrix_world @ bpy.types.Object.matrix_world.fget(o).inverted() @ bpy.mathutils.Vector(v) if False else [v[0]+o.location[0], v[1]+o.location[1], v[2]+o.location[2]]
                for i in range(3):
                    if wv[i] < box_min[i]: box_min[i] = wv[i]
                    if wv[i] > box_max[i]: box_max[i] = wv[i]
    cx = (box_min[0]+box_max[0])/2
    cy = (box_min[1]+box_max[1])/2
    cz = (box_min[2]+box_max[2])/2
    sz_x = box_max[0]-box_min[0]
    sz_y = box_max[1]-box_min[1]
    sz_z = box_max[2]-box_min[2]
    print("Van centre: " + str(round(cx,1)) + "," + str(round(cy,1)) + "," + str(round(cz,1)))
    print("Van size: " + str(round(sz_x,1)) + "x" + str(round(sz_y,1)) + "x" + str(round(sz_z,1)))
    return cx, cy, cz, sz_x, sz_y, sz_z

def make_bed_and_extras(cx, cy, cz, sx, sy, sz):
    # Scale factors based on actual van dimensions
    # Ford Transit is ~5.5m long, ~2m wide, ~2.3m tall in real life
    # OBJ units vary - use sz (height) as reference, real height ~230cm
    unit = sz / 230.0  # 1 real cm in OBJ units

    # Bed platform - rear 1/3 of van, full width, ~60cm above floor
    bed_w = sx * 0.82
    bed_l = sy * 0.38
    bed_h = unit * 6
    bed_x = cx
    bed_y = cy - sy * 0.28
    bed_z = cz - sz * 0.1

    bpy.ops.mesh.primitive_cube_add(size=1)
    bed = bpy.context.active_object
    bed.name = 'BedPlatform'
    bed.scale = (bed_w, bed_l, bed_h)
    bed.location = (bed_x, bed_y, bed_z)

    # Mattress on top of bed
    bpy.ops.mesh.primitive_cube_add(size=1)
    matt = bpy.context.active_object
    matt.name = 'Mattress'
    matt.scale = (bed_w * 0.96, bed_l * 0.96, unit * 10)
    matt.location = (bed_x, bed_y, bed_z + bed_h * 0.5 + unit * 5)

    # Pillow 1 - left
    bpy.ops.mesh.primitive_cube_add(size=1)
    p1 = bpy.context.active_object
    p1.name = 'Pillow1'
    p1.scale = (bed_w * 0.35, unit * 50, unit * 8)
    p1.location = (cx - bed_w * 0.22, bed_y + bed_l * 0.38, bed_z + bed_h * 0.5 + unit * 18)

    # Pillow 2 - right
    bpy.ops.mesh.primitive_cube_add(size=1)
    p2 = bpy.context.active_object
    p2.name = 'Pillow2'
    p2.scale = (bed_w * 0.35, unit * 50, unit * 8)
    p2.location = (cx + bed_w * 0.22, bed_y + bed_l * 0.38, bed_z + bed_h * 0.5 + unit * 18)

    # Overhead shelf above cab seats - front area, high up
    shelf_w = sx * 0.75
    shelf_l = sy * 0.18
    shelf_h = unit * 8
    bpy.ops.mesh.primitive_cube_add(size=1)
    shelf = bpy.context.active_object
    shelf.name = 'OverheadShelf'
    shelf.scale = (shelf_w, shelf_l, shelf_h)
    shelf.location = (cx, cy + sy * 0.32, cz + sz * 0.33)

    # Shower rail - rear left corner, vertical
    bpy.ops.mesh.primitive_cylinder_add(radius=unit*2, depth=unit*90)
    rail = bpy.context.active_object
    rail.name = 'ShowerRail'
    rail.location = (cx - sx * 0.38, cy - sy * 0.42, cz + unit * 5)

    # Shower head - top of rail
    bpy.ops.mesh.primitive_cylinder_add(radius=unit*8, depth=unit*3)
    head = bpy.context.active_object
    head.name = 'ShowerHead'
    head.location = (cx - sx * 0.38, cy - sy * 0.42, cz + unit * 50)
    head.rotation_euler = (1.5708, 0, 0)

    print("Added bed, mattress, pillows, overhead shelf and shower")

def run(objects, faces, name):
    if not objects:
        print("No objects: " + name)
        return
    print("Processing: " + name)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    cur = len(obj.data.polygons)
    print("Faces before: " + str(cur))
    if cur > faces:
        r = float(faces) / float(cur)
        m = obj.modifiers.new("D", 'DECIMATE')
        m.ratio = r
        bpy.ops.object.modifier_apply(modifier="D")
        print("Faces after: " + str(len(obj.data.polygons)))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    p = os.path.join(OUTPUT_DIR, name)
    bpy.ops.export_scene.gltf(filepath=p, use_selection=True, export_format='GLB', export_normals=True)
    print("Saved: " + p)
    bpy.ops.object.delete()

print("== EXTERIOR ==")
clear()
imp()
cx, cy, cz, sx, sy, sz = get_van_scale()
make_bed_and_extras(cx, cy, cz, sx, sy, sz)
objs = []
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        if not is_interior(o.name):
            if not is_skip(o.name):
                objs.append(o)
print("Count: " + str(len(objs)))
run(objs, EXTERIOR_FACES, 'van_exterior.glb')
print("== DONE ==")
