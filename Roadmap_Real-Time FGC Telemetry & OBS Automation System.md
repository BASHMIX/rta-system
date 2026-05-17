# Project Roadmap: Real-Time FGC Telemetry & OBS Automation System

This document outlines the comprehensive architecture and execution plan for building a lightweight, real-time visual telemetry extractor and OBS automation tool. The system operates locally, avoiding CPU/GPU bottlenecks, and serves as a robust foundation for future AI integration.

---

## Phase 1: Technology Stack
*   **Core Backend:** Python 3.10+
*   **Video Transport:** `Spout-Python` (or `SpoutGL`) for zero-latency, VRAM-to-VRAM frame sharing.
*   **Computer Vision:** `OpenCV` (`cv2`) and `NumPy` for high-speed, matrix-based pixel masking and ROI (Region of Interest) cropping.
*   **Frontend / UI:** `CustomTkinter` (Modern, dark-mode native desktop GUI).
*   **OBS Integration:** `obsws-python` (OBS WebSocket v5 API) for triggering events, sources, and filters.

---

## Phase 2: User Interface (Configuration Workspace)
The UI is strictly a setup environment. Once configurations are saved, the UI can be minimized, shifting processing entirely to the lightweight backend worker thread.

### UI Layout & Components
1.  **Canvas Area (Spout Feed):** A central display mapping the live Spout output from OBS.
2.  **Toolbar / Tools:**
    *   **Draw Bounding Box:** Click and drag to define an ROI.
    *   **Assign Element Type:** Dropdown to label the drawn box (e.g., `Lifebar`, `Combo Counter`, `System Text`).
    *   **Set Logic Parameters:** Sliders/inputs to define logic rules for the selected box (e.g., `Segments: 4`, `Direction: Right-to-Left`, `Color Match: Green`).
3.  **The "Mirror" Utility:** 
    *   A dedicated button: **[Mirror P1 Data to P2]**.
    *   *Logic:* Calculates the exact opposite coordinates based on screen width (`Screen Width - X_coordinate`) and automatically flips the depletion direction (RTL becomes LTR).
4.  **Save & Compile:** Generates the `config.json` file and transitions the app into "Live Monitor" mode.

---

## Phase 3: Data Architecture (JSON Configuration Schema)
The configuration file acts as the single source of truth. It is loaded directly into the RAM when the monitoring loop starts, ensuring zero I/O delays.

