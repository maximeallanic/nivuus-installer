/**
 * WebSocket API client for Docker Marketplace
 */

import type {
  HomeAssistant,
  CatalogResponse,
  ConfigResponse,
  InstalledResponse,
  InstallResponse,
  LogsResponse,
  AppStatusResponse,
  InstallConfig,
} from "./types";

export class MarketplaceApi {
  constructor(private hass: HomeAssistant) {}

  /**
   * Get the full app catalog
   */
  async getCatalog(): Promise<CatalogResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/catalog",
    });
  }

  /**
   * Get installed apps with status
   */
  async getInstalled(): Promise<InstalledResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/installed",
    });
  }

  /**
   * Get detailed status for an app
   */
  async getAppStatus(appId: string): Promise<AppStatusResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/app_status",
      app_id: appId,
    });
  }

  /**
   * Install an app from the catalog
   */
  async installApp(appId: string, config?: InstallConfig): Promise<InstallResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/install",
      app_id: appId,
      config: config || {},
    });
  }

  /**
   * Remove an installed app
   */
  async removeApp(appId: string, removeData = false): Promise<InstallResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/remove",
      app_id: appId,
      remove_data: removeData,
    });
  }

  /**
   * Get logs for an app
   */
  async getLogs(appId: string, tail = 100): Promise<LogsResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/logs",
      app_id: appId,
      tail,
    });
  }

  /**
   * Start an app
   */
  async startApp(appId: string): Promise<InstallResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/start",
      app_id: appId,
    });
  }

  /**
   * Stop an app
   */
  async stopApp(appId: string): Promise<InstallResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/stop",
      app_id: appId,
    });
  }

  /**
   * Restart an app
   */
  async restartApp(appId: string): Promise<InstallResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/restart",
      app_id: appId,
    });
  }

  /**
   * Update an app using HA service (no WebSocket command for update yet)
   */
  async updateApp(appId: string): Promise<void> {
    return this.hass.callService("docker_marketplace", "update_app", {
      app_id: appId,
    });
  }

  /**
   * Get configuration for an installed app
   */
  async getConfig(appId: string): Promise<ConfigResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/get_config",
      app_id: appId,
    });
  }

  /**
   * Update configuration for an installed app
   */
  async updateConfig(appId: string, config: InstallConfig): Promise<InstallResponse> {
    return this.hass.connection.sendMessagePromise({
      type: "docker_marketplace/update_config",
      app_id: appId,
      config,
    });
  }
}
