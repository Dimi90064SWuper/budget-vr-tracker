# Budget VR Tracker

DIY система трекинга для VR на основе обычной веб-камеры и камеры смартфона.

## 🎯 Возможности

- **Трекинг рук** — MediaPipe Hands, 21 точка на каждой руке
- **Трекинг ног** — MediaPipe Pose, отслеживание стоп для full-body tracking
- **Две камеры** — веб-камера ПК для рук, телефон для ног
- **SteamVR интеграция** — 4 виртуальных устройства (2 контроллера + 2 трекера)
- **Калибровка** — T-поза для определения масштаба
- **Низкая задержка** — целевая latency < 20ms
- **Веб-интерфейс** — 3D визуализация в браузере

## 🚀 Быстрый старт

```bash
# Установка зависимостей
sudo apt install -y python3.10 python3.10-venv build-essential cmake nlohmann-json3-dev
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Загрузка моделей MediaPipe
./download_models.sh

# Сборка драйвера
cd driver && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Установка драйвера
python ../tools/install_driver.py

# Запуск с веб-интерфейсом
./run_tracker.sh
```

## 📁 Структура

```
budget-vr-tracker/
├── tracker/              # Python tracking pipeline
│   ├── main.py          # Точка входа
│   ├── camera_manager.py # Управление камерами
│   ├── hand_tracker.py   # MediaPipe Hands
│   ├── pose_tracker.py   # MediaPipe Pose
│   ├── coordinate_fusion.py
│   ├── steamvr_bridge.py # UDP мост
│   ├── calibration.py    # T-поза калибровка
│   ├── config.py         # Конфигурация
│   └── web_viewer.py     # 3D визуализация
│
├── driver/               # C++ OpenVR driver
│   ├── CMakeLists.txt
│   └── src/
│       ├── main.cpp
│       ├── device_provider.cpp
│       ├── controller_device.cpp
│       ├── tracker_device.cpp
│       └── pipe_server.cpp
│
├── tools/
│   ├── install_driver.py
│   └── calibration_wizard.py
│
├── tests/
├── docs/
└── README.md
```

## 🛠️ Требования

- **ОС**: Linux (Ubuntu 20.04+, Fedora 35+)
- **Python**: 3.10+
- **C++**: GCC 11+, CMake 3.20+
- **SteamVR**: установлен и настроен

## 📚 Документация

- [WEB_VIEWER.md](docs/WEB_VIEWER.md) — 3D визуализация в браузере
- [GITHUB_SETUP.md](docs/GITHUB_SETUP.md) — Инструкция по push на GitHub

## 🔧 Настройка

### Конфигурация

Файл: `~/.budget_vr/config.yaml`

```yaml
cameras:
  webcam:
    index: 0
    width: 1280
    height: 720
  phone:
    url: "http://192.168.1.100:8080/video"
    enabled: true

bridge:
  mode: "udp"
  udp_port: 57011

smoothing:
  alpha: 0.7
  position_deadzone_m: 0.005
```

## 🐛 Устранение проблем

### Камера не работает

```bash
# Проверка камер
ls -l /dev/video*

# Тест
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.read()[0] else 'FAIL')"
```

### Драйвер не виден в SteamVR

```bash
# Проверка сборки
ls driver/build/bin/linux64/driver_budget_vr_tracker.so

# Переустановка
python tools/install_driver.py
```

## 📝 Лицензия

MIT License
