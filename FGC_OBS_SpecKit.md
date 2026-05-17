# Project Specification Kit (SpecKit): FGC Telemetry & OBS Automation

## 1. System Architecture & Tech Stack
- **Language**: Python 3.10+ (Dedicated Conda environment: `fgc_obs`)
- **UI Framework**: `customtkinter` (Dark mode, modern desktop GUI, rounded corners)
- **Computer Vision**: `OpenCV` (`cv2`), `NumPy`
- **Capture Method**: `mss` (For high-speed, lightweight screen capturing).
- **Automation**: `obsws-python` (OBS WebSocket v5 API)

## 2. Phase 1: The UI and Drawing Tools (Configuration Workspace)
**Core Design Rule**: The UI is strictly for setup. It must NOT process live video to avoid CPU/GPU bottlenecks.

- **Image Loader / Snapshot Mechanism**: 
  - Add an "Upload Screenshot" button to load a static image of the fighting game HUD. This allows the user to precisely select elements that only appear for a few frames (e.g., "Counter" text).
- **Interactive Canvas**: Display the loaded screenshot.
- **Drawing Tools**: 
  - The user clicks and drags the mouse to draw a Bounding Box (ROI) directly over the **Health Bar**, **Timer**, or **System Text**.
  - A toolbar to select the element type (e.g., `P1 Health Bar`, `P2 Health Bar`).
- **Data Preview**: As the box is drawn, display the live `X, Y, Width, Height` values in a side panel.
- **Mirror Action**: A "Mirror to P2" button that calculates the exact opposite coordinates based on the `1920x1080` screen width and flips the orientation.
- **Export**: Save all drawn coordinates and selected actions to a `config.json` file.

## 3. Phase 2: The Backend Engine (Live Monitoring Mode)
**Core Design Rule**: This script runs silently in the background (headless) with NO `cv2.imshow()`.

- **Efficient Capture Loop**: Use `mss` to capture **ONLY** the specific bounding boxes (ROIs) defined in `config.json`. DO NOT capture the full 1080p screen.
- **Health Bar Math**:
  - Convert the tiny cropped ROI array to HSV.
  - Apply `cv2.inRange()` to isolate the health bar color.
  - Calculate the percentage of active pixels.
- **Event Dispatcher**: If the health percentage drops below a threshold (e.g., 20%), trigger an OBS WebSocket event (e.g., enable a Red Vignette filter).

---

## 4. How to Direct the Agent (Prompting Guide)
When you are ready to write the code with your AI Agent (e.g., Cursor, v0, or Claude), feed it this SpecKit along with the following prompt to adapt the `haste-rl` logic.

### 📌 Prompt to copy & paste for the Agent:
> "Agent, we are building the backend for our OBS automation tool based on the provided SpecKit. 
> 
> I want you to analyze the repository `https://github.com/shplok/haste-rl`, specifically how it handles Computer Vision Integration (health monitoring, lives tracking, and template matching) using `mss` and `OpenCV`.
> 
> **Your Task:**
> DO NOT create a new standalone example. Edit and integrate into our existing workflow. Extract their highly optimized methodology for capturing specific screen regions and calculating health states. 
> Adapt their `mss` capture logic so that it ONLY captures the tiny `[X, Y, W, H]` coordinates defined in our `config.json` (avoiding full 1080p captures), and apply their color/template matching logic to evaluate the health bar percentage. Keep the script headless and extremely fast."

## 5. Development Milestones (Step-by-Step Execution Plan)
- [ ] **Step 1:** Build the `customtkinter` UI layout with the static image uploader and the interactive drawing canvas.
- [ ] **Step 2:** Implement the mouse event logic (Click, Drag, Release) to draw rectangles on the canvas and update the `X, Y, W, H` fields.
- [ ] **Step 3:** Implement the JSON serialization to save the drawn regions to `config.json`.
- [ ] **Step 4:** (Using the Agent Prompt above) Build the `mss` + `OpenCV` background worker that reads the JSON and tracks the Health Bar ROI.
- [ ] **Step 5:** Connect `obsws-python` to the backend worker to toggle a test filter in OBS when health drops.
