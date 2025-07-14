# Layout Mapper

A prototype application built with **OpenCV**, **EasyOCR**, **Streamlit**, and other Python libraries that:
1. Performs segmentation of web page layout images using OpenCV and constructs a block hierarchy.
2. Analyzes each block to gather information about vertex coordinates, used colors, and text content.
3. Saves results in JSON format and provides visualization of **bounding boxes** on the original image, saving a new annotated image (`annotated-result.png`) with detected block contours.
4. Generates a flat HTML collection of detected blocks in their original size with color and text content information based on JSON results.

---

## 1. Environment Setup

### 1.1. Clone/Copy Repository
Copy project files to any convenient folder (e.g., `layout-mapper/`).

```bash
git clone https://github.com/sunychibo/web-layout-to-code.git
```
```bash
cd web-layout-to-code
```

### 1.2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
```
```bash
source venv/bin/activate # Linux/Mac
# or
venv\Scripts\activate # Windows
```

### 1.3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 2. Launching the Application
From the project root (where `app.py` is located), run:
```bash
streamlit run app.py
```
The **Streamlit** interface will open in your browser (typically at http://localhost:8501).

---

## 3. Usage
1. **Upload** a web interface image (e.g., `assets/website_template_3.png`) via `Browse files`.
2. Optimal default parameters are preconfigured. Experiment with different settings (detailed below). `defaults_atomic-noise.json` contains a preset for high-detail recognition. Press `Apply` to save changes.
3. Click **Process Image** to:
   - Generate block hierarchy (JSON) via OpenCV
   - Detect colors (`detect_colors`)
   - Extract text (`extract_text` via EasyOCR)
   - Save results to `output-coordinates.json`
4. View the JSON structure under "Generated JSON".
5. Click **Render Bboxes** to visualize blocks overlaid on the original image.
6. Generate HTML by clicking "Generate HTML Collection".

### 3.1 Configuration Parameters Table
Key parameters for classical thresholding and morphological analysis. Ranges are approximate and depend on image resolution/characteristics.

| **Parameter** | **Purpose** | **Possible Range** | **Default Value** |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|--------------------------------|
| **threshold_method** | Binarization method:<br>- `fixed`: classic `cv2.threshold(..., THRESH_BINARY_INV)`<br>- `otsu`: `cv2.THRESH_OTSU`<br>- `triangle`: `cv2.THRESH_TRIANGLE`<br>- `adaptive_mean`: `cv2.ADAPTIVE_THRESH_MEAN_C`<br>- `adaptive_gaussian`: `cv2.ADAPTIVE_THRESH_GAUSSIAN_C` | [`fixed`, `otsu`, `triangle`, `adaptive_mean`, `adaptive_gaussian`] | `fixed` |
| **threshold_value** | Hard threshold for binarization (when `fixed` is selected) | 0–255 | 127 |
| **max_value** | Value assigned to pixels above threshold (typically 255) | 1–255 | 255 |
| **adaptive_block_size** | Local neighborhood size (square: 3×3, 5×5...) for `cv2.adaptiveThreshold` | 3–99 (odd values) | 11 |
| **adaptive_C** | Constant subtracted from mean (adaptive thresholding) | -10…10 | 2 |
| **morphology_kernel_size** | Structuring element size (e.g., for `cv2.getStructuringElement`) | 1–31 (usually odd) | 3 |
| **morphology_iterations** | Iterations for morphological operations (erode/dilate/open/close) | 0–5 | 1 |
| **min_block_width** | Minimum detected bounding box width to qualify as a "block" | 10–200 (image-dependent) | 20 |
| **min_block_height** | Minimum bounding box height | 10–200 | 20 |
| **retrieval_mode** | Contour retrieval mode:<br>- `cv2.RETR_EXTERNAL` (external only)<br>- `cv2.RETR_TREE` (hierarchy)<br>- `cv2.RETR_CCOMP`, `cv2.RETR_LIST` | [`RETR_EXTERNAL`, `RETR_TREE`, ...] | `RETR_EXTERNAL` |
| **approx_method** | Contour approximation algorithm:<br>- `cv2.CHAIN_APPROX_SIMPLE`<br>- `cv2.CHAIN_APPROX_NONE`<br>- `cv2.CHAIN_APPROX_TC89_L1`<br>- `cv2.CHAIN_APPROX_TC89_KCOS` | [`CHAIN_APPROX_SIMPLE`, ...] | `CHAIN_APPROX_SIMPLE` |
| **min_area** | Minimum contour area (pixels) for inclusion | 0–10000+ | 0 (disabled) |
| **max_area** | Maximum contour area (excludes oversized areas except layout) | ≥ `min_area` | ∞ (disabled) |
| **approx_polygons** | Enable polygon approximation (improves corner detection vs. boundingRect) | true/false | false |

---

## 4. Project Structure
Key files/folders:

- **`app.py`** – Main Streamlit application
- **`modules/`** – Processing logic:
   - `opencv_processing.py` – Layout segmentation (OpenCV)
   - `color_processing.py` – Background color/gradient analysis
   - `text_recognition_processing.py` – OCR (EasyOCR)
   - `render_bboxes.py` – Bbox visualization
   - `html_processing.py` – HTML generation/export
- **`ui_panel.py`** – Control panel (sliders, selects, etc.)
- **`output-coordinates.json`** – Output JSON (created on "Process Image")
- **`assets/website_template.png`** – Sample web layout image
- **`requirements.txt`** – Dependencies list

---

## 5. Potential & Scalability
- **AI Integration**: Extendable with YOLO models for element detection (buttons/icons/forms) and local language models (CodeParrot/GPT-Neo) for direct HTML/CSS generation from JSON.
- **Offline Operation**: Local OCR (EasyOCR) and ML models (YOLO/CodeParrot) eliminate external API dependencies.
- **Modular Architecture**: Independent modules (color/text/rendering/codegen) simplify maintenance and enable new analyses (font detection, CSS style recognition, image segmentation).
- **Future Development**: Support for adaptive segmentation, block-type classifiers (button/input/heading), and multilingual interface recognition.
