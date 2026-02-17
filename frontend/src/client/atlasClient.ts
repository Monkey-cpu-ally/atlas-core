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

