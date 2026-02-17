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

const inflightGetRequests = new Map<string, Promise<unknown>>();

async function fetchJson<T>(
  url: string,
  errorPrefix: string,
  init?: RequestInit,
  includeErrorBody = false
): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    if (includeErrorBody) {
      const text = await response.text();
      throw new Error(`${errorPrefix} (${response.status}): ${text}`);
    }
    throw new Error(`${errorPrefix} (${response.status})`);
  }
  return (await response.json()) as T;
}

// Coalesce concurrent GETs for identical URLs.
async function fetchJsonGet<T>(url: string, errorPrefix: string): Promise<T> {
  const existing = inflightGetRequests.get(url) as Promise<T> | undefined;
  if (existing) {
    return existing;
  }
  const request = fetchJson<T>(url, errorPrefix).finally(() => {
    inflightGetRequests.delete(url);
  });
  inflightGetRequests.set(url, request as Promise<unknown>);
  return request;
}

export async function orchestrateAtlas(
  baseUrl: string,
  payload: AtlasRequest
): Promise<AtlasResponse> {
  return fetchJson<AtlasResponse>(
    `${baseUrl}/route`,
    "Atlas orchestrate failed",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    true
  );
}

export async function orchestrateAtlasViaLegacyEndpoint(
  baseUrl: string,
  payload: AtlasRequest
): Promise<AtlasResponse> {
  return fetchJson<AtlasResponse>(
    `${baseUrl}/atlas/orchestrate`,
    "Atlas orchestrate failed",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    true
  );
}

export async function getProjectMemory(baseUrl: string, project: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/projects/${encodeURIComponent(project)}/memory`,
    "Atlas memory fetch failed"
  );
}

export async function getAtlasVision(baseUrl: string) {
  return fetchJsonGet(`${baseUrl}/atlas/vision`, "Atlas vision fetch failed");
}

export async function getAtlasDomains(baseUrl: string) {
  return fetchJsonGet(`${baseUrl}/atlas/domains`, "Atlas domains fetch failed");
}

export async function getActivePrototype(baseUrl: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/prototypes/active`,
    "Atlas active prototype fetch failed"
  );
}

export async function getProjectRegistry(baseUrl: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/project-registry`,
    "Atlas project registry fetch failed"
  );
}

export async function searchProjectRegistry(baseUrl: string, query: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/project-registry/search?q=${encodeURIComponent(query)}`,
    "Atlas project registry search failed"
  );
}

export async function getProjectRegistryItem(baseUrl: string, projectId: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/project-registry/${encodeURIComponent(projectId)}`,
    "Atlas project registry item failed"
  );
}

export async function getCapabilityMatrix(baseUrl: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/capability-matrix`,
    "Atlas capability matrix fetch failed"
  );
}

export async function getTeachingFramework(baseUrl: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/teaching-framework`,
    "Atlas teaching framework fetch failed"
  );
}

export async function getAcademicIntegrationPlan(baseUrl: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/academic-integration-plan`,
    "Atlas academic integration plan fetch failed"
  );
}

export async function getOperationalRules(baseUrl: string) {
  return fetchJsonGet(
    `${baseUrl}/atlas/operational-rules`,
    "Atlas operational rules fetch failed"
  );
}

export async function getDoctrine(baseUrl: string) {
  return fetchJsonGet(`${baseUrl}/atlas/doctrine`, "Atlas doctrine fetch failed");
}

