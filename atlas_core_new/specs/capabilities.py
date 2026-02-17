"""
Multimodal Capabilities & Hardware Awareness

What they can produce and how they adapt to your devices.
"""

MULTIMODAL_CAPABILITIES = {
    "description": "Types of output the system can produce",
    "current_capabilities": [
        {
            "id": "text",
            "name": "Text",
            "status": "primary",
            "description": "Written explanations, conversations, documentation"
        },
        {
            "id": "voice",
            "name": "Voice",
            "status": "tts-ready",
            "description": "Text-to-speech output for spoken responses"
        },
        {
            "id": "visual-diagrams",
            "name": "Visual Diagrams & Schematics",
            "status": "active",
            "description": "Technical drawings, flowcharts, system diagrams"
        },
        {
            "id": "simulations",
            "name": "Simulations",
            "status": "conceptual",
            "description": "Mental model simulations and scenario walkthroughs"
        },
        {
            "id": "code-generation",
            "name": "Code Generation",
            "status": "active",
            "description": "Working code in multiple languages"
        },
        {
            "id": "blueprint-breakdowns",
            "name": "Blueprint-Style Breakdowns",
            "status": "active",
            "description": "LEGO-style step-by-step build instructions"
        }
    ],
    "future_capabilities": [
        {
            "id": "camera-integration",
            "name": "Camera Integration",
            "status": "future-phase",
            "description": "Visual input processing"
        },
        {
            "id": "earpiece-integration",
            "name": "Earpiece Integration",
            "status": "future-phase",
            "description": "Real-time audio interaction"
        }
    ]
}

HARDWARE_AWARENESS = {
    "description": "How the system adapts to your devices",
    "display_optimization": {
        "dark_mode": {
            "optimized_for": "OLED dark mode",
            "preference": "Darker colors and soft colors (NOT bright colors)"
        },
        "resolution": {
            "target": "QHD+ (3120 x 1440) friendly",
            "features": [
                "High-resolution diagrams",
                "8K asset generation (for export, print, desktop)"
            ]
        }
    },
    "processing_awareness": {
        "mobile": {
            "target": "Snapdragon-class mobile chips (Android)",
            "adaptation": "Battery-conscious output when mobile"
        },
        "desktop": {
            "target": "Desktop-class CPUs/GPUs",
            "adaptation": "Full performance utilization"
        },
        "adaptive_modes": {
            "description": "They scale down for phones, scale up for workstations",
            "modes": ["mobile-light", "desktop-full", "adaptive"]
        }
    }
}
