# AI-driven Skin Symptoms Checker
## Key Features
#### Three input modes
Image only → fast heuristic signal (+ optional embedding).                                                                
Text only → lightweight, local text model (optional).                                                          
Image + Text → combined, user-friendly explanation.

#### Clean API 
POST /detect accepts multipart/form-data with optional file and symptom.
#### Modern UI 
Drag-and-drop upload, live preview, character count, disabled states, overlay “Processing…” indicator, toast notifications, and skeleton loading.

## Architecture
#### Backend: Python Flask                                                                               
Route GET / → serves UI.                                                             
Route POST /detect → accepts multipart/form-data and returns JSON.                                          
Optional image embedding via Salesforce/blip-vqa-base (Keras SavedModel on HF).                                   
HEIC/HEIF support via pillow-heif.                                                      
#### Frontend: Single page (detect.html)                                                      
All styles are in-page.                                                                 
One JS file (static/detect.js) to avoid event conflicts.

![capture9](https://github.com/user-attachments/assets/5a5e2d3c-58c9-4b03-a754-357d46f5cc5b)

