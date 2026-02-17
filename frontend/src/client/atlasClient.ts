export type AtlasMode = "mentor" | "warrior" | "builder";
export type PipelineStage = "blueprint" | "build" | "modify";

export interface AtlasRequest {
  project: string;
  user_input: string;
  mode?: AtlasMode;
  context?: Record<string, unknown>;
  pipeline_stage?: PipelineStage;
}

export interface AtlasResponse {
  project: string;
  version: string;
  project_registry_entry?: Record<string, unknown> | null;
  mode: AtlasMode;
  intent: string;
  intent_reason: string;
  pipeline_stage: PipelineStage;
  validation_status: "ok" | "flagged" | "blocked";
  ajani: Record<string, unknown>;
  minerva: Record<string, unknown>;
  hermes: Record<string, unknown>;
  project_memory: Record<string, unknown>;
}

export async function orchestrateAtlas(
  baseUrl: string,
  payload: AtlasRequest
): Promise<AtlasResponse> {
  const response = await fetch(`${baseUrl}/route`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Atlas orchestrate failed (${response.status}): ${text}`);
  }

  return (await response.json()) as AtlasResponse;
}

export async function orchestrateAtlasViaLegacyEndpoint(
  baseUrl: string,
  payload: AtlasRequest
): Promise<AtlasResponse> {
  const response = await fetch(`${baseUrl}/atlas/orchestrate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Atlas orchestrate failed (${response.status}): ${text}`);
  }
  return (await response.json()) as AtlasResponse;
}

export async function getProjectMemory(baseUrl: string, project: string) {
  const response = await fetch(
    `${baseUrl}/atlas/projects/${encodeURIComponent(project)}/memory`
  );
  if (!response.ok) {
    throw new Error(`Atlas memory fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getAtlasVision(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/vision`);
  if (!response.ok) {
    throw new Error(`Atlas vision fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getAtlasDomains(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/domains`);
  if (!response.ok) {
    throw new Error(`Atlas domains fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getActivePrototype(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/prototypes/active`);
  if (!response.ok) {
    throw new Error(`Atlas active prototype fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getProjectRegistry(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/project-registry`);
  if (!response.ok) {
    throw new Error(`Atlas project registry fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getCapabilityMatrix(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/capability-matrix`);
  if (!response.ok) {
    throw new Error(`Atlas capability matrix fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getTeachingFramework(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/teaching-framework`);
  if (!response.ok) {
    throw new Error(`Atlas teaching framework fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getAcademicIntegrationPlan(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/academic-integration-plan`);
  if (!response.ok) {
    throw new Error(`Atlas academic integration plan fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getOperationalRules(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/operational-rules`);
  if (!response.ok) {
    throw new Error(`Atlas operational rules fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getDoctrine(baseUrl: string) {
  const response = await fetch(`${baseUrl}/atlas/doctrine`);
  if (!response.ok) {
    throw new Error(`Atlas doctrine fetch failed (${response.status})`);
  }
  return response.json();
}

