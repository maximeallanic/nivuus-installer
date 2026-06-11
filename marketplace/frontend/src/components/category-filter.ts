/**
 * Category Filter Component
 * HA-style filter chips
 */

import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";
import type { Category } from "../types";

@customElement("category-filter")
export class CategoryFilter extends LitElement {
  @property({ type: Array }) categories: Category[] = [];
  @property({ type: String }) selected = "all";

  static styles = css`
    :host {
      display: block;
    }

    .filter-container {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 4px 0;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }

    .filter-container::-webkit-scrollbar {
      display: none;
    }

    .filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 18px;
      background: var(--card-background-color);
      border: 1px solid var(--divider-color);
      color: var(--primary-text-color);
      font-size: 14px;
      font-weight: 400;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
      user-select: none;
    }

    .filter-chip:hover {
      background: var(--secondary-background-color);
    }

    .filter-chip.selected {
      background: var(--primary-color);
      border-color: var(--primary-color);
      color: var(--text-primary-color, #fff);
    }

    .filter-chip ha-icon {
      --mdc-icon-size: 18px;
    }

    .filter-chip.selected ha-icon {
      color: var(--text-primary-color, #fff);
    }

    .count {
      font-size: 12px;
      opacity: 0.7;
      margin-left: 2px;
    }
  `;

  render() {
    return html`
      <div class="filter-container">
        <button
          class="filter-chip ${this.selected === "all" ? "selected" : ""}"
          @click=${() => this._selectCategory("all")}
        >
          <ha-icon icon="mdi:view-grid"></ha-icon>
          Tout
        </button>

        <button
          class="filter-chip ${this.selected === "installed" ? "selected" : ""}"
          @click=${() => this._selectCategory("installed")}
        >
          <ha-icon icon="mdi:check-circle"></ha-icon>
          Installées
        </button>

        ${this.categories.map(
          (cat) => html`
            <button
              class="filter-chip ${this.selected === cat.id ? "selected" : ""}"
              @click=${() => this._selectCategory(cat.id)}
            >
              <ha-icon .icon=${cat.icon}></ha-icon>
              ${cat.name}
              <span class="count">${cat.app_count}</span>
            </button>
          `
        )}
      </div>
    `;
  }

  private _selectCategory(categoryId: string) {
    this.selected = categoryId;
    this.dispatchEvent(
      new CustomEvent("category-change", {
        detail: { category: categoryId },
        bubbles: true,
        composed: true,
      })
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "category-filter": CategoryFilter;
  }
}