```json
{
  "system": {
    "resolution": [1920, 1080],
    "target_fps": 30,
    "obs_websocket": {
      "host": "localhost",
      "port": 4455,
      "password": "your_secret_password"
    }
  },
  "players": {
    "P1": {
      "lifebar": {
        "roi": [100, 50, 800, 80], 
        "direction": "RTL",
        "segments": 4,
        "target_color_hsv_range": [[40, 50, 50], [80, 255, 255]] 
      },
      "system_text_zone": {
        "roi": [100, 300, 400, 350],
        "trigger_on_pixel_change": true
      }
    },
    "P2": {
      "lifebar": {
        "roi": [1120, 50, 1820, 80],
        "direction": "LTR",
        "segments": 4,
        "target_color_hsv_range": [[40, 50, 50], [80, 255, 255]]
      },
      "system_text_zone": {
        "roi": [1520, 300, 1820, 350],
        "trigger_on_pixel_change": true
      }
    }
  },
  "obs_events": [
    {
      "trigger": "P1_Life_Under_25",
      "condition": "P1.lifebar.current_percentage < 25",
      "actions": [
        {"type": "toggle_source", "scene": "Main_Gameplay", "source": "Red_Danger_Vignette", "state": true},
        {"type": "toggle_filter", "source": "Game_Capture", "filter": "Danger_Color_Correction", "state": true}
      ]
    },
    {
      "trigger": "Counter_Attack_Detected",
      "condition": "P1.system_text_zone.pixel_density_change > 50",
      "actions": [
        {"type": "toggle_source", "scene": "Main_Gameplay", "source": "Impact_Flash_WebM", "state": true}
      ]
    }
  ]
}


بالتأكيد! نظراً لأنني لا أستطيع إرسال ملفات مباشرة للتحميل عبر هذه المحادثة، قمت بتجهيز المحتوى بالكامل داخل صندوق كود (Code Block) بصيغة Markdown.

يمكنك ببساطة النقر على زر "نسخ" (Copy) في الزاوية العلوية لصندوق الكود، ولصقه في أي محرر نصوص (مثل VS Code أو حتى Notepad)، ثم حفظ الملف باسم roadmap.md.

Markdown
# Project Roadmap: Real-Time FGC Telemetry & OBS Automation System

This document outlines the comprehensive architecture and execution plan for building a lightweight, real-time visual telemetry extractor and OBS automation tool. The system operates locally, avoiding CPU/GPU bottlenecks, and serves as a robust foundation for future AI integration.

---

## Phase 1: Technology Stack
*   **Core Backend:** Python 3.10+
*   **Video Transport:** `Spout-Python` (or `SpoutGL`) for zero-latency, VRAM-to-VRAM frame sharing.
*   **Computer Vision:** `OpenCV` (`cv2`) and `NumPy` for high-speed, matrix-based pixel masking and ROI (Region of Interest) cropping.
*   **Frontend / UI:** `CustomTkinter` (Modern, dark-mode native desktop GUI).
*   **OBS Integration:** `obsws-python` (OBS WebSocket v5 API) for triggering events, sources, and filters.

---

## Phase 2: User Interface (Configuration Workspace)
The UI is strictly a setup environment. Once configurations are saved, the UI can be minimized, shifting processing entirely to the lightweight backend worker thread.

### UI Layout & Components
1.  **Canvas Area (Spout Feed):** A central display mapping the live Spout output from OBS.
2.  **Toolbar / Tools:**
    *   **Draw Bounding Box:** Click and drag to define an ROI.
    *   **Assign Element Type:** Dropdown to label the drawn box (e.g., `Lifebar`, `Combo Counter`, `System Text`).
    *   **Set Logic Parameters:** Sliders/inputs to define logic rules for the selected box (e.g., `Segments: 4`, `Direction: Right-to-Left`, `Color Match: Green`).
3.  **The "Mirror" Utility:** 
    *   A dedicated button: **[Mirror P1 Data to P2]**.
    *   *Logic:* Calculates the exact opposite coordinates based on screen width (`Screen Width - X_coordinate`) and automatically flips the depletion direction (RTL becomes LTR).
4.  **Save & Compile:** Generates the `config.json` file and transitions the app into "Live Monitor" mode.

---

## Phase 3: Data Architecture (JSON Configuration Schema)
The configuration file acts as the single source of truth. It is loaded directly into the RAM when the monitoring loop starts, ensuring zero I/O delays.

```json
{
  "system": {
    "resolution": [1920, 1080],
    "target_fps": 30,
    "obs_websocket": {
      "host": "localhost",
      "port": 4455,
      "password": "your_secret_password"
    }
  },
  "players": {
    "P1": {
      "lifebar": {
        "roi": [100, 50, 800, 80], 
        "direction": "RTL",
        "segments": 4,
        "target_color_hsv_range": [[40, 50, 50], [80, 255, 255]] 
      },
      "system_text_zone": {
        "roi": [100, 300, 400, 350],
        "trigger_on_pixel_change": true
      }
    },
    "P2": {
      "lifebar": {
        "roi": [1120, 50, 1820, 80],
        "direction": "LTR",
        "segments": 4,
        "target_color_hsv_range": [[40, 50, 50], [80, 255, 255]]
      },
      "system_text_zone": {
        "roi": [1520, 300, 1820, 350],
        "trigger_on_pixel_change": true
      }
    }
  },
  "obs_events": [
    {
      "trigger": "P1_Life_Under_25",
      "condition": "P1.lifebar.current_percentage < 25",
      "actions": [
        {"type": "toggle_source", "scene": "Main_Gameplay", "source": "Red_Danger_Vignette", "state": true},
        {"type": "toggle_filter", "source": "Game_Capture", "filter": "Danger_Color_Correction", "state": true}
      ]
    },
    {
      "trigger": "Counter_Attack_Detected",
      "condition": "P1.system_text_zone.pixel_density_change > 50",
      "actions": [
        {"type": "toggle_source", "scene": "Main_Gameplay", "source": "Impact_Flash_WebM", "state": true}
      ]
    }
  ]
}
Phase 4: Backend Core Logic (The Worker Thread)
This thread runs asynchronously, detached from the UI, executing the main analytical loop.

