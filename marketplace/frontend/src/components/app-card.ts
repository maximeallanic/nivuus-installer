/**
 * App Card Component
 * Uses ha-card for HA-native look
 */

import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";
import type { AppSummary, InstalledApp, AppState } from "../types";

@customElement("app-card")
export class AppCard extends LitElement {
  @property({ type: Object }) app?: AppSummary;
  @property({ type: Object }) installed?: InstalledApp;

  static styles = css`
    :host {
      display: block;
    }

    ha-card {
      cursor: pointer;
      height: 100%;
      transition: box-shadow 0.2s ease-in-out;
    }

    ha-card:hover {
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
    }

    .card-content {
      padding: 16px;
    }

    .header {
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }

    .icon-container {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: var(--primary-color);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .icon-container ha-icon {
      color: white;
      --mdc-icon-size: 24px;
    }

    .info {
      flex: 1;
      min-width: 0;
    }

    .name {
      font-size: 16px;
      font-weight: 500;
      color: var(--primary-text-color);
      margin: 0 0 4px 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .version {
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .description {
      font-size: 14px;
      color: var(--secondary-text-color);
      margin: 12px 0 0 0;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--divider-color);
    }

    .status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 500;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .status-dot.running {
      background: var(--success-color, #4caf50);
    }

    .status-dot.stopped {
      background: var(--error-color, #f44336);
    }

    .status-dot.installing {
      background: var(--warning-color, #ff9800);
    }

    .status-dot.error {
      background: var(--error-color, #f44336);
    }

    .stats {
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .stat {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .stat ha-icon {
      --mdc-icon-size: 14px;
    }

    .category-badge {
      font-size: 11px;
      color: var(--secondary-text-color);
      background: var(--secondary-background-color);
      padding: 4px 8px;
      border-radius: 4px;
      text-transform: capitalize;
    }
  `;

  render() {
    if (!this.app && !this.installed) return html``;

    const name = this.app?.name || this.installed?.name || "Unknown";
    const description = this.app?.description || "";
    const version = this.app?.version || this.installed?.version || "";
    const icon = this.app?.icon || "mdi:docker";
    const state = this.installed?.state;

    return html`
      <ha-card @click=${this._handleClick}>
        <div class="card-content">
          <div class="header">
            <div class="icon-container">
              <ha-icon .icon=${icon}></ha-icon>
            </div>
            <div class="info">
              <h3 class="name">${name}</h3>
              <span class="version">v${version}</span>
            </div>
          </div>

          ${description ? html`<p class="description">${description}</p>` : ""}

          <div class="footer">
            ${state
              ? this._renderStatus(state)
              : html`<span class="category-badge">${this.app?.category || ""}</span>`}
            ${this.installed && state === "running" ? this._renderStats() : ""}
          </div>
        </div>
      </ha-card>
    `;
  }

  private _renderStatus(state: AppState) {
    const labels: Record<AppState, string> = {
      running: "En cours",
      stopped: "Arrêté",
      installing: "Installation...",
      error: "Erreur",
      not_installed: "Non installé",
    };

    return html`
      <span class="status">
        <span class="status-dot ${state}"></span>
        ${labels[state] || state}
      </span>
    `;
  }

  private _renderStats() {
    if (!this.installed) return "";

    return html`
      <div class="stats">
        <div class="stat">
          <ha-icon icon="mdi:cpu-64-bit"></ha-icon>
          ${this.installed.cpu_percent.toFixed(1)}%
        </div>
        <div class="stat">
          <ha-icon icon="mdi:memory"></ha-icon>
          ${this._formatMemory(this.installed.memory_usage)}
        </div>
      </div>
    `;
  }

  private _formatMemory(bytes: number): string {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(0)} KB`;
    }
    if (bytes < 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
    }
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }

  private _handleClick() {
    this.dispatchEvent(
      new CustomEvent("app-click", {
        detail: { app: this.app, installed: this.installed },
        bubbles: true,
        composed: true,
      })
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "app-card": AppCard;
  }
}
