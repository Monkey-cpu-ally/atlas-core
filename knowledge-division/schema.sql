-- ATLAS Knowledge Division Starter Schema
-- Database: atlas_knowledge_division

CREATE DATABASE IF NOT EXISTS atlas_knowledge_division;
USE atlas_knowledge_division;

-- AI agents in the ATLAS system
CREATE TABLE ai_agents (
    agent_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    role_title VARCHAR(100) NOT NULL,
    domain_focus TEXT NOT NULL,
    voice_style VARCHAR(255),
    color_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The main 22 Knowledge Banks
CREATE TABLE knowledge_banks (
    bank_id INT PRIMARY KEY AUTO_INCREMENT,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    primary_agent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_agent_id) REFERENCES ai_agents(agent_id)
);

-- Individual knowledge entries
CREATE TABLE knowledge_entries (
    entry_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    what_is_it TEXT,
    how_it_works TEXT,
    why_it_matters TEXT,
    problem_solved TEXT,
    strengths TEXT,
    weaknesses TEXT,
    known_facts TEXT,
    assumptions TEXT,
    unknowns TEXT,
    technical_risks TEXT,
    safety_risks TEXT,
    ethical_risks TEXT,
    legal_risks TEXT,
    cost_estimate TEXT,
    manufacturing_difficulty ENUM('Low', 'Medium', 'High', 'Frontier') DEFAULT 'Medium',
    improvement_potential TEXT,
    luxury_version TEXT,
    next_generation_version TEXT,
    final_status ENUM('Unknown', 'Learning', 'Partially Verified', 'Verified', 'Tested', 'Prototype', 'Project Ready', 'ATLAS Original') DEFAULT 'Unknown',
    mastery_level TINYINT CHECK (mastery_level BETWEEN 1 AND 10),
    confidence_level ENUM('Low', 'Medium', 'High') DEFAULT 'Low',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Many-to-many link between entries and banks
CREATE TABLE entry_bank_links (
    entry_id INT NOT NULL,
    bank_id INT NOT NULL,
    relationship_type ENUM('Primary', 'Related') DEFAULT 'Related',
    PRIMARY KEY (entry_id, bank_id),
    FOREIGN KEY (entry_id) REFERENCES knowledge_entries(entry_id) ON DELETE CASCADE,
    FOREIGN KEY (bank_id) REFERENCES knowledge_banks(bank_id) ON DELETE CASCADE
);

-- Sources used for knowledge entries
CREATE TABLE sources (
    source_id INT PRIMARY KEY AUTO_INCREMENT,
    entry_id INT NOT NULL,
    source_title VARCHAR(255) NOT NULL,
    source_url TEXT,
    source_type ENUM('Book', 'Paper', 'Patent', 'Official Documentation', 'University', 'Video', 'Article', 'Dataset', 'User Notes', 'Image', 'Other') DEFAULT 'Other',
    source_quality ENUM('A-Level', 'B-Level', 'C-Level', 'D-Level', 'F-Level') DEFAULT 'D-Level',
    notes TEXT,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES knowledge_entries(entry_id) ON DELETE CASCADE
);

-- AI reviews for each knowledge entry
CREATE TABLE ai_reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    entry_id INT NOT NULL,
    agent_id INT NOT NULL,
    review_summary TEXT,
    strengths_seen TEXT,
    weaknesses_seen TEXT,
    improvement_ideas TEXT,
    risk_notes TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES knowledge_entries(entry_id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(agent_id)
);

-- Council-level review
CREATE TABLE council_reviews (
    council_review_id INT PRIMARY KEY AUTO_INCREMENT,
    entry_id INT NOT NULL,
    final_judgment TEXT NOT NULL,
    confidence ENUM('Low', 'Medium', 'High') DEFAULT 'Low',
    biggest_opportunity TEXT,
    biggest_risk TEXT,
    should_study_further BOOLEAN DEFAULT TRUE,
    should_become_project BOOLEAN DEFAULT FALSE,
    next_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES knowledge_entries(entry_id) ON DELETE CASCADE
);

-- ATLAS projects linked to knowledge entries
CREATE TABLE projects (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    status ENUM('Idea', 'Research', 'Design', 'Prototype', 'Testing', 'Paused', 'Complete') DEFAULT 'Idea',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE entry_project_links (
    entry_id INT NOT NULL,
    project_id INT NOT NULL,
    usage_note TEXT,
    PRIMARY KEY (entry_id, project_id),
    FOREIGN KEY (entry_id) REFERENCES knowledge_entries(entry_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- Style and design reviews
CREATE TABLE style_reviews (
    style_review_id INT PRIMARY KEY AUTO_INCREMENT,
    entry_id INT NOT NULL,
    looks_strong_because TEXT,
    looks_weak_because TEXT,
    resembles_brand TEXT,
    feels_cheap_generic_luxury TEXT,
    originality_notes TEXT,
    final_design_judgment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES knowledge_entries(entry_id) ON DELETE CASCADE
);

-- Starter AI agents
INSERT INTO ai_agents (name, role_title, domain_focus, voice_style, color_code) VALUES
('Hermes', 'Architect and Engineer', 'Engineering, robotics, manufacturing, software, materials, machines, physics, architecture', 'Deep, precise, technical, builder-focused', 'off-white'),
('Minerva', 'Scholar of Nature and Story', 'Biology, botany, medicine, environment, art, storytelling, language, history', 'Wise, poetic, clear, nature-centered', 'teal'),
('Ajani', 'Strategist and Commander', 'Strategy, economics, psychology, leadership, risk, security, project planning', 'Direct, disciplined, protective, tactical', 'crimson'),
('Council', 'Final Review Council', 'Combined review across all ATLAS domains', 'Balanced, evidence-first, decisive', 'purple');

-- Starter Knowledge Banks
INSERT INTO knowledge_banks (bank_name, description, primary_agent_id) VALUES
('Artificial Intelligence', 'Machine learning, LLMs, computer vision, agents, AI memory, AI safety, and intelligent systems.', 1),
('Robotics', 'Humanoids, green robots, industrial robots, bio-inspired robots, drones, actuators, and control systems.', 1),
('Software Engineering', 'Programming, databases, APIs, applications, testing, deployment, cybersecurity, and system design.', 1),
('Mechanical Engineering', 'Motors, gears, hydraulics, pneumatics, mechanisms, force, torque, machine design, and manufacturing constraints.', 1),
('Electrical Engineering', 'Circuits, wiring, PCBs, sensors, batteries, power electronics, embedded systems, and signal processing.', 1),
('Materials Science', 'Metals, polymers, ceramics, composites, graphene, carbon fiber, smart materials, biomaterials, and coatings.', 1),
('Physics', 'Mechanics, electromagnetism, thermodynamics, optics, acoustics, quantum mechanics, relativity, and simulation.', 1),
('Chemistry', 'Organic, inorganic, electrochemistry, polymers, catalysts, fuels, corrosion, and reaction systems.', 2),
('Biology', 'Cells, genetics, microbiology, evolution, animals, humans, tissue systems, and bio-inspired design.', 2),
('Medicine', 'Anatomy, physiology, neuroscience, pharmacology, medical devices, diagnostics, and regenerative medicine.', 2),
('Botany', 'Plants, seeds, growth rates, medicinal plants, soil, hydroponics, environmental plants, and Minerva plant library.', 2),
('Environmental Science', 'Ecosystems, water, soil, recycling, pollution, clean energy, sustainability, and restoration systems.', 2),
('Aerospace', 'Aircraft, rockets, eVTOL, drones, satellites, propulsion, aerodynamics, avionics, and space systems.', 1),
('Architecture', 'Buildings, city design, interiors, luxury spaces, future habitats, factories, and environmental design.', 1),
('Manufacturing', 'CNC, 3D printing, casting, forging, assembly lines, automation, tooling, and factory systems.', 1),
('Mathematics', 'Algebra, geometry, calculus, probability, statistics, optimization, graph theory, algorithms, and formal reasoning.', 1),
('Economics & Business', 'Markets, competition, luxury brands, pricing, supply chains, finance, ownership, strategy, and wealth systems.', 3),
('History', 'Civilizations, inventions, wars, trade, architecture, technology timelines, cultural shifts, and lessons from the past.', 2),
('Psychology', 'Human behavior, learning, creativity, leadership, attention, motivation, persuasion, UX, and decision-making.', 3),
('Art & Design', 'Luxury fashion, industrial design, animation, painting, sculpture, typography, color, composition, and beauty judgment.', 2),
('Storytelling', 'Books, movies, games, worldbuilding, plot, character, mystery, horror, environmental storytelling, and mythology.', 2),
('Philosophy', 'Logic, ethics, systems thinking, meaning, leadership, responsibility, truth, beauty, invention, and decision principles.', 3);

-- Starter projects
INSERT INTO projects (project_name, description, status) VALUES
('Weaver Project', 'Multi-arm suspended robotics and manufacturing system connected to ATLAS AI.', 'Research'),
('Green Robots', 'Bio-inspired environmental robots for repair, cleaning, planting, and sustainable field work.', 'Research'),
('Power Cell', 'Gel-stack salt/fresh water copper energy storage and generation concept.', 'Research'),
('Resonance Scanner', 'Wearable electromagnetic, acoustic, signal, and control-system scanner concept.', 'Research'),
('Metal Flower', 'Seed-housing environmental plant deployment and restoration system.', 'Research'),
('ATLAS HUD', 'Visual interface with AI rings, face windows, memory tabs, and project control.', 'Design'),
('Digital Twin Engine', 'Simulation system for machines, environments, projects, and design testing.', 'Idea'),
('Quantum Simulator', 'Classical simulation of quantum-inspired optimization and reasoning systems.', 'Idea'),
('Luxury Style Engine', 'Fashion, art, brand, design, and aesthetic judgment system for ATLAS.', 'Research');