Initialization (__init__):

Parse config.json to RAM.

Establish Spout receiver connection.

Establish OBS WebSocket client.

The Analytics Loop (while True):

Fetch frame via Spout (NumPy array).

Crop & Mask: Slice the array using predefined ROIs. Apply cv2.inRange() to isolate health bar colors.

Segment Math: Instead of checking 100% of the bar, check the bounding box of the active segment. Calculate the fill ratio.

Delta Calculation: Compare current_hp to last_frame_hp. If the delta exceeds a predefined threshold (e.g., >15% drop in 2 frames), flag a "Major Damage" event.

بالتأكيد! نظراً لأنني لا أستطيع إرسال ملفات مباشرة للتحميل عبر هذه المحادثة، قمت بتجهيز المحتوى بالكامل داخل صندوق كود (Code Block) بصيغة Markdown.

يمكنك ببساطة النقر على زر "نسخ" (Copy) في الزاوية العلوية لصندوق الكود، ولصقه في أي محرر نصوص (مثل VS Code أو حتى Notepad)، ثم حفظ الملف باسم roadmap.md.

Markdown
# Project Roadmap: Real-Time FGC Telemetry & OBS Automation System

This document outlines the comprehensive architecture and execution plan for building a lightweight, real-time visual telemetry extractor and OBS automation tool. The system operates locally, avoiding CPU/GPU bottlenecks, and serves as a robust foundation for future AI integration.

---

## Phase 1: Technology Stack
*   **Core Backend:** Python 3.10+
*   **Video Transport:** `Spout-Python` (or `SpoutGL`) for zero-latency, VRAM-to-VRAM frame sharing.
*   **Computer Vision:** `OpenCV` (`cv2`) and `NumPy` for high-speed, matrix-based pixel masking and ROI (Region of Interest) cropping.
*   **Frontend / UI:** `CustomTkinter` (Modern, dark-mode native desktop GUI).
*   **OBS Integration:** `obsws-python` (OBS WebSocket v5 API) for triggering events, sources, and filters.

---

## Phase 2: User Interface (Configuration Workspace)
The UI is strictly a setup environment. Once configurations are saved, the UI can be minimized, shifting processing entirely to the lightweight backend worker thread.

### UI Layout & Components
1.  **Canvas Area (Spout Feed):** A central display mapping the live Spout output from OBS.
2.  **Toolbar / Tools:**
    *   **Draw Bounding Box:** Click and drag to define an ROI.
    *   **Assign Element Type:** Dropdown to label the drawn box (e.g., `Lifebar`, `Combo Counter`, `System Text`).
    *   **Set Logic Parameters:** Sliders/inputs to define logic rules for the selected box (e.g., `Segments: 4`, `Direction: Right-to-Left`, `Color Match: Green`).
3.  **The "Mirror" Utility:** 
    *   A dedicated button: **[Mirror P1 Data to P2]**.
    *   *Logic:* Calculates the exact opposite coordinates based on screen width (`Screen Width - X_coordinate`) and automatically flips the depletion direction (RTL becomes LTR).
4.  **Save & Compile:** Generates the `config.json` file and transitions the app into "Live Monitor" mode.

---

## Phase 3: Data Architecture (JSON Configuration Schema)
The configuration file acts as the single source of truth. It is loaded directly into the RAM when the monitoring loop starts, ensuring zero I/O delays.

