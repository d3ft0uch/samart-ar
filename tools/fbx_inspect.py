"""Импорт FBX в пустую сцену и краткий отчёт по содержимому.
Запуск: /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/fbx_inspect.py -- <fbx>
"""
import bpy, sys, os

argv = sys.argv[sys.argv.index("--") + 1:]
fbx = argv[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
tris = 0
for o in meshes:
    o.data.calc_loop_triangles()
    tris += len(o.data.loop_triangles)

print(f"[stat] objects={len(bpy.data.objects)} meshes={len(meshes)} mats={len(bpy.data.materials)} images={len(bpy.data.images)} tris={tris}")
for img in bpy.data.images:
    src = img.filepath or "(packed)"
    print(f"[img] {img.name!r} size={tuple(img.size)} channels={img.channels} src={src} packed={bool(img.packed_file)}")
for m in bpy.data.materials:
    print(f"[mat] {m.name!r}")
