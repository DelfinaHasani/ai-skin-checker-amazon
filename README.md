# AI-driven skin symptoms checker
## Key Features
### Three input modes
Image only → fast heuristic signal (+ optional embedding).                                                                
Text only → lightweight, local text model (optional).                                                          
Image + Text → combined, user-friendly explanation.

Clean API: POST /detect accepts multipart/form-data with optional file and symptom.
Modern UI: Drag-and-drop upload, live preview, character count, disabled states, overlay “Processing…” indicator, toast notifications, and skeleton loading.
Works offline (core demo). External models are optional and can be toggled.
Windows-friendly: Instructions for PowerShell, port checks, and common pitfalls.
