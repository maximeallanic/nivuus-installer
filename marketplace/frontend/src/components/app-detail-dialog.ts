/**
 * App Detail Dialog Component
 * Uses ha-dialog for HA-native look
 */

import { LitElement, html, css, PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type { AppSummary, InstalledApp, InstallConfig, HomeAssistant, ConfigSchema } from "../types";
import { MarketplaceApi } from "../api";

@customElement("app-detail-dialog")
export class AppDetailDialog extends LitElement {
  @property({ attribute: false }) hass?: HomeAssistant;
  @property({ type: Object }) app?: AppSummary;
  @property({ type: Object }) installed?: InstalledApp;
  @property({ type: Boolean }) open = false;
  @property({ type: Boolean }) loading = false;

  @state() private _config: InstallConfig = {};
  @state() private _savedConfig: InstallConfig = {};
  @state() private _configSchema: ConfigSchema | null = null;
  @state() private _activeTab = "status";
  @state() private _confirmDelete = false;
  @state() private _configLoading = false;
  @state() private _configDirty = false;
  @state() private _savingConfig = false;

  private _api?: MarketplaceApi;

  static styles = css`
    ha-dialog {
      --mdc-dialog-min-width: 500px;
      --mdc-dialog-max-width: 600px;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }

    .icon-container {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      background: var(--primary-color);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .icon-container ha-icon {
      color: white;
      --mdc-icon-size: 28px;
    }

    .title-section {
      flex: 1;
    }

    .app-name {
      font-size: 20px;
      font-weight: 500;
      color: var(--primary-text-color);
      margin: 0 0 4px 0;
    }

    .app-meta {
      font-size: 13px;
      color: var(--secondary-text-color);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-indicator {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 500;
    }

    .status-indicator.running {
      background: rgba(var(--rgb-green), 0.15);
      color: var(--success-color, #4caf50);
    }

    .status-indicator.stopped {
      background: rgba(var(--rgb-red), 0.15);
      color: var(--error-color, #f44336);
    }

    .description {
      font-size: 14px;
      line-height: 1.5;
      color: var(--primary-text-color);
      margin-bottom: 16px;
    }

    .section {
      margin-bottom: 20px;
    }

    .section-title {
      font-size: 11px;
      font-weight: 600;
      color: var(--secondary-text-color);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }

    .info-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }

    .info-item {
      padding: 12px;
      background: var(--secondary-background-color);
      border-radius: 8px;
    }

    .info-label {
      font-size: 11px;
      color: var(--secondary-text-color);
      margin-bottom: 4px;
    }

    .info-value {
      font-size: 14px;
      font-weight: 500;
      color: var(--primary-text-color);
    }

    .field {
      margin-bottom: 16px;
    }

    .field-label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: var(--primary-text-color);
      margin-bottom: 8px;
    }

    .field-hint {
      font-size: 12px;
      color: var(--secondary-text-color);
      margin-top: 4px;
    }

    .field-required {
      color: var(--error-color);
      font-size: 11px;
      margin-left: 4px;
    }

    .required-notice {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      margin-bottom: 16px;
      background: rgba(var(--rgb-amber), 0.1);
      border-radius: 8px;
      font-size: 13px;
      color: var(--primary-text-color);
    }

    .required-notice ha-icon {
      color: var(--warning-color);
      --mdc-icon-size: 20px;
    }

    ha-textfield {
      display: block;
      width: 100%;
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding-top: 16px;
      border-top: 1px solid var(--divider-color);
      margin-top: 16px;
    }

    ha-button {
      --mdc-theme-primary: var(--primary-color);
    }

    .danger-btn {
      --mdc-theme-primary: var(--error-color);
      --ha-label-badge-color: var(--error-color);
    }

    .danger-btn::part(button) {
      color: var(--error-color);
    }

    .tabs {
      display: flex;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }

    .tab {
      padding: 8px 16px;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
      background: none;
      border: none;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
      transition: color 0.2s, border-color 0.2s;
    }

    .tab:hover {
      color: var(--primary-text-color);
    }

    .tab.active {
      color: var(--primary-color);
      border-bottom-color: var(--primary-color);
    }

    .requirements-grid {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .requirement {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--secondary-background-color);
      border-radius: 8px;
      font-size: 13px;
      color: var(--primary-text-color);
    }

    .requirement ha-icon {
      color: var(--secondary-text-color);
      --mdc-icon-size: 18px;
    }

    .confirm-delete {
      background: rgba(var(--rgb-red), 0.1);
      border: 1px solid var(--error-color);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }

    .confirm-delete-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 500;
      color: var(--error-color);
      margin-bottom: 8px;
    }

    .confirm-delete-title ha-icon {
      --mdc-icon-size: 20px;
    }

    .confirm-delete-text {
      font-size: 13px;
      color: var(--primary-text-color);
      margin-bottom: 12px;
    }

    .confirm-delete-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    }

    .tab-bar {
      display: flex;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }

    .tab-button {
      padding: 12px 16px;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
      background: none;
      border: none;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
      transition: color 0.2s, border-color 0.2s;
    }

    .tab-button:hover {
      color: var(--primary-text-color);
    }

    .tab-button.active {
      color: var(--primary-color);
      border-bottom-color: var(--primary-color);
    }

    .tab-content {
      min-height: 150px;
    }

    .config-message {
      padding: 12px;
      background: rgba(var(--rgb-amber), 0.1);
      border-radius: 8px;
      font-size: 13px;
      color: var(--primary-text-color);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .config-message ha-icon {
      color: var(--warning-color);
      --mdc-icon-size: 20px;
    }

    .config-actions {
      display: flex;
      gap: 8px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--divider-color);
    }

    @media (max-width: 600px) {
      ha-dialog {
        --mdc-dialog-min-width: 90vw;
      }
      .info-grid {
        grid-template-columns: 1fr;
      }
    }

    .loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(var(--rgb-card-background-color, 255, 255, 255), 0.9);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 10;
      border-radius: var(--ha-card-border-radius, 12px);
    }

    .loading-overlay span {
      margin-top: 16px;
      font-size: 14px;
      color: var(--primary-text-color);
    }

    .dialog-content {
      position: relative;
    }
  `;

  protected updated(changedProps: PropertyValues) {
    if (changedProps.has("hass") && this.hass && !this._api) {
      this._api = new MarketplaceApi(this.hass);
    }

    // Load config when dialog opens or tab changes to config
    if (changedProps.has("open") && this.open && this.installed) {
      this._loadConfig();
    }
  }

  private async _loadConfig() {
    if (!this._api || !this.app?.id) return;

    this._configLoading = true;
    try {
      const response = await this._api.getConfig(this.app.id);
      this._savedConfig = response.config || {};
      this._config = { ...this._savedConfig };
      this._configSchema = response.schema;
      this._configDirty = false;
    } catch (err) {
      console.error("Failed to load config:", err);
    } finally {
      this._configLoading = false;
    }
  }

  render() {
    if (!this.app) return html``;

    return html`
      <ha-dialog
        ?open=${this.open}
        @closed=${this._handleClose}
        hideActions
      >
        <div class="dialog-content">
          ${this.loading
            ? html`
                <div class="loading-overlay">
                  <ha-circular-progress indeterminate></ha-circular-progress>
                  <span>Installation en cours...</span>
                </div>
              `
            : ""}

          <div class="header">
            <div class="icon-container">
              <ha-icon .icon=${this.app.icon || "mdi:docker"}></ha-icon>
            </div>
            <div class="title-section">
              <h2 class="app-name">${this.app.name}</h2>
              <div class="app-meta">
                <span>v${this.app.version}</span>
                ${this.installed
                  ? html`
                      <span class="status-indicator ${this.installed.state}">
                        ${this._getStatusLabel(this.installed.state)}
                      </span>
                    `
                  : ""}
              </div>
            </div>
          </div>

          <p class="description">${this.app.description}</p>

          ${this._confirmDelete ? this._renderConfirmDelete() : ""}

          ${this.installed ? this._renderInstalledTabs() : this._renderInstall()}

          ${this._confirmDelete ? "" : this._renderActions()}
        </div>
      </ha-dialog>
    `;
  }

  private _renderConfirmDelete() {
    return html`
      <div class="confirm-delete">
        <div class="confirm-delete-title">
          <ha-icon icon="mdi:alert"></ha-icon>
          Confirmer la suppression
        </div>
        <div class="confirm-delete-text">
          Êtes-vous sûr de vouloir supprimer <strong>${this.app?.name}</strong> ?
          Cette action est irréversible.
        </div>
        <div class="confirm-delete-actions">
          <ha-button @click=${() => (this._confirmDelete = false)}>Annuler</ha-button>
          <ha-button class="danger-btn" @click=${this._confirmRemove}>Supprimer</ha-button>
        </div>
      </div>
    `;
  }

  private _renderInstalledTabs() {
    return html`
      <div class="tab-bar">
        <button
          class="tab-button ${this._activeTab === "status" ? "active" : ""}"
          @click=${() => (this._activeTab = "status")}
        >
          Statut
        </button>
        <button
          class="tab-button ${this._activeTab === "config" ? "active" : ""}"
          @click=${() => (this._activeTab = "config")}
        >
          Configuration
        </button>
      </div>
      <div class="tab-content">
        ${this._activeTab === "status" ? this._renderInstalled() : this._renderConfigTab()}
      </div>
    `;
  }

  private _renderConfigTab() {
    if (this._configLoading) {
      return html`
        <div class="loading-container" style="padding: 40px; text-align: center;">
          <ha-circular-progress indeterminate></ha-circular-progress>
          <p style="margin-top: 16px; color: var(--secondary-text-color);">Chargement de la configuration...</p>
        </div>
      `;
    }

    if (!this._configSchema) {
      return html`
        <div class="section">
          <p style="color: var(--secondary-text-color); font-size: 13px;">
            Aucune configuration disponible pour cette application.
          </p>
        </div>
      `;
    }

    const hasPorts = this._configSchema.ports.length > 0;
    const hasVolumes = this._configSchema.volumes.length > 0;
    const hasEnv = this._configSchema.environment.length > 0;

    if (!hasPorts && !hasVolumes && !hasEnv) {
      return html`
        <div class="section">
          <p style="color: var(--secondary-text-color); font-size: 13px;">
            Cette application utilise la configuration par défaut.
          </p>
        </div>
      `;
    }

    return html`
      ${this._configDirty
        ? html`
            <div class="config-message">
              <ha-icon icon="mdi:alert-circle"></ha-icon>
              Des modifications non enregistrées. Redémarrez l'application après sauvegarde.
            </div>
          `
        : ""}

      ${hasPorts
        ? html`
            <div class="section">
              <div class="section-title">Ports</div>
              ${this._configSchema.ports.map(
                (port) => html`
                  <div class="field">
                    <label class="field-label">${port.description || `Port ${port.container}`}</label>
                    <ha-textfield
                      type="number"
                      .value=${String(this._config[port.key] ?? port.host)}
                      @input=${(e: Event) => this._updateConfigField(port.key, (e.target as HTMLInputElement).value)}
                    ></ha-textfield>
                    <span class="field-hint">Port conteneur: ${port.container}/${port.protocol}</span>
                  </div>
                `
              )}
            </div>
          `
        : ""}

      ${hasVolumes
        ? html`
            <div class="section">
              <div class="section-title">Volumes</div>
              ${this._configSchema.volumes.map(
                (vol) => html`
                  <div class="field">
                    <label class="field-label">
                      ${vol.description || vol.name}
                      ${vol.required ? html`<span style="color: var(--error-color)">*</span>` : ""}
                    </label>
                    <ha-textfield
                      .value=${String(this._config[vol.key] ?? vol.default_host ?? "")}
                      @input=${(e: Event) => this._updateConfigField(vol.key, (e.target as HTMLInputElement).value)}
                    ></ha-textfield>
                    <span class="field-hint">Chemin conteneur: ${vol.container}</span>
                  </div>
                `
              )}
            </div>
          `
        : ""}

      ${hasEnv
        ? html`
            <div class="section">
              <div class="section-title">Variables d'environnement</div>
              ${this._configSchema.environment.map(
                (env) => html`
                  <div class="field">
                    <label class="field-label">
                      ${env.description || env.name}
                      ${env.required ? html`<span style="color: var(--error-color)">*</span>` : ""}
                    </label>
                    <ha-textfield
                      .type=${env.secret ? "password" : "text"}
                      .value=${String(this._config[env.key] ?? env.default ?? "")}
                      @input=${(e: Event) => this._updateConfigField(env.key, (e.target as HTMLInputElement).value)}
                    ></ha-textfield>
                  </div>
                `
              )}
            </div>
          `
        : ""}

      ${this._configDirty
        ? html`
            <div class="config-actions">
              <ha-button @click=${this._resetConfig}>Annuler</ha-button>
              <ha-button unelevated ?disabled=${this._savingConfig} @click=${this._saveConfig}>
                ${this._savingConfig ? "Enregistrement..." : "Enregistrer"}
              </ha-button>
            </div>
          `
        : ""}
    `;
  }

  private _updateConfigField(key: string, value: string) {
    this._config = { ...this._config, [key]: value };
    this._configDirty = JSON.stringify(this._config) !== JSON.stringify(this._savedConfig);
  }

  private _resetConfig() {
    this._config = { ...this._savedConfig };
    this._configDirty = false;
  }

  private async _saveConfig() {
    if (!this._api || !this.app?.id) return;

    this._savingConfig = true;
    try {
      await this._api.updateConfig(this.app.id, this._config);
      this._savedConfig = { ...this._config };
      this._configDirty = false;
    } catch (err) {
      console.error("Failed to save config:", err);
    } finally {
      this._savingConfig = false;
    }
  }

  private _renderInstalled() {
    if (!this.installed) return "";

    return html`
      <div class="section">
        <div class="section-title">Statut</div>
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">État</div>
            <div class="info-value">${this._getStatusLabel(this.installed.state)}</div>
          </div>
          <div class="info-item">
            <div class="info-label">Image</div>
            <div class="info-value">${this.installed.image}</div>
          </div>
          ${this.installed.state === "running"
            ? html`
                <div class="info-item">
                  <div class="info-label">CPU</div>
                  <div class="info-value">${this.installed.cpu_percent.toFixed(1)}%</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Mémoire</div>
                  <div class="info-value">${this._formatMemory(this.installed.memory_usage)}</div>
                </div>
              `
            : ""}
        </div>
      </div>
    `;
  }

  private _renderInstall() {
    const hasPorts = (this.app?.ports?.length || 0) > 0;
    const hasEnv = (this.app?.environment?.length || 0) > 0;
    const hasRequirements = this.app?.requirements?.min_memory || this.app?.requirements?.gpu !== "none";
    const requiredEnvCount = this.app?.environment?.filter((e) => e.required).length || 0;

    if (!hasPorts && !hasEnv) {
      return html`
        <div class="section">
          <p style="color: var(--secondary-text-color)">
            Cette application utilise la configuration par défaut.
          </p>
        </div>
      `;
    }

    return html`
      ${requiredEnvCount > 0
        ? html`
            <div class="required-notice">
              <ha-icon icon="mdi:alert-circle"></ha-icon>
              <span>${requiredEnvCount} champ(s) requis pour l'installation</span>
            </div>
          `
        : ""}

      ${requiredEnvCount > 0
        ? html`
            <div class="section">
              <div class="section-title">Configuration</div>
              ${this.app!.environment!.filter((env) => env.required).map(
                (env) => html`
                  <div class="field">
                    <label class="field-label">
                      ${env.description || env.name}
                    </label>
                    <ha-textfield
                      .type=${env.secret ? "password" : "text"}
                      .value=${String(this._config[`env_${env.name}`] ?? env.default ?? "")}
                      required
                      @input=${(e: Event) =>
                        this._updateConfig(`env_${env.name}`, (e.target as HTMLInputElement).value)}
                    ></ha-textfield>
                  </div>
                `
              )}
            </div>
          `
        : ""}

      ${hasPorts
        ? html`
            <div class="section">
              <div class="section-title">Ports</div>
              ${this.app!.ports!.map(
                (port) => html`
                  <div class="field">
                    <label class="field-label">${port.description || `Port ${port.container}`}</label>
                    <ha-textfield
                      type="number"
                      .value=${String(this._config[`port_${port.container}`] || port.host)}
                      @input=${(e: Event) =>
                        this._updateConfig(`port_${port.container}`, (e.target as HTMLInputElement).value)}
                    ></ha-textfield>
                    <span class="field-hint">Port conteneur: ${port.container}/${port.protocol}</span>
                  </div>
                `
              )}
            </div>
          `
        : ""}

      ${hasRequirements
        ? html`
            <div class="section">
              <div class="section-title">Prérequis</div>
              <div class="requirements-grid">
                ${this.app!.requirements!.min_memory
                  ? html`
                      <div class="requirement">
                        <ha-icon icon="mdi:memory"></ha-icon>
                        Min ${this.app!.requirements!.min_memory} MB RAM
                      </div>
                    `
                  : ""}
                ${this.app!.requirements!.gpu !== "none"
                  ? html`
                      <div class="requirement">
                        <ha-icon icon="mdi:expansion-card"></ha-icon>
                        GPU ${this.app!.requirements!.gpu === "required" ? "requis" : "optionnel"}
                      </div>
                    `
                  : ""}
              </div>
            </div>
          `
        : ""}
    `;
  }

  private _renderActions() {
    if (this.installed) {
      const isRunning = this.installed.state === "running";
      return html`
        <div class="actions">
          <ha-button @click=${this._handleClose}>Fermer</ha-button>
          ${isRunning
            ? html`
                <ha-button @click=${this._handleStop}>Arrêter</ha-button>
                <ha-button @click=${this._handleRestart}>Redémarrer</ha-button>
              `
            : html`<ha-button unelevated @click=${this._handleStart}>Démarrer</ha-button>`}
          <ha-button class="danger-btn" @click=${this._handleRemove}>Supprimer</ha-button>
        </div>
      `;
    }

    return html`
      <div class="actions">
        <ha-button @click=${this._handleClose}>Annuler</ha-button>
        <ha-button unelevated ?disabled=${this.loading} @click=${this._handleInstall}>
          ${this.loading ? "Installation..." : "Installer"}
        </ha-button>
      </div>
    `;
  }

  private _getStatusLabel(state: string): string {
    const labels: Record<string, string> = {
      running: "En cours",
      stopped: "Arrêté",
      installing: "Installation...",
      error: "Erreur",
      not_installed: "Non installé",
    };
    return labels[state] || state;
  }

  private _formatMemory(bytes: number): string {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }

  private _updateConfig(key: string, value: string) {
    this._config = { ...this._config, [key]: value };
  }

  private _handleClose() {
    this._confirmDelete = false;
    this._activeTab = "status";
    this.dispatchEvent(new CustomEvent("dialog-close", { bubbles: true, composed: true }));
  }

  private _handleInstall() {
    this.dispatchEvent(
      new CustomEvent("app-install", {
        detail: { appId: this.app?.id, config: this._config },
        bubbles: true,
        composed: true,
      })
    );
  }

  private _handleStart() {
    this.dispatchEvent(
      new CustomEvent("app-start", {
        detail: { appId: this.app?.id },
        bubbles: true,
        composed: true,
      })
    );
  }

  private _handleStop() {
    this.dispatchEvent(
      new CustomEvent("app-stop", {
        detail: { appId: this.app?.id },
        bubbles: true,
        composed: true,
      })
    );
  }

  private _handleRestart() {
    this.dispatchEvent(
      new CustomEvent("app-restart", {
        detail: { appId: this.app?.id },
        bubbles: true,
        composed: true,
      })
    );
  }

  private _handleRemove() {
    this._confirmDelete = true;
  }

  private _confirmRemove() {
    this._confirmDelete = false;
    this.dispatchEvent(
      new CustomEvent("app-remove", {
        detail: { appId: this.app?.id },
        bubbles: true,
        composed: true,
      })
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "app-detail-dialog": AppDetailDialog;
  }
}