```json
{
  "system": {
    "resolution": [1920, 1080],
    "target_fps": 30,
    "obs_websocket": {
      "host": "localhost",
      "port": 4455,
      "password": "your_secret_password"
    }
  },
  "players": {
    "P1": {
      "lifebar": {
        "roi": [100, 50, 800, 80], 
        "direction": "RTL",
        "segments": 4,
        "target_color_hsv_range": [[40, 50, 50], [80, 255, 255]] 
      },
      "system_text_zone": {
        "roi": [100, 300, 400, 350],
        "trigger_on_pixel_change": true
      }
    },
    "P2": {
      "lifebar": {
        "roi": [1120, 50, 1820, 80],
        "direction": "LTR",
        "segments": 4,
        "target_color_hsv_range": [[40, 50, 50], [80, 255, 255]]
      },
      "system_text_zone": {
        "roi": [1520, 300, 1820, 350],
        "trigger_on_pixel_change": true
      }
    }
  },
  "obs_events": [
    {
      "trigger": "P1_Life_Under_25",
      "condition": "P1.lifebar.current_percentage < 25",
      "actions": [
        {"type": "toggle_source", "scene": "Main_Gameplay", "source": "Red_Danger_Vignette", "state": true},
        {"type": "toggle_filter", "source": "Game_Capture", "filter": "Danger_Color_Correction", "state": true}
      ]
    },
    {
      "trigger": "Counter_Attack_Detected",
      "condition": "P1.system_text_zone.pixel_density_change > 50",
      "actions": [
        {"type": "toggle_source", "scene": "Main_Gameplay", "source": "Impact_Flash_WebM", "state": true}
      ]
    }
  ]
}
Phase 4: Backend Core Logic (The Worker Thread)
This thread runs asynchronously, detached from the UI, executing the main analytical loop.

Initialization (__init__):

Parse config.json to RAM.

Establish Spout receiver connection.

Establish OBS WebSocket client.

The Analytics Loop (while True):

Fetch frame via Spout (NumPy array).

Crop & Mask: Slice the array using predefined ROIs. Apply cv2.inRange() to isolate health bar colors.

Segment Math: Instead of checking 100% of the bar, check the bounding box of the active segment. Calculate the fill ratio.

Delta Calculation: Compare current_hp to last_frame_hp. If the delta exceeds a predefined threshold (e.g., >15% drop in 2 frames), flag a "Major Damage" event.

Event Dispatcher: If an event flag is raised, evaluate it against the obs_events rules in the configuration.

Phase 5: OBS WebSocket Automation Module
This module translates detected events into visual changes on stream seamlessly.

Toggle Scene Items (Sources):
Use the SetSceneItemEnabled request.

Use Case: Turning on an animated overlay (like a flash or a combo counter graphic) when a specific text ROI changes color.

Toggle Source Filters:
Use the SetSourceFilterEnabled request.

Use Case: Activating a heavy vignette, color grading LUT, or blur filter directly on the Spout Sender source or Game Capture source when a player enters the "Danger Zone" (last lifebar segment).

Phase 6: Development Sprints
To maintain an agile workflow and ensure stability before scaling to AI, execute in this order:

Sprint 1 (Backend Core): Establish Spout -> Python connection. Successfully slice a NumPy array and print terminal logs based on color thresholding.

Sprint 2 (OBS Bridge): Connect obsws-python. Write wrapper functions to toggle visibility and filters. Link Sprint 1 terminal logs to actual OBS actions.

Sprint 3 (Frontend Setup): Build the CustomTkinter UI. Implement the Spout video preview, drawing tools, and JSON serialization.

Sprint 4 (Math & Mirroring): Implement the logical segmentation of the ROIs and the P1->P2 mirror calculations within the UI.

Sprint 5 (System Polish): Finalize the background threading to ensure the UI does not block the Spout frame-fetching loop. Ensure CPU usage remains under 5%.