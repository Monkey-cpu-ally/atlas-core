"""
Comprehensive Lesson Plans for all 22 Fields of Study.
Each field has subfields, chapters, estimated study times, and final projects.
"""

CURRICULUM = {
    "software_engineering": {
        "id": "software_engineering",
        "name": "Software Engineering",
        "icon": "💻",
        "description": "Build software systems from concept to deployment",
        "estimated_weeks": 16,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "subfields": [
            {
                "id": "programming_fundamentals",
                "name": "Programming Fundamentals",
                "chapters": [
                    {"id": "ch1", "title": "Variables, Types & Memory", "minutes": 45},
                    {"id": "ch2", "title": "Control Flow & Logic", "minutes": 45},
                    {"id": "ch3", "title": "Functions & Modularity", "minutes": 45},
                    {"id": "ch4", "title": "Data Structures Basics", "minutes": 60},
                    {"id": "ch5", "title": "Object-Oriented Thinking", "minutes": 60}
                ]
            },
            {
                "id": "web_development",
                "name": "Web Development",
                "chapters": [
                    {"id": "ch1", "title": "HTML & Semantic Markup", "minutes": 45},
                    {"id": "ch2", "title": "CSS Layout & Styling", "minutes": 45},
                    {"id": "ch3", "title": "JavaScript Essentials", "minutes": 60},
                    {"id": "ch4", "title": "APIs & Data Fetching", "minutes": 45},
                    {"id": "ch5", "title": "Frontend Frameworks", "minutes": 60}
                ]
            },
            {
                "id": "backend_systems",
                "name": "Backend Systems",
                "chapters": [
                    {"id": "ch1", "title": "Server Architecture", "minutes": 45},
                    {"id": "ch2", "title": "Databases & SQL", "minutes": 60},
                    {"id": "ch3", "title": "Authentication & Security", "minutes": 45},
                    {"id": "ch4", "title": "API Design Patterns", "minutes": 45},
                    {"id": "ch5", "title": "Deployment & DevOps", "minutes": 60}
                ]
            },
            {
                "id": "knowledge_preservation",
                "name": "Knowledge Vault & Archive Systems",
                "chapters": [
                    {"id": "ch1", "title": "Format-Agnostic Archival Design", "minutes": 45},
                    {"id": "ch2", "title": "Knowledge Graph Preservation", "minutes": 60},
                    {"id": "ch3", "title": "Version History & Decision Capture", "minutes": 45},
                    {"id": "ch4", "title": "Multi-Redundancy Architecture", "minutes": 45},
                    {"id": "ch5", "title": "Self-Describing Archive Formats", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Full-Stack Application",
            "description": "Build a complete web application with user authentication, database, and deployment",
            "requirements": ["Frontend UI", "Backend API", "Database integration", "User auth", "Deployed live"]
        }
    },
    
    "robotics": {
        "id": "robotics",
        "name": "Robotics",
        "icon": "🤖",
        "description": "Design and build autonomous robotic systems",
        "estimated_weeks": 24,
        "daily_minutes": 45,
        "lead_persona": "ajani",
        "subfields": [
            {
                "id": "mechanical_design",
                "name": "Mechanical Design",
                "chapters": [
                    {"id": "ch1", "title": "Robot Anatomy & Structure", "minutes": 45},
                    {"id": "ch2", "title": "Motors & Actuators", "minutes": 45},
                    {"id": "ch3", "title": "Gears, Pulleys & Transmission", "minutes": 60},
                    {"id": "ch4", "title": "3D Design for Robotics", "minutes": 60},
                    {"id": "ch5", "title": "Material Selection", "minutes": 45}
                ]
            },
            {
                "id": "electronics",
                "name": "Electronics & Sensors",
                "chapters": [
                    {"id": "ch1", "title": "Basic Circuit Theory", "minutes": 45},
                    {"id": "ch2", "title": "Microcontrollers (Arduino/ESP32)", "minutes": 60},
                    {"id": "ch3", "title": "Sensors & Input Devices", "minutes": 45},
                    {"id": "ch4", "title": "Power Systems & Batteries", "minutes": 45},
                    {"id": "ch5", "title": "PCB Design Basics", "minutes": 60}
                ]
            },
            {
                "id": "robot_programming",
                "name": "Robot Programming",
                "chapters": [
                    {"id": "ch1", "title": "Embedded C/C++", "minutes": 60},
                    {"id": "ch2", "title": "Motion Control Algorithms", "minutes": 60},
                    {"id": "ch3", "title": "Sensor Fusion", "minutes": 45},
                    {"id": "ch4", "title": "Path Planning", "minutes": 60},
                    {"id": "ch5", "title": "Computer Vision Basics", "minutes": 60}
                ]
            },
            {
                "id": "swarm_robotics",
                "name": "Swarm Robotics",
                "advanced": True,
                "chapters": [
                    {"id": "ch1", "title": "Swarm Intelligence Principles", "minutes": 45},
                    {"id": "ch2", "title": "Communication Protocols", "minutes": 60},
                    {"id": "ch3", "title": "Coordination Algorithms", "minutes": 60},
                    {"id": "ch4", "title": "Emergent Behavior", "minutes": 45},
                    {"id": "ch5", "title": "Multi-Robot Systems", "minutes": 60}
                ]
            },
            {
                "id": "soft_robotics",
                "name": "Soft Robotics",
                "advanced": True,
                "chapters": [
                    {"id": "ch1", "title": "Soft Materials & Actuation", "minutes": 45},
                    {"id": "ch2", "title": "Pneumatic & Hydraulic Systems", "minutes": 60},
                    {"id": "ch3", "title": "Bio-Inspired Design", "minutes": 45},
                    {"id": "ch4", "title": "Grippers & Manipulation", "minutes": 60},
                    {"id": "ch5", "title": "Wearable Robotics", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Autonomous Robot",
            "description": "Build a robot that can navigate, sense its environment, and complete a task autonomously",
            "requirements": ["Mechanical chassis", "Sensor integration", "Autonomous navigation", "Task completion"]
        }
    },
    
    "artificial_intelligence": {
        "id": "artificial_intelligence",
        "name": "Artificial Intelligence",
        "icon": "🧠",
        "description": "Build intelligent systems that learn and adapt",
        "estimated_weeks": 18,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "subfields": [
            {
                "id": "ml_fundamentals",
                "name": "Machine Learning Fundamentals",
                "chapters": [
                    {"id": "ch1", "title": "What is Machine Learning?", "minutes": 45},
                    {"id": "ch2", "title": "Supervised Learning", "minutes": 60},
                    {"id": "ch3", "title": "Unsupervised Learning", "minutes": 45},
                    {"id": "ch4", "title": "Model Evaluation", "minutes": 45},
                    {"id": "ch5", "title": "Feature Engineering", "minutes": 60}
                ]
            },
            {
                "id": "deep_learning",
                "name": "Deep Learning",
                "chapters": [
                    {"id": "ch1", "title": "Neural Network Basics", "minutes": 60},
                    {"id": "ch2", "title": "Training & Optimization", "minutes": 60},
                    {"id": "ch3", "title": "Convolutional Networks", "minutes": 60},
                    {"id": "ch4", "title": "Recurrent Networks", "minutes": 60},
                    {"id": "ch5", "title": "Transformers & Attention", "minutes": 60}
                ]
            },
            {
                "id": "applied_ai",
                "name": "Applied AI",
                "chapters": [
                    {"id": "ch1", "title": "Natural Language Processing", "minutes": 60},
                    {"id": "ch2", "title": "Computer Vision", "minutes": 60},
                    {"id": "ch3", "title": "Reinforcement Learning", "minutes": 60},
                    {"id": "ch4", "title": "AI Ethics & Safety", "minutes": 45},
                    {"id": "ch5", "title": "Deploying AI Models", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "AI Application",
            "description": "Build an AI-powered application that solves a real problem",
            "requirements": ["Trained model", "User interface", "Real data", "Deployed system"]
        }
    },
    
    "3d_printing": {
        "id": "3d_printing",
        "name": "3D Printing & Fabrication",
        "icon": "🖨️",
        "description": "Master additive manufacturing and digital fabrication",
        "estimated_weeks": 12,
        "daily_minutes": 45,
        "lead_persona": "ajani",
        "subfields": [
            {
                "id": "printer_technology",
                "name": "Printer Technology",
                "chapters": [
                    {"id": "ch1", "title": "FDM Printing Fundamentals", "minutes": 45},
                    {"id": "ch2", "title": "Resin Printing (SLA/DLP)", "minutes": 45},
                    {"id": "ch3", "title": "Printer Mechanics & Calibration", "minutes": 60},
                    {"id": "ch4", "title": "Materials Science", "minutes": 45},
                    {"id": "ch5", "title": "Advanced Printer Types", "minutes": 45}
                ]
            },
            {
                "id": "3d_modeling",
                "name": "3D Modeling for Print",
                "chapters": [
                    {"id": "ch1", "title": "CAD Fundamentals", "minutes": 60},
                    {"id": "ch2", "title": "Design for Manufacturability", "minutes": 45},
                    {"id": "ch3", "title": "Organic Modeling", "minutes": 60},
                    {"id": "ch4", "title": "Parametric Design", "minutes": 45},
                    {"id": "ch5", "title": "File Formats & Slicing", "minutes": 45}
                ]
            },
            {
                "id": "print_optimization",
                "name": "Print Optimization",
                "chapters": [
                    {"id": "ch1", "title": "Support Structures", "minutes": 45},
                    {"id": "ch2", "title": "Layer Settings & Quality", "minutes": 45},
                    {"id": "ch3", "title": "Post-Processing", "minutes": 45},
                    {"id": "ch4", "title": "Troubleshooting Prints", "minutes": 60},
                    {"id": "ch5", "title": "Multi-Material Printing", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Functional Print Project",
            "description": "Design and print a functional object that solves a real problem",
            "requirements": ["Original CAD design", "Material selection", "Optimized print settings", "Working prototype"]
        }
    },
    
    "electronics": {
        "id": "electronics",
        "name": "Electronics",
        "icon": "⚡",
        "description": "Design and build electronic circuits and systems",
        "estimated_weeks": 16,
        "daily_minutes": 45,
        "lead_persona": "ajani",
        "subfields": [
            {
                "id": "circuit_fundamentals",
                "name": "Circuit Fundamentals",
                "chapters": [
                    {"id": "ch1", "title": "Voltage, Current & Resistance", "minutes": 45},
                    {"id": "ch2", "title": "Ohm's Law & Circuit Analysis", "minutes": 45},
                    {"id": "ch3", "title": "Capacitors & Inductors", "minutes": 45},
                    {"id": "ch4", "title": "Diodes & Transistors", "minutes": 60},
                    {"id": "ch5", "title": "Power Supplies", "minutes": 45}
                ]
            },
            {
                "id": "digital_electronics",
                "name": "Digital Electronics",
                "chapters": [
                    {"id": "ch1", "title": "Logic Gates", "minutes": 45},
                    {"id": "ch2", "title": "Combinational Circuits", "minutes": 45},
                    {"id": "ch3", "title": "Sequential Circuits", "minutes": 60},
                    {"id": "ch4", "title": "Microcontroller Basics", "minutes": 60},
                    {"id": "ch5", "title": "Communication Protocols", "minutes": 45}
                ]
            },
            {
                "id": "pcb_design",
                "name": "PCB Design",
                "chapters": [
                    {"id": "ch1", "title": "Schematic Capture", "minutes": 45},
                    {"id": "ch2", "title": "PCB Layout Fundamentals", "minutes": 60},
                    {"id": "ch3", "title": "Design Rules & Manufacturing", "minutes": 45},
                    {"id": "ch4", "title": "SMD vs Through-Hole", "minutes": 45},
                    {"id": "ch5", "title": "Testing & Debugging", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Custom Electronics Device",
            "description": "Design and build a custom electronic device from schematic to working prototype",
            "requirements": ["Original schematic", "PCB design", "Assembled board", "Working device"]
        }
    },
    
    "mathematics": {
        "id": "mathematics",
        "name": "Mathematics",
        "icon": "📐",
        "description": "Master mathematical thinking and problem-solving",
        "estimated_weeks": 20,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "subfields": [
            {
                "id": "algebra_foundations",
                "name": "Algebra Foundations",
                "chapters": [
                    {"id": "ch1", "title": "Variables & Expressions", "minutes": 45},
                    {"id": "ch2", "title": "Equations & Inequalities", "minutes": 45},
                    {"id": "ch3", "title": "Functions & Graphs", "minutes": 60},
                    {"id": "ch4", "title": "Systems of Equations", "minutes": 45},
                    {"id": "ch5", "title": "Polynomials & Factoring", "minutes": 60}
                ]
            },
            {
                "id": "calculus",
                "name": "Calculus",
                "chapters": [
                    {"id": "ch1", "title": "Limits & Continuity", "minutes": 60},
                    {"id": "ch2", "title": "Derivatives", "minutes": 60},
                    {"id": "ch3", "title": "Applications of Derivatives", "minutes": 60},
                    {"id": "ch4", "title": "Integrals", "minutes": 60},
                    {"id": "ch5", "title": "Applications of Integration", "minutes": 60}
                ]
            },
            {
                "id": "statistics",
                "name": "Statistics & Probability",
                "chapters": [
                    {"id": "ch1", "title": "Descriptive Statistics", "minutes": 45},
                    {"id": "ch2", "title": "Probability Basics", "minutes": 45},
                    {"id": "ch3", "title": "Distributions", "minutes": 60},
                    {"id": "ch4", "title": "Hypothesis Testing", "minutes": 60},
                    {"id": "ch5", "title": "Regression Analysis", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Mathematical Analysis Project",
            "description": "Apply mathematical concepts to analyze a real-world dataset or problem",
            "requirements": ["Problem formulation", "Mathematical modeling", "Analysis", "Conclusions"]
        }
    },
    
    "physics": {
        "id": "physics",
        "name": "Physics",
        "icon": "🔬",
        "description": "Understand the fundamental laws governing the universe",
        "estimated_weeks": 18,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "subfields": [
            {
                "id": "classical_mechanics",
                "name": "Classical Mechanics",
                "chapters": [
                    {"id": "ch1", "title": "Motion & Kinematics", "minutes": 45},
                    {"id": "ch2", "title": "Forces & Newton's Laws", "minutes": 60},
                    {"id": "ch3", "title": "Energy & Work", "minutes": 45},
                    {"id": "ch4", "title": "Momentum & Collisions", "minutes": 45},
                    {"id": "ch5", "title": "Rotational Motion", "minutes": 60}
                ]
            },
            {
                "id": "electromagnetism",
                "name": "Electromagnetism",
                "chapters": [
                    {"id": "ch1", "title": "Electric Charge & Fields", "minutes": 60},
                    {"id": "ch2", "title": "Electric Potential", "minutes": 45},
                    {"id": "ch3", "title": "Current & Circuits", "minutes": 45},
                    {"id": "ch4", "title": "Magnetism", "minutes": 60},
                    {"id": "ch5", "title": "Electromagnetic Waves", "minutes": 60}
                ]
            },
            {
                "id": "modern_physics",
                "name": "Modern Physics",
                "chapters": [
                    {"id": "ch1", "title": "Special Relativity", "minutes": 60},
                    {"id": "ch2", "title": "Quantum Mechanics Intro", "minutes": 60},
                    {"id": "ch3", "title": "Atomic Structure", "minutes": 45},
                    {"id": "ch4", "title": "Nuclear Physics", "minutes": 45},
                    {"id": "ch5", "title": "Particle Physics", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Physics Experiment",
            "description": "Design and conduct an experiment demonstrating a physics principle",
            "requirements": ["Hypothesis", "Experimental design", "Data collection", "Analysis", "Conclusion"]
        }
    },
    
    "biology": {
        "id": "biology",
        "name": "Biology",
        "icon": "🧬",
        "description": "Explore life from molecules to ecosystems",
        "estimated_weeks": 20,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "cell_biology",
                "name": "Cell Biology",
                "chapters": [
                    {"id": "ch1", "title": "Cell Structure", "minutes": 45},
                    {"id": "ch2", "title": "Cell Membrane & Transport", "minutes": 45},
                    {"id": "ch3", "title": "Cellular Respiration", "minutes": 60},
                    {"id": "ch4", "title": "Photosynthesis", "minutes": 45},
                    {"id": "ch5", "title": "Cell Division", "minutes": 60}
                ]
            },
            {
                "id": "genetics",
                "name": "Genetics",
                "chapters": [
                    {"id": "ch1", "title": "DNA Structure & Replication", "minutes": 60},
                    {"id": "ch2", "title": "Gene Expression", "minutes": 60},
                    {"id": "ch3", "title": "Mendelian Genetics", "minutes": 45},
                    {"id": "ch4", "title": "Molecular Genetics", "minutes": 60},
                    {"id": "ch5", "title": "Genetic Engineering", "minutes": 60}
                ]
            },
            {
                "id": "ecology",
                "name": "Ecology & Evolution",
                "chapters": [
                    {"id": "ch1", "title": "Ecosystems", "minutes": 45},
                    {"id": "ch2", "title": "Population Dynamics", "minutes": 45},
                    {"id": "ch3", "title": "Evolution by Natural Selection", "minutes": 60},
                    {"id": "ch4", "title": "Biodiversity", "minutes": 45},
                    {"id": "ch5", "title": "Conservation Biology", "minutes": 45}
                ]
            },
            {
                "id": "marine_biology",
                "name": "Marine Biology",
                "advanced": True,
                "chapters": [
                    {"id": "ch1", "title": "Ocean Zones & Marine Habitats", "minutes": 45},
                    {"id": "ch2", "title": "Marine Invertebrates", "minutes": 60},
                    {"id": "ch3", "title": "Fish & Marine Vertebrates", "minutes": 60},
                    {"id": "ch4", "title": "Coral Reef Ecosystems", "minutes": 45},
                    {"id": "ch5", "title": "Deep Sea Biology", "minutes": 60}
                ]
            },
            {
                "id": "microbiology",
                "name": "Microbiology",
                "advanced": True,
                "chapters": [
                    {"id": "ch1", "title": "Bacteria & Archaea", "minutes": 45},
                    {"id": "ch2", "title": "Viruses & Prions", "minutes": 45},
                    {"id": "ch3", "title": "Fungi & Protists", "minutes": 45},
                    {"id": "ch4", "title": "Host-Pathogen Interactions", "minutes": 60},
                    {"id": "ch5", "title": "Applied Microbiology", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Biology Research Project",
            "description": "Conduct a research project on a biological topic of interest",
            "requirements": ["Research question", "Literature review", "Investigation", "Findings presentation"]
        }
    },
    
    "chemistry": {
        "id": "chemistry",
        "name": "Chemistry",
        "icon": "⚗️",
        "description": "Understand matter and its transformations",
        "estimated_weeks": 16,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "subfields": [
            {
                "id": "general_chemistry",
                "name": "General Chemistry",
                "chapters": [
                    {"id": "ch1", "title": "Atomic Structure", "minutes": 45},
                    {"id": "ch2", "title": "Chemical Bonding", "minutes": 60},
                    {"id": "ch3", "title": "Stoichiometry", "minutes": 60},
                    {"id": "ch4", "title": "States of Matter", "minutes": 45},
                    {"id": "ch5", "title": "Solutions", "minutes": 45}
                ]
            },
            {
                "id": "organic_chemistry",
                "name": "Organic Chemistry",
                "chapters": [
                    {"id": "ch1", "title": "Carbon & Hydrocarbons", "minutes": 60},
                    {"id": "ch2", "title": "Functional Groups", "minutes": 60},
                    {"id": "ch3", "title": "Reactions & Mechanisms", "minutes": 60},
                    {"id": "ch4", "title": "Polymers", "minutes": 45},
                    {"id": "ch5", "title": "Biochemistry Intro", "minutes": 45}
                ]
            },
            {
                "id": "reactions",
                "name": "Chemical Reactions",
                "chapters": [
                    {"id": "ch1", "title": "Reaction Types", "minutes": 45},
                    {"id": "ch2", "title": "Thermodynamics", "minutes": 60},
                    {"id": "ch3", "title": "Kinetics", "minutes": 60},
                    {"id": "ch4", "title": "Equilibrium", "minutes": 45},
                    {"id": "ch5", "title": "Electrochemistry", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Chemistry Investigation",
            "description": "Design and conduct a chemistry experiment",
            "requirements": ["Research question", "Safety plan", "Procedure", "Data analysis", "Report"]
        }
    },
    
    "music_theory": {
        "id": "music_theory",
        "name": "Music Theory",
        "icon": "🎵",
        "description": "Understand the language of music",
        "estimated_weeks": 14,
        "daily_minutes": 30,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "fundamentals",
                "name": "Music Fundamentals",
                "chapters": [
                    {"id": "ch1", "title": "Notes & Staff", "minutes": 30},
                    {"id": "ch2", "title": "Rhythm & Time Signatures", "minutes": 30},
                    {"id": "ch3", "title": "Scales & Keys", "minutes": 45},
                    {"id": "ch4", "title": "Intervals", "minutes": 30},
                    {"id": "ch5", "title": "Chords", "minutes": 45}
                ]
            },
            {
                "id": "harmony",
                "name": "Harmony",
                "chapters": [
                    {"id": "ch1", "title": "Chord Progressions", "minutes": 45},
                    {"id": "ch2", "title": "Voice Leading", "minutes": 45},
                    {"id": "ch3", "title": "Cadences", "minutes": 30},
                    {"id": "ch4", "title": "Modulation", "minutes": 45},
                    {"id": "ch5", "title": "Extended Harmony", "minutes": 45}
                ]
            },
            {
                "id": "composition",
                "name": "Composition",
                "chapters": [
                    {"id": "ch1", "title": "Melody Writing", "minutes": 45},
                    {"id": "ch2", "title": "Form & Structure", "minutes": 45},
                    {"id": "ch3", "title": "Arranging", "minutes": 45},
                    {"id": "ch4", "title": "Counterpoint", "minutes": 60},
                    {"id": "ch5", "title": "Orchestration Basics", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Original Composition",
            "description": "Compose an original piece of music",
            "requirements": ["Written score", "Harmonic analysis", "Form explanation", "Recording/performance"]
        }
    },
    
    "creative_writing": {
        "id": "creative_writing",
        "name": "Creative Writing",
        "icon": "✍️",
        "description": "Master the art of storytelling",
        "estimated_weeks": 14,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "fiction_fundamentals",
                "name": "Fiction Fundamentals",
                "chapters": [
                    {"id": "ch1", "title": "Character Development", "minutes": 45},
                    {"id": "ch2", "title": "Plot Structure", "minutes": 45},
                    {"id": "ch3", "title": "Setting & World-Building", "minutes": 45},
                    {"id": "ch4", "title": "Point of View", "minutes": 30},
                    {"id": "ch5", "title": "Dialogue", "minutes": 45}
                ]
            },
            {
                "id": "genre_writing",
                "name": "Genre Writing",
                "chapters": [
                    {"id": "ch1", "title": "Horror & Dark Fiction", "minutes": 45},
                    {"id": "ch2", "title": "Science Fiction", "minutes": 45},
                    {"id": "ch3", "title": "Fantasy", "minutes": 45},
                    {"id": "ch4", "title": "Thriller & Mystery", "minutes": 45},
                    {"id": "ch5", "title": "Literary Fiction", "minutes": 45}
                ]
            },
            {
                "id": "craft",
                "name": "Writing Craft",
                "chapters": [
                    {"id": "ch1", "title": "Voice & Style", "minutes": 45},
                    {"id": "ch2", "title": "Show Don't Tell", "minutes": 30},
                    {"id": "ch3", "title": "Revision & Editing", "minutes": 45},
                    {"id": "ch4", "title": "Pacing & Tension", "minutes": 45},
                    {"id": "ch5", "title": "Theme & Meaning", "minutes": 45}
                ]
            },
            {
                "id": "horror_worldbuilding",
                "name": "Horror Universe Worldbuilding",
                "chapters": [
                    {"id": "ch1", "title": "Cosmic Horror & Cultural Folklore", "minutes": 45},
                    {"id": "ch2", "title": "Multi-Timeline Anthology Structure", "minutes": 60},
                    {"id": "ch3", "title": "Entity Design from Mythology", "minutes": 45},
                    {"id": "ch4", "title": "Cross-Media Storytelling", "minutes": 45},
                    {"id": "ch5", "title": "Building Interconnected Cosmologies", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Short Story Collection",
            "description": "Write a collection of 3-5 short stories",
            "requirements": ["Multiple stories", "Revision", "Thematic connection", "Final polish"]
        }
    },
    
    "visual_arts": {
        "id": "visual_arts",
        "name": "Visual Arts",
        "icon": "🎨",
        "description": "Develop your artistic vision and skills",
        "estimated_weeks": 14,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "drawing_fundamentals",
                "name": "Drawing Fundamentals",
                "chapters": [
                    {"id": "ch1", "title": "Line & Contour", "minutes": 45},
                    {"id": "ch2", "title": "Shape & Form", "minutes": 45},
                    {"id": "ch3", "title": "Value & Shading", "minutes": 45},
                    {"id": "ch4", "title": "Perspective", "minutes": 60},
                    {"id": "ch5", "title": "Composition", "minutes": 45}
                ]
            },
            {
                "id": "color_theory",
                "name": "Color Theory",
                "chapters": [
                    {"id": "ch1", "title": "Color Wheel Basics", "minutes": 30},
                    {"id": "ch2", "title": "Color Harmony", "minutes": 45},
                    {"id": "ch3", "title": "Value in Color", "minutes": 45},
                    {"id": "ch4", "title": "Color & Mood", "minutes": 45},
                    {"id": "ch5", "title": "Digital Color", "minutes": 45}
                ]
            },
            {
                "id": "digital_art",
                "name": "Digital Art",
                "chapters": [
                    {"id": "ch1", "title": "Digital Tools", "minutes": 45},
                    {"id": "ch2", "title": "Layers & Masks", "minutes": 45},
                    {"id": "ch3", "title": "Brushes & Textures", "minutes": 45},
                    {"id": "ch4", "title": "Digital Painting", "minutes": 60},
                    {"id": "ch5", "title": "Portfolio Building", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Art Portfolio",
            "description": "Create a portfolio of original artworks",
            "requirements": ["5+ finished pieces", "Various techniques", "Artist statement", "Presentation"]
        }
    },
    
    "philosophy": {
        "id": "philosophy",
        "name": "Philosophy",
        "icon": "🏛️",
        "description": "Explore fundamental questions about existence and knowledge",
        "estimated_weeks": 16,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "history_of_philosophy",
                "name": "History of Philosophy",
                "chapters": [
                    {"id": "ch1", "title": "Ancient Greek Philosophy", "minutes": 60},
                    {"id": "ch2", "title": "Medieval Philosophy", "minutes": 45},
                    {"id": "ch3", "title": "Modern Philosophy", "minutes": 60},
                    {"id": "ch4", "title": "Continental Philosophy", "minutes": 45},
                    {"id": "ch5", "title": "Analytic Philosophy", "minutes": 45}
                ]
            },
            {
                "id": "ethics",
                "name": "Ethics",
                "chapters": [
                    {"id": "ch1", "title": "Moral Foundations", "minutes": 45},
                    {"id": "ch2", "title": "Virtue Ethics", "minutes": 45},
                    {"id": "ch3", "title": "Deontology", "minutes": 45},
                    {"id": "ch4", "title": "Consequentialism", "minutes": 45},
                    {"id": "ch5", "title": "Applied Ethics", "minutes": 60}
                ]
            },
            {
                "id": "epistemology",
                "name": "Epistemology & Logic",
                "chapters": [
                    {"id": "ch1", "title": "What is Knowledge?", "minutes": 45},
                    {"id": "ch2", "title": "Sources of Knowledge", "minutes": 45},
                    {"id": "ch3", "title": "Formal Logic", "minutes": 60},
                    {"id": "ch4", "title": "Fallacies", "minutes": 45},
                    {"id": "ch5", "title": "Critical Thinking", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Philosophical Essay",
            "description": "Write an original philosophical argument on a topic of your choice",
            "requirements": ["Thesis statement", "Logical argument", "Objections addressed", "Conclusion"]
        }
    },
    
    "history": {
        "id": "history",
        "name": "History",
        "icon": "📜",
        "description": "Understand the past to navigate the future",
        "estimated_weeks": 16,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "world_history",
                "name": "World History",
                "chapters": [
                    {"id": "ch1", "title": "Ancient Civilizations", "minutes": 60},
                    {"id": "ch2", "title": "Classical Era", "minutes": 60},
                    {"id": "ch3", "title": "Medieval Period", "minutes": 45},
                    {"id": "ch4", "title": "Early Modern Era", "minutes": 45},
                    {"id": "ch5", "title": "Modern History", "minutes": 60}
                ]
            },
            {
                "id": "african_diaspora",
                "name": "African Diaspora History",
                "chapters": [
                    {"id": "ch1", "title": "Ancient African Civilizations", "minutes": 60},
                    {"id": "ch2", "title": "The Atlantic Slave Trade", "minutes": 60},
                    {"id": "ch3", "title": "Resistance & Abolition", "minutes": 60},
                    {"id": "ch4", "title": "Civil Rights Movement", "minutes": 60},
                    {"id": "ch5", "title": "Contemporary Issues", "minutes": 45}
                ]
            },
            {
                "id": "historiography",
                "name": "Historiography",
                "chapters": [
                    {"id": "ch1", "title": "What is History?", "minutes": 45},
                    {"id": "ch2", "title": "Primary vs Secondary Sources", "minutes": 45},
                    {"id": "ch3", "title": "Historical Analysis", "minutes": 45},
                    {"id": "ch4", "title": "Bias & Perspective", "minutes": 45},
                    {"id": "ch5", "title": "Writing History", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Historical Research Paper",
            "description": "Research and write about a historical topic using primary sources",
            "requirements": ["Primary sources", "Secondary sources", "Thesis", "Argument", "Bibliography"]
        }
    },
    
    "psychology": {
        "id": "psychology",
        "name": "Psychology",
        "icon": "🧠",
        "description": "Understand the human mind and behavior",
        "estimated_weeks": 14,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "general_psychology",
                "name": "General Psychology",
                "chapters": [
                    {"id": "ch1", "title": "History of Psychology", "minutes": 45},
                    {"id": "ch2", "title": "Research Methods", "minutes": 45},
                    {"id": "ch3", "title": "Biological Bases", "minutes": 60},
                    {"id": "ch4", "title": "Sensation & Perception", "minutes": 45},
                    {"id": "ch5", "title": "Consciousness", "minutes": 45}
                ]
            },
            {
                "id": "cognitive",
                "name": "Cognitive Psychology",
                "chapters": [
                    {"id": "ch1", "title": "Learning", "minutes": 45},
                    {"id": "ch2", "title": "Memory", "minutes": 45},
                    {"id": "ch3", "title": "Thinking & Problem Solving", "minutes": 45},
                    {"id": "ch4", "title": "Language", "minutes": 45},
                    {"id": "ch5", "title": "Intelligence", "minutes": 45}
                ]
            },
            {
                "id": "social",
                "name": "Social Psychology",
                "chapters": [
                    {"id": "ch1", "title": "Social Cognition", "minutes": 45},
                    {"id": "ch2", "title": "Attitudes & Persuasion", "minutes": 45},
                    {"id": "ch3", "title": "Group Dynamics", "minutes": 45},
                    {"id": "ch4", "title": "Prejudice & Discrimination", "minutes": 60},
                    {"id": "ch5", "title": "Prosocial Behavior", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Psychology Case Study",
            "description": "Conduct a case study analysis using psychological principles",
            "requirements": ["Case selection", "Theoretical framework", "Analysis", "Recommendations"]
        }
    },
    
    "economics": {
        "id": "economics",
        "name": "Economics",
        "icon": "📊",
        "description": "Understand how resources are allocated and distributed",
        "estimated_weeks": 14,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "subfields": [
            {
                "id": "microeconomics",
                "name": "Microeconomics",
                "chapters": [
                    {"id": "ch1", "title": "Supply & Demand", "minutes": 45},
                    {"id": "ch2", "title": "Elasticity", "minutes": 45},
                    {"id": "ch3", "title": "Consumer Choice", "minutes": 45},
                    {"id": "ch4", "title": "Production & Costs", "minutes": 60},
                    {"id": "ch5", "title": "Market Structures", "minutes": 60}
                ]
            },
            {
                "id": "macroeconomics",
                "name": "Macroeconomics",
                "chapters": [
                    {"id": "ch1", "title": "GDP & Economic Growth", "minutes": 45},
                    {"id": "ch2", "title": "Unemployment & Inflation", "minutes": 45},
                    {"id": "ch3", "title": "Fiscal Policy", "minutes": 45},
                    {"id": "ch4", "title": "Monetary Policy", "minutes": 45},
                    {"id": "ch5", "title": "International Trade", "minutes": 60}
                ]
            },
            {
                "id": "personal_finance",
                "name": "Personal Finance",
                "chapters": [
                    {"id": "ch1", "title": "Budgeting", "minutes": 30},
                    {"id": "ch2", "title": "Saving & Investing", "minutes": 45},
                    {"id": "ch3", "title": "Credit & Debt", "minutes": 45},
                    {"id": "ch4", "title": "Taxes", "minutes": 45},
                    {"id": "ch5", "title": "Financial Planning", "minutes": 45}
                ]
            },
            {
                "id": "generational_wealth",
                "name": "Generational Wealth & Family Tech",
                "chapters": [
                    {"id": "ch1", "title": "Digital Inheritance Infrastructure", "minutes": 45},
                    {"id": "ch2", "title": "Age-Locked Access Control Systems", "minutes": 45},
                    {"id": "ch3", "title": "Cryptographic Estate Planning", "minutes": 60},
                    {"id": "ch4", "title": "Multi-Generational Key Management", "minutes": 45},
                    {"id": "ch5", "title": "Family Governance & Succession Protocols", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Economic Analysis",
            "description": "Analyze an economic issue or market using economic principles",
            "requirements": ["Issue identification", "Data analysis", "Economic theory application", "Policy recommendations"]
        }
    },
    
    "environmental_science": {
        "id": "environmental_science",
        "name": "Environmental Science",
        "icon": "🌍",
        "description": "Understand and protect our natural world",
        "estimated_weeks": 18,
        "daily_minutes": 45,
        "lead_persona": "ajani",
        "subfields": [
            {
                "id": "earth_systems",
                "name": "Earth Systems",
                "chapters": [
                    {"id": "ch1", "title": "Atmosphere", "minutes": 45},
                    {"id": "ch2", "title": "Hydrosphere", "minutes": 45},
                    {"id": "ch3", "title": "Lithosphere", "minutes": 45},
                    {"id": "ch4", "title": "Biosphere", "minutes": 45},
                    {"id": "ch5", "title": "System Interactions", "minutes": 60}
                ]
            },
            {
                "id": "climate",
                "name": "Climate Science",
                "chapters": [
                    {"id": "ch1", "title": "Climate vs Weather", "minutes": 30},
                    {"id": "ch2", "title": "Greenhouse Effect", "minutes": 45},
                    {"id": "ch3", "title": "Climate Change Evidence", "minutes": 60},
                    {"id": "ch4", "title": "Climate Impacts", "minutes": 60},
                    {"id": "ch5", "title": "Mitigation & Adaptation", "minutes": 60}
                ]
            },
            {
                "id": "sustainability",
                "name": "Sustainability",
                "chapters": [
                    {"id": "ch1", "title": "Sustainable Development", "minutes": 45},
                    {"id": "ch2", "title": "Energy Systems", "minutes": 60},
                    {"id": "ch3", "title": "Waste Management", "minutes": 45},
                    {"id": "ch4", "title": "Water Resources", "minutes": 45},
                    {"id": "ch5", "title": "Green Technology", "minutes": 60}
                ]
            },
            {
                "id": "terraforming",
                "name": "Planetary Engineering & Terraforming",
                "advanced": True,
                "chapters": [
                    {"id": "ch1", "title": "Planetary Atmospheres", "minutes": 60},
                    {"id": "ch2", "title": "Mars Terraforming Theory", "minutes": 60},
                    {"id": "ch3", "title": "Closed Ecosystem Engineering", "minutes": 60},
                    {"id": "ch4", "title": "Megastructure Concepts", "minutes": 60},
                    {"id": "ch5", "title": "Long-Term Climate Modification", "minutes": 60}
                ]
            },
            {
                "id": "self_sustaining_estates",
                "name": "Self-Sustaining Estate Design",
                "chapters": [
                    {"id": "ch1", "title": "Closed-Loop Resource Cycling", "minutes": 45},
                    {"id": "ch2", "title": "Integrated Renewable Energy Grids", "minutes": 60},
                    {"id": "ch3", "title": "Living Water Purification Systems", "minutes": 45},
                    {"id": "ch4", "title": "Waste-to-Resource Conversion", "minutes": 45},
                    {"id": "ch5", "title": "Generational Sustainability Planning", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Environmental Action Plan",
            "description": "Develop an actionable plan to address an environmental issue",
            "requirements": ["Problem analysis", "Stakeholder mapping", "Solution design", "Implementation plan"]
        }
    },
    
    "business": {
        "id": "business",
        "name": "Business & Entrepreneurship",
        "icon": "💼",
        "description": "Build and grow successful ventures",
        "estimated_weeks": 14,
        "daily_minutes": 45,
        "lead_persona": "ajani",
        "subfields": [
            {
                "id": "entrepreneurship",
                "name": "Entrepreneurship",
                "chapters": [
                    {"id": "ch1", "title": "Identifying Opportunities", "minutes": 45},
                    {"id": "ch2", "title": "Business Models", "minutes": 45},
                    {"id": "ch3", "title": "Market Research", "minutes": 45},
                    {"id": "ch4", "title": "MVP & Validation", "minutes": 60},
                    {"id": "ch5", "title": "Pitching & Fundraising", "minutes": 60}
                ]
            },
            {
                "id": "management",
                "name": "Management",
                "chapters": [
                    {"id": "ch1", "title": "Leadership Principles", "minutes": 45},
                    {"id": "ch2", "title": "Team Building", "minutes": 45},
                    {"id": "ch3", "title": "Decision Making", "minutes": 45},
                    {"id": "ch4", "title": "Operations", "minutes": 45},
                    {"id": "ch5", "title": "Strategy", "minutes": 60}
                ]
            },
            {
                "id": "marketing",
                "name": "Marketing",
                "chapters": [
                    {"id": "ch1", "title": "Marketing Fundamentals", "minutes": 45},
                    {"id": "ch2", "title": "Branding", "minutes": 45},
                    {"id": "ch3", "title": "Digital Marketing", "minutes": 60},
                    {"id": "ch4", "title": "Content Strategy", "minutes": 45},
                    {"id": "ch5", "title": "Analytics & Optimization", "minutes": 45}
                ]
            },
            {
                "id": "fashion_brand_building",
                "name": "Fashion Brand Architecture",
                "chapters": [
                    {"id": "ch1", "title": "Cultural Symbolism in Design", "minutes": 45},
                    {"id": "ch2", "title": "Sub-Collection Identity Systems", "minutes": 45},
                    {"id": "ch3", "title": "Controlled Scarcity & Value", "minutes": 60},
                    {"id": "ch4", "title": "Heritage Encoding Through Design Language", "minutes": 45},
                    {"id": "ch5", "title": "Generational Brand Vision", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Business Plan",
            "description": "Create a comprehensive business plan for a venture",
            "requirements": ["Executive summary", "Market analysis", "Business model", "Financial projections", "Go-to-market strategy"]
        }
    },
    
    "game_design": {
        "id": "game_design",
        "name": "Game Design",
        "icon": "🎮",
        "description": "Create engaging interactive experiences",
        "estimated_weeks": 16,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "game_theory",
                "name": "Game Design Theory",
                "chapters": [
                    {"id": "ch1", "title": "What Makes Games Fun", "minutes": 45},
                    {"id": "ch2", "title": "Player Psychology", "minutes": 45},
                    {"id": "ch3", "title": "Core Loops", "minutes": 45},
                    {"id": "ch4", "title": "Game Balance", "minutes": 60},
                    {"id": "ch5", "title": "Narrative Design", "minutes": 45}
                ]
            },
            {
                "id": "game_development",
                "name": "Game Development",
                "chapters": [
                    {"id": "ch1", "title": "Game Engines Intro", "minutes": 60},
                    {"id": "ch2", "title": "Game Programming Basics", "minutes": 60},
                    {"id": "ch3", "title": "2D Game Development", "minutes": 60},
                    {"id": "ch4", "title": "3D Game Development", "minutes": 60},
                    {"id": "ch5", "title": "UI & UX for Games", "minutes": 45}
                ]
            },
            {
                "id": "game_art",
                "name": "Game Art & Audio",
                "chapters": [
                    {"id": "ch1", "title": "Pixel Art", "minutes": 45},
                    {"id": "ch2", "title": "Character Design", "minutes": 60},
                    {"id": "ch3", "title": "Environment Art", "minutes": 60},
                    {"id": "ch4", "title": "Animation Basics", "minutes": 60},
                    {"id": "ch5", "title": "Sound Design", "minutes": 45}
                ]
            },
            {
                "id": "game_lore_analysis",
                "name": "Game Lore & Narrative Analysis",
                "chapters": [
                    {"id": "ch1", "title": "Environmental Storytelling Methods", "minutes": 45},
                    {"id": "ch2", "title": "Item Description Narrative Threading", "minutes": 45},
                    {"id": "ch3", "title": "Symbolic & Mythological Mapping", "minutes": 60},
                    {"id": "ch4", "title": "Fragmented Timeline Reconstruction", "minutes": 45},
                    {"id": "ch5", "title": "Level Design as Narrative Architecture", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Complete Game",
            "description": "Design and build a complete playable game",
            "requirements": ["Game design document", "Playable build", "Art assets", "Sound/music", "Polish & testing"]
        }
    },
    
    "film_studies": {
        "id": "film_studies",
        "name": "Film Studies",
        "icon": "🎬",
        "description": "Understand and create cinematic art",
        "estimated_weeks": 14,
        "daily_minutes": 45,
        "lead_persona": "minerva",
        "subfields": [
            {
                "id": "film_analysis",
                "name": "Film Analysis",
                "chapters": [
                    {"id": "ch1", "title": "Visual Language", "minutes": 45},
                    {"id": "ch2", "title": "Cinematography", "minutes": 60},
                    {"id": "ch3", "title": "Editing", "minutes": 45},
                    {"id": "ch4", "title": "Sound Design", "minutes": 45},
                    {"id": "ch5", "title": "Genre Study", "minutes": 60}
                ]
            },
            {
                "id": "screenwriting",
                "name": "Screenwriting",
                "chapters": [
                    {"id": "ch1", "title": "Story Structure", "minutes": 45},
                    {"id": "ch2", "title": "Character Arcs", "minutes": 45},
                    {"id": "ch3", "title": "Dialogue", "minutes": 45},
                    {"id": "ch4", "title": "Scene Writing", "minutes": 60},
                    {"id": "ch5", "title": "Format & Industry", "minutes": 45}
                ]
            },
            {
                "id": "production",
                "name": "Film Production",
                "chapters": [
                    {"id": "ch1", "title": "Pre-Production", "minutes": 45},
                    {"id": "ch2", "title": "Directing Basics", "minutes": 60},
                    {"id": "ch3", "title": "Camera & Lighting", "minutes": 60},
                    {"id": "ch4", "title": "Post-Production", "minutes": 60},
                    {"id": "ch5", "title": "Distribution", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Short Film",
            "description": "Write, direct, and produce a short film",
            "requirements": ["Script", "Shot list", "Filming", "Editing", "Final cut"]
        }
    },
    
    "architecture": {
        "id": "architecture",
        "name": "Architecture",
        "icon": "🏗️",
        "description": "Design spaces that shape human experience",
        "estimated_weeks": 18,
        "daily_minutes": 45,
        "lead_persona": "ajani",
        "subfields": [
            {
                "id": "design_principles",
                "name": "Design Principles",
                "chapters": [
                    {"id": "ch1", "title": "Space & Form", "minutes": 60},
                    {"id": "ch2", "title": "Light & Shadow", "minutes": 45},
                    {"id": "ch3", "title": "Proportion & Scale", "minutes": 45},
                    {"id": "ch4", "title": "Circulation", "minutes": 45},
                    {"id": "ch5", "title": "Context & Site", "minutes": 60}
                ]
            },
            {
                "id": "technical",
                "name": "Technical Architecture",
                "chapters": [
                    {"id": "ch1", "title": "Structural Systems", "minutes": 60},
                    {"id": "ch2", "title": "Materials", "minutes": 45},
                    {"id": "ch3", "title": "Building Systems", "minutes": 60},
                    {"id": "ch4", "title": "Building Codes", "minutes": 45},
                    {"id": "ch5", "title": "Sustainable Design", "minutes": 60}
                ]
            },
            {
                "id": "representation",
                "name": "Architectural Representation",
                "chapters": [
                    {"id": "ch1", "title": "Sketching", "minutes": 45},
                    {"id": "ch2", "title": "Technical Drawing", "minutes": 60},
                    {"id": "ch3", "title": "3D Modeling", "minutes": 60},
                    {"id": "ch4", "title": "Rendering", "minutes": 60},
                    {"id": "ch5", "title": "Presentation", "minutes": 45}
                ]
            },
            {
                "id": "ancient_symbolism",
                "name": "Symbolism in Ancient Design",
                "chapters": [
                    {"id": "ch1", "title": "Sacred Geometry Fundamentals", "minutes": 45},
                    {"id": "ch2", "title": "Adinkra Symbols & Philosophical Encoding", "minutes": 45},
                    {"id": "ch3", "title": "Astronomical Alignment in Ancient Structures", "minutes": 60},
                    {"id": "ch4", "title": "Mandala Geometry & Cosmological Maps", "minutes": 45},
                    {"id": "ch5", "title": "Architecture as Cultural Memory", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Architectural Design",
            "description": "Design a complete building or space",
            "requirements": ["Concept sketches", "Floor plans", "Sections/elevations", "3D model", "Presentation boards"]
        }
    },
    
    "aerospace_engineering": {
        "id": "aerospace_engineering",
        "name": "Aerospace Engineering",
        "icon": "🚀",
        "description": "Design and build aircraft, spacecraft, and propulsion systems",
        "estimated_weeks": 22,
        "daily_minutes": 60,
        "lead_persona": "hermes",
        "advanced": True,
        "subfields": [
            {
                "id": "aerodynamics",
                "name": "Aerodynamics",
                "chapters": [
                    {"id": "ch1", "title": "Fluid Dynamics Basics", "minutes": 60},
                    {"id": "ch2", "title": "Lift, Drag & Airfoils", "minutes": 60},
                    {"id": "ch3", "title": "Boundary Layers", "minutes": 45},
                    {"id": "ch4", "title": "High-Speed Aerodynamics", "minutes": 60},
                    {"id": "ch5", "title": "CFD Fundamentals", "minutes": 60}
                ]
            },
            {
                "id": "propulsion",
                "name": "Propulsion Systems",
                "chapters": [
                    {"id": "ch1", "title": "Jet Engine Fundamentals", "minutes": 60},
                    {"id": "ch2", "title": "Rocket Propulsion", "minutes": 60},
                    {"id": "ch3", "title": "Electric Propulsion", "minutes": 45},
                    {"id": "ch4", "title": "Fuel Systems", "minutes": 45},
                    {"id": "ch5", "title": "Future Propulsion Concepts", "minutes": 60}
                ]
            },
            {
                "id": "orbital_mechanics",
                "name": "Orbital Mechanics",
                "chapters": [
                    {"id": "ch1", "title": "Kepler's Laws", "minutes": 45},
                    {"id": "ch2", "title": "Orbit Types & Parameters", "minutes": 60},
                    {"id": "ch3", "title": "Hohmann Transfers", "minutes": 60},
                    {"id": "ch4", "title": "Interplanetary Trajectories", "minutes": 60},
                    {"id": "ch5", "title": "Rendezvous & Docking", "minutes": 60}
                ]
            },
            {
                "id": "spacecraft_design",
                "name": "Spacecraft Design",
                "chapters": [
                    {"id": "ch1", "title": "Spacecraft Structures", "minutes": 60},
                    {"id": "ch2", "title": "Thermal Control Systems", "minutes": 45},
                    {"id": "ch3", "title": "Power Systems", "minutes": 45},
                    {"id": "ch4", "title": "Life Support Systems", "minutes": 60},
                    {"id": "ch5", "title": "Communications & Telemetry", "minutes": 45}
                ]
            }
        ],
        "final_project": {
            "title": "Spacecraft Mission Design",
            "description": "Design a complete spacecraft mission from concept to deployment",
            "requirements": ["Mission concept", "Spacecraft design", "Trajectory planning", "System integration", "Mission simulation"]
        }
    },
    
    "nanotechnology": {
        "id": "nanotechnology",
        "name": "Nanotechnology",
        "icon": "🔬",
        "description": "Engineer materials and devices at the molecular scale",
        "estimated_weeks": 18,
        "daily_minutes": 45,
        "lead_persona": "hermes",
        "advanced": True,
        "subfields": [
            {
                "id": "nanomaterials",
                "name": "Nanomaterials",
                "chapters": [
                    {"id": "ch1", "title": "Quantum Effects at Nanoscale", "minutes": 60},
                    {"id": "ch2", "title": "Carbon Nanotubes & Graphene", "minutes": 60},
                    {"id": "ch3", "title": "Quantum Dots", "minutes": 45},
                    {"id": "ch4", "title": "Nanocomposites", "minutes": 45},
                    {"id": "ch5", "title": "Self-Assembly", "minutes": 60}
                ]
            },
            {
                "id": "nanofabrication",
                "name": "Nanofabrication",
                "chapters": [
                    {"id": "ch1", "title": "Lithography Techniques", "minutes": 60},
                    {"id": "ch2", "title": "Deposition Methods", "minutes": 45},
                    {"id": "ch3", "title": "Etching & Patterning", "minutes": 45},
                    {"id": "ch4", "title": "Bottom-Up Assembly", "minutes": 60},
                    {"id": "ch5", "title": "Molecular Machines", "minutes": 60}
                ]
            },
            {
                "id": "nanomedicine",
                "name": "Nanomedicine",
                "chapters": [
                    {"id": "ch1", "title": "Drug Delivery Systems", "minutes": 60},
                    {"id": "ch2", "title": "Nanosensors", "minutes": 45},
                    {"id": "ch3", "title": "Tissue Engineering", "minutes": 60},
                    {"id": "ch4", "title": "Cancer Nanotech", "minutes": 60},
                    {"id": "ch5", "title": "Neural Interfaces", "minutes": 60}
                ]
            }
        ],
        "final_project": {
            "title": "Nanodevice Design",
            "description": "Design a nanodevice for a specific application",
            "requirements": ["Concept design", "Material selection", "Fabrication plan", "Testing protocol", "Application analysis"]
        }
    }
}


def get_all_fields():
    """Return list of all fields with summary info."""
    return [
        {
            "id": field["id"],
            "name": field["name"],
            "icon": field["icon"],
            "description": field["description"],
            "estimated_weeks": field["estimated_weeks"],
            "daily_minutes": field["daily_minutes"],
            "lead_persona": field["lead_persona"],
            "total_chapters": sum(len(sf["chapters"]) for sf in field["subfields"]),
            "total_subfields": len(field["subfields"])
        }
        for field in CURRICULUM.values()
    ]


def get_field(field_id: str):
    """Get full details for a specific field."""
    return CURRICULUM.get(field_id)


def get_subfield(field_id: str, subfield_id: str):
    """Get a specific subfield with its chapters."""
    field = CURRICULUM.get(field_id)
    if not field:
        return None
    for sf in field["subfields"]:
        if sf["id"] == subfield_id:
            return sf
    return None


def get_chapter(field_id: str, subfield_id: str, chapter_id: str):
    """Get a specific chapter."""
    subfield = get_subfield(field_id, subfield_id)
    if not subfield:
        return None
    for ch in subfield["chapters"]:
        if ch["id"] == chapter_id:
            return ch
    return None


def calculate_field_total_time(field_id: str):
    """Calculate total study time for a field in minutes."""
    field = CURRICULUM.get(field_id)
    if not field:
        return 0
    total = 0
    for sf in field["subfields"]:
        for ch in sf["chapters"]:
            total += ch["minutes"]
    return total


def estimate_completion_days(field_id: str, daily_minutes: int = 30):
    """Estimate days to complete a field at given daily study rate."""
    total_minutes = calculate_field_total_time(field_id)
    return (total_minutes + daily_minutes - 1) // daily_minutes
