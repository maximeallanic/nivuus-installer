/**
 * Types for Docker Marketplace Panel
 */

// Home Assistant types (simplified)
export interface HomeAssistant {
  connection: Connection;
  language: string;
  callService: (domain: string, service: string, data?: Record<string, unknown>) => Promise<void>;
}

export interface Connection {
  sendMessagePromise: <T>(message: WebSocketMessage) => Promise<T>;
  subscribeEvents: (callback: (event: unknown) => void, eventType: string) => Promise<() => void>;
}

export interface WebSocketMessage {
  type: string;
  [key: string]: unknown;
}

// Catalog types
export interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
  app_count: number;
}

export interface AppSummary {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  logo: string;
  version: string;
  tags: string[];
  // Optional fields included in detailed response
  ports?: Port[];
  environment?: EnvVar[];
  requirements?: {
    min_memory: number;
    recommended_memory: number;
    gpu: string;
  };
}

export interface AppDetail extends AppSummary {
  maintainer: string;
  website: string;
  documentation: string;
  requirements: {
    min_memory: number;
    recommended_memory: number;
    gpu: string;
  };
  ports: Port[];
  volumes: Volume[];
  environment: EnvVar[];
  depends_on: string[];
}

export interface Port {
  container: number;
  host: number;
  protocol: string;
  description: string;
}

export interface Volume {
  name: string;
  container: string;
  description: string;
  required: boolean;
}

export interface EnvVar {
  name: string;
  default: string;
  description: string;
  required: boolean;
  secret: boolean;
}

export interface CatalogResponse {
  categories: Category[];
  apps: AppSummary[];
}

// Installed apps types
export interface InstalledApp {
  id: string;
  name: string;
  state: AppState;
  image: string;
  version: string;
  cpu_percent: number;
  memory_usage: number;
  memory_percent: number;
}

export interface InstalledResponse {
  apps: InstalledApp[];
}

export type AppState = "running" | "stopped" | "installing" | "error" | "not_installed";

// Install config
export interface InstallConfig {
  [key: string]: string | number;
}

// API response types
export interface InstallResponse {
  status: "success" | "error";
  app_id: string;
}

export interface LogsResponse {
  app_id: string;
  logs: string;
}

export interface AppStatusResponse {
  app_id: string;
  catalog: AppDetail | null;
  installed: boolean;
  status?: {
    state: AppState;
    image: string;
    version: string;
    cpu_percent: number;
    memory_usage: number;
    memory_percent: number;
  };
}

export interface ConfigSchemaPort {
  key: string;
  container: number;
  host: number;
  protocol: string;
  description: string;
}

export interface ConfigSchemaVolume {
  key: string;
  name: string;
  container: string;
  default_host: string;
  description: string;
  required: boolean;
}

export interface ConfigSchemaEnv {
  key: string;
  name: string;
  default: string;
  description: string;
  required: boolean;
  secret: boolean;
}

export interface ConfigSchema {
  ports: ConfigSchemaPort[];
  volumes: ConfigSchemaVolume[];
  environment: ConfigSchemaEnv[];
}

export interface ConfigResponse {
  app_id: string;
  config: InstallConfig;
  schema: ConfigSchema | null;
}
