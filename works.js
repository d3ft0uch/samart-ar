// Каталог работ выставки.
// Добавляешь работу — добавляешь запись сюда и кладёшь GLB в models/.
// QR для работы ведёт на: https://твой-сайт/viewer.html?id=КЛЮЧ

const WORKS = {
  "1": {
    title: "Объект 1",
    author: "— замени подпись —",
    description: "— замени описание —",
    model: "models/obj1.glb",
    usdz: "models/obj1.usdz",
  },
  "2": {
    title: "Объект 2",
    author: "— замени подпись —",
    description: "— замени описание —",
    model: "models/obj2.glb",
    usdz: "models/obj2.usdz",
  },
  "3": {
    title: "Объект 3",
    author: "— замени подпись —",
    description: "— замени описание —",
    model: "models/obj3.glb",
    usdz: "models/obj3.usdz",
  },
  "4": {
    title: "Объект 4",
    author: "— замени подпись —",
    description: "— замени описание —",
    model: "models/obj4.glb",
    usdz: "models/obj4.usdz",
  },
};

// Конфиг для room.html — MindAR image tracking по фото зон/фрагментов интерьера.
// Каждый spot — свой image-таргет + свой 3D-объект.
// Порядок spots ДОЛЖЕН совпадать с порядком картинок, из которых собран mindFile:
// первая картинка → targetIndex 0 → spots[0], и т.д. См. README про перекомпиляцию.
//
// position/rotation — вынос объекта относительно центра узнанного фото
// (координаты MindAR: X — вправо, Y — вверх, Z — от плоскости фото к камере;
// единица ≈ ширина маркера, т.е. если маркер 40 см — 1.0 = 40 см).
const ROOM_CONFIG = {
  mindFile: "targets/room.mind",
  spots: [
    {
      title: "Зона 1",
      model: "models/obj1.glb",
      scale: "0.5 0.5 0.5",
      position: "0 0 0",
      rotation: "0 0 0",
    },
    {
      title: "Зона 2",
      model: "models/obj2.glb",
      scale: "0.5 0.5 0.5",
      position: "0 0 0",
      rotation: "0 0 0",
    },
    {
      title: "Зона 3",
      model: "models/obj3.glb",
      scale: "0.5 0.5 0.5",
      position: "0 0 0",
      rotation: "0 0 0",
    },
    {
      title: "Зона 4",
      model: "models/obj4.glb",
      scale: "0.5 0.5 0.5",
      position: "0 0 0",
      rotation: "0 0 0",
    },
  ],
};
