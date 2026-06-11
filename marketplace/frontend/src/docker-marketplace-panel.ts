/**
 * Nivuus Store Panel
 * Main panel component for Home Assistant sidebar
 */

import { LitElement, html, css, PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type {
  HomeAssistant,
  AppSummary,
  InstalledApp,
  Category,
} from "./types";
import { MarketplaceApi } from "./api";

import "./components/category-filter";
import "./components/app-card";
import "./components/app-detail-dialog";

@customElement("docker-marketplace-panel")
export class DockerMarketplacePanel extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: Boolean }) narrow = false;

  @state() private _loading = true;
  @state() private _error = "";
  @state() private _categories: Category[] = [];
  @state() private _apps: AppSummary[] = [];
  @state() private _installed: InstalledApp[] = [];
  @state() private _selectedCategory = "all";
  @state() private _searchQuery = "";
  @state() private _selectedApp: AppSummary | null = null;
  @state() private _dialogOpen = false;
  @state() private _installing = false;

  private _api?: MarketplaceApi;
  private _refreshInterval?: number;

  static styles = css`
    :host {
      display: block;
      height: 100%;
      background: var(--primary-background-color);
      --app-header-background-color: var(--sidebar-background-color);
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      height: 56px;
      background: var(--app-header-background-color);
      border-bottom: 1px solid var(--divider-color);
      box-sizing: border-box;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .header-left ha-icon-button {
      color: var(--primary-text-color);
    }

    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 20px;
      font-weight: 400;
      color: var(--primary-text-color);
    }

    .header-title ha-icon {
      color: var(--primary-color);
      --mdc-icon-size: 24px;
    }

    .search-input {
      display: flex;
      align-items: center;
      background: var(--card-background-color);
      border: 1px solid var(--divider-color);
      border-radius: 28px;
      padding: 0 16px;
      height: 40px;
      width: 300px;
      box-sizing: border-box;
    }

    .search-input ha-icon {
      color: var(--secondary-text-color);
      --mdc-icon-size: 20px;
      margin-right: 8px;
    }

    .search-input input {
      flex: 1;
      border: none;
      background: transparent;
      font-size: 14px;
      color: var(--primary-text-color);
      outline: none;
    }

    .search-input input::placeholder {
      color: var(--secondary-text-color);
    }

    .content {
      padding: 16px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .stats-bar {
      display: flex;
      gap: 16px;
      margin-bottom: 16px;
    }

    .stat-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: var(--card-background-color);
      border-radius: var(--ha-card-border-radius, 12px);
      border: 1px solid var(--divider-color);
      min-width: 140px;
    }

    .stat-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      --mdc-icon-size: 20px;
    }

    .stat-icon.running {
      background: rgba(var(--rgb-green), 0.2);
      color: var(--success-color, #4caf50);
    }

    .stat-icon.installed {
      background: rgba(var(--rgb-primary-color), 0.2);
      color: var(--primary-color);
    }

    .stat-icon.available {
      background: rgba(var(--rgb-amber), 0.2);
      color: var(--warning-color, #ff9800);
    }

    .stat-info {
      display: flex;
      flex-direction: column;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 500;
      color: var(--primary-text-color);
      line-height: 1;
    }

    .stat-label {
      font-size: 12px;
      color: var(--secondary-text-color);
      margin-top: 4px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }

    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 16px;
      color: var(--secondary-text-color);
    }

    .loading-container ha-circular-progress {
      margin-bottom: 16px;
    }

    .error-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 16px;
      text-align: center;
    }

    .error-container ha-icon {
      color: var(--error-color);
      --mdc-icon-size: 48px;
      margin-bottom: 16px;
    }

    .error-container p {
      color: var(--secondary-text-color);
      margin: 0 0 16px 0;
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 16px;
      color: var(--secondary-text-color);
    }

    .empty-state ha-icon {
      --mdc-icon-size: 64px;
      opacity: 0.5;
      margin-bottom: 16px;
    }

    mwc-button {
      --mdc-theme-primary: var(--primary-color);
    }

    @media (max-width: 870px) {
      .search-input {
        width: 200px;
      }
      .stats-bar {
        flex-wrap: wrap;
      }
      .stat-card {
        flex: 1;
        min-width: 120px;
      }
    }

    @media (max-width: 600px) {
      .header {
        flex-direction: column;
        height: auto;
        padding: 12px 16px;
        gap: 12px;
      }
      .search-input {
        width: 100%;
      }
      .grid {
        grid-template-columns: 1fr;
      }
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this._refreshInterval = window.setInterval(() => {
      this._loadInstalled();
    }, 30000);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this._refreshInterval) {
      clearInterval(this._refreshInterval);
    }
  }

  protected updated(changedProps: PropertyValues) {
    if (changedProps.has("hass") && this.hass && !this._api) {
      this._api = new MarketplaceApi(this.hass);
      this._loadData();
    }
  }

  private async _loadData() {
    this._loading = true;
    this._error = "";

    try {
      const [catalog, installed] = await Promise.all([
        this._api!.getCatalog(),
        this._api!.getInstalled(),
      ]);

      this._categories = catalog.categories;
      this._apps = catalog.apps;
      this._installed = installed.apps;
    } catch (err) {
      console.error("Failed to load marketplace data:", err);
      this._error = "Impossible de charger le catalogue. Vérifiez que l'intégration est configurée.";
    } finally {
      this._loading = false;
    }
  }

  private async _loadInstalled() {
    if (!this._api) return;

    try {
      const installed = await this._api.getInstalled();
      this._installed = installed.apps;
    } catch (err) {
      console.error("Failed to refresh installed apps:", err);
    }
  }

  render() {
    return html`
      ${this._renderHeader()}

      <div class="content">
        ${this._loading
          ? this._renderLoading()
          : this._error
          ? this._renderError()
          : this._renderMain()}
      </div>

      <app-detail-dialog
        .hass=${this.hass}
        .app=${this._selectedApp}
        .installed=${this._getInstalledApp(this._selectedApp?.id)}
        ?open=${this._dialogOpen}
        ?loading=${this._installing}
        @dialog-close=${this._handleDialogClose}
        @app-install=${this._handleAppInstall}
        @app-start=${this._handleAppStart}
        @app-stop=${this._handleAppStop}
        @app-restart=${this._handleAppRestart}
        @app-update=${this._handleAppUpdate}
        @app-remove=${this._handleAppRemove}
      ></app-detail-dialog>
    `;
  }

  private _renderHeader() {
    return html`
      <div class="header">
        <div class="header-left">
          ${this.narrow
            ? html`
                <ha-icon-button
                  .label=${"Menu"}
                  .path=${"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"}
                  @click=${this._toggleSidebar}
                ></ha-icon-button>
              `
            : ""}
          <div class="header-title">
            <ha-icon icon="mdi:store"></ha-icon>
            <span>Nivuus Store</span>
          </div>
        </div>

        <div class="search-input">
          <ha-icon icon="mdi:magnify"></ha-icon>
          <input
            type="text"
            placeholder="Rechercher..."
            .value=${this._searchQuery}
            @input=${this._handleSearch}
          />
        </div>
      </div>
    `;
  }

  private _toggleSidebar() {
    this.dispatchEvent(
      new CustomEvent("hass-toggle-menu", {
        bubbles: true,
        composed: true,
      })
    );
  }

  private _renderLoading() {
    return html`
      <div class="loading-container">
        <ha-circular-progress indeterminate></ha-circular-progress>
        <span>Chargement du catalogue...</span>
      </div>
    `;
  }

  private _renderError() {
    return html`
      <div class="error-container">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <p>${this._error}</p>
        <mwc-button raised @click=${this._loadData}>
          Réessayer
        </mwc-button>
      </div>
    `;
  }

  private _renderMain() {
    return html`
      ${this._renderStats()}

      <category-filter
        .categories=${this._categories}
        .selected=${this._selectedCategory}
        @category-change=${this._handleCategoryChange}
      ></category-filter>

      ${this._renderGrid()}
    `;
  }

  private _renderStats() {
    const runningCount = this._installed.filter((a) => a.state === "running").length;
    const totalInstalled = this._installed.length;
    const availableApps = this._apps.length;

    return html`
      <div class="stats-bar">
        <div class="stat-card">
          <div class="stat-icon running">
            <ha-icon icon="mdi:play-circle"></ha-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${runningCount}</span>
            <span class="stat-label">En cours</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon installed">
            <ha-icon icon="mdi:check-circle"></ha-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${totalInstalled}</span>
            <span class="stat-label">Installées</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon available">
            <ha-icon icon="mdi:package-variant"></ha-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${availableApps}</span>
            <span class="stat-label">Disponibles</span>
          </div>
        </div>
      </div>
    `;
  }

  private _renderGrid() {
    const filteredApps = this._getFilteredApps();

    if (filteredApps.length === 0) {
      return html`
        <div class="empty-state">
          <ha-icon icon="mdi:package-variant-closed"></ha-icon>
          <span>Aucune application trouvée</span>
        </div>
      `;
    }

    return html`
      <div class="grid">
        ${filteredApps.map(
          (app) => html`
            <app-card
              .app=${app}
              .installed=${this._getInstalledApp(app.id)}
              @app-click=${() => this._handleAppClick(app)}
            ></app-card>
          `
        )}
      </div>
    `;
  }

  private _getFilteredApps(): AppSummary[] {
    let apps = [...this._apps];

    if (this._selectedCategory === "installed") {
      const installedIds = new Set(this._installed.map((i) => i.id));
      apps = apps.filter((app) => installedIds.has(app.id));
    } else if (this._selectedCategory !== "all") {
      apps = apps.filter((app) => app.category === this._selectedCategory);
    }

    if (this._searchQuery) {
      const query = this._searchQuery.toLowerCase();
      apps = apps.filter(
        (app) =>
          app.name.toLowerCase().includes(query) ||
          app.description.toLowerCase().includes(query) ||
          app.tags.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    return apps;
  }

  private _getInstalledApp(appId?: string): InstalledApp | undefined {
    if (!appId) return undefined;
    return this._installed.find((i) => i.id === appId);
  }

  private _handleSearch(e: Event) {
    this._searchQuery = (e.target as HTMLInputElement).value;
  }

  private _handleCategoryChange(e: CustomEvent) {
    this._selectedCategory = e.detail.category;
  }

  private _handleAppClick(app: AppSummary) {
    this._selectedApp = app;
    this._dialogOpen = true;
  }

  private _handleDialogClose() {
    this._dialogOpen = false;
    this._selectedApp = null;
  }

  private async _handleAppInstall(e: CustomEvent) {
    const { appId, config } = e.detail;
    if (!this._api || !appId) return;

    this._installing = true;
    try {
      await this._api.installApp(appId, config);
      this._handleDialogClose();
      await this._loadInstalled();
    } catch (err) {
      console.error("Failed to install app:", err);
    } finally {
      this._installing = false;
    }
  }

  private async _handleAppStart(e: CustomEvent) {
    const { appId } = e.detail;
    if (!this._api || !appId) return;

    try {
      await this._api.startApp(appId);
      await this._loadInstalled();
    } catch (err) {
      console.error("Failed to start app:", err);
    }
  }

  private async _handleAppStop(e: CustomEvent) {
    const { appId } = e.detail;
    if (!this._api || !appId) return;

    try {
      await this._api.stopApp(appId);
      await this._loadInstalled();
    } catch (err) {
      console.error("Failed to stop app:", err);
    }
  }

  private async _handleAppRestart(e: CustomEvent) {
    const { appId } = e.detail;
    if (!this._api || !appId) return;

    try {
      await this._api.restartApp(appId);
      await this._loadInstalled();
    } catch (err) {
      console.error("Failed to restart app:", err);
    }
  }

  private async _handleAppUpdate(e: CustomEvent) {
    const { appId } = e.detail;
    if (!this._api || !appId) return;

    try {
      await this._api.updateApp(appId);
      await this._loadInstalled();
    } catch (err) {
      console.error("Failed to update app:", err);
    }
  }

  private async _handleAppRemove(e: CustomEvent) {
    const { appId } = e.detail;
    if (!this._api || !appId) return;

    try {
      await this._api.removeApp(appId);
      this._handleDialogClose();
      await this._loadInstalled();
    } catch (err) {
      console.error("Failed to remove app:", err);
    }
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "docker-marketplace-panel": DockerMarketplacePanel;
  }
}
