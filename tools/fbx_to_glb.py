"""Импорт FBX → decimate + downscale текстур → экспорт GLB (Draco + WebP)
и опционально USDZ для iOS AR Quick Look.

Запуск (пример):
  /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/fbx_to_glb.py -- \
    --in obj1.fbx --out models/obj1.glb --usdz models/obj1.usdz \
    --decimate 0.2 --tex 1024
"""
import bpy, sys, os, argparse

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument("--in", dest="inp", required=True)
p.add_argument("--out", dest="out", required=True, help="путь к GLB")
p.add_argument("--usdz", dest="usdz", default=None, help="путь к USDZ (для iOS Quick Look)")
p.add_argument("--decimate", type=float, default=0.2, help="0..1, чем меньше — тем сильнее упрощение")
p.add_argument("--tex", type=int, default=1024, help="максимальная сторона текстуры, px")
args = p.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)

# Обход бага FBX-импортера Blender 5.0: blen_read_light() лезет к
# lamp.cycles.cast_shadow, удалённому в 5.0. Оборачиваем функцию так,
# чтобы AttributeError не роняла весь импорт — просто возвращаем базовую лампу.
try:
    import io_scene_fbx.import_fbx as _ifbx
    _orig_blen_read_light = _ifbx.blen_read_light
    def _safe_blen_read_light(fbx_tmpl, fbx_obj, settings):
        try:
            return _orig_blen_read_light(fbx_tmpl, fbx_obj, settings)
        except AttributeError as e:
            print(f"[warn] пропускаю свойство лампы: {e}")
            return bpy.data.lights.new(name="fbx_light", type="POINT")
    _ifbx.blen_read_light = _safe_blen_read_light
except Exception as e:
    print(f"[warn] не удалось поставить обход blen_read_light: {e}")

bpy.ops.import_scene.fbx(filepath=args.inp)

# Decimate всем мешам
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if args.decimate and args.decimate < 1.0:
        m = o.modifiers.new("dec", "DECIMATE")
        m.ratio = args.decimate
        with bpy.context.temp_override(object=o, selected_objects=[o], selected_editable_objects=[o]):
            bpy.ops.object.modifier_apply(modifier=m.name)

# Downscale packed images
for img in list(bpy.data.images):
    w, h = img.size
    if w == 0 or h == 0:
        continue
    m = max(w, h)
    if m <= args.tex:
        continue
    scale = args.tex / m
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    img.scale(nw, nh)
    print(f"[scale] {img.name}: {w}x{h} -> {nw}x{nh}")

# Считаем итог
tris = 0
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    o.data.calc_loop_triangles()
    tris += len(o.data.loop_triangles)
print(f"[after] meshes={sum(1 for o in bpy.data.objects if o.type=='MESH')} tris={tris}")

os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

# GLB export c Draco + WebP
bpy.ops.export_scene.gltf(
    filepath=args.out,
    export_format="GLB",
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14,
    export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=12,
    export_image_format="WEBP",
    export_image_quality=80,
    export_apply=True,
    export_yup=True,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
)
sz = os.path.getsize(args.out)
print(f"[done] wrote {args.out} ({sz/1024/1024:.2f} MB)")

if args.usdz:
    os.makedirs(os.path.dirname(args.usdz) or ".", exist_ok=True)

    # USD-экспортер копирует текстуры С ДИСКА по img.filepath.
    # Если FBX содержал packed-текстуры со сломанной ссылкой на исходник
    # (типичный кейс: путь к .fbm/ папке, которой нет рядом) — USDZ выйдет
    # без текстур. Пересохраняем все images во временную папку и переклеиваем
    # filepath на них, чтобы экспортер точно нашёл файлы.
    import tempfile
    _texdir = tempfile.mkdtemp(prefix="samart-tex-")
    for img in bpy.data.images:
        w, h = img.size
        if w == 0 or h == 0:
            continue
        name = img.name
        if not name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            name += ".png"
            img.file_format = "PNG"
        p = os.path.join(_texdir, name)
        img.filepath_raw = p
        img.save()
    print(f"[usdz] пересохранил {sum(1 for i in bpy.data.images if i.size[0])} текстур в {_texdir}")

    # iOS AR Quick Look:
    # - расширение .usdz — Blender сам упакует в zip;
    # - generate_preview_surface=True — читаемо для Quick Look (MaterialX им пока не нужен);
    # - usdz_downscale_size — верхняя граница стороны текстуры внутри архива,
    #   ставим тот же лимит, что и для GLB, чтобы файл не разбухал;
    # - Y-up: iOS QL по умолчанию ждёт Y-up, оставляем дефолт.
    downscale = "CUSTOM"
    bpy.ops.wm.usd_export(
        filepath=args.usdz,
        export_animation=False,
        export_hair=False,
        export_uvmaps=True,
        export_normals=True,
        export_materials=True,
        export_lights=False,
        export_cameras=False,
        export_curves=False,
        export_points=False,
        export_volumes=False,
        generate_preview_surface=True,
        generate_materialx_network=False,
        export_textures_mode="NEW",
        overwrite_textures=True,
        relative_paths=True,
        triangulate_meshes=True,
        usdz_downscale_size=downscale,
        usdz_downscale_custom_size=args.tex,
        evaluation_mode="RENDER",
    )
    sz2 = os.path.getsize(args.usdz)
    print(f"[done] wrote {args.usdz} ({sz2/1024/1024:.2f} MB)")
