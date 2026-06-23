import { items, natures } from "../data/demo-fixtures";
import { serviceResult, type Item, type Nature, type ServiceResult } from "../types/domain";

export type CatalogService = {
  listNatures(): Promise<ServiceResult<Nature[]>>;
  listItems(query?: string): Promise<ServiceResult<Item[]>>;
};

export const catalogService: CatalogService = {
  async listNatures() {
    return serviceResult(natures);
  },

  async listItems(query = "") {
    const normalized = query.trim().toLowerCase();
    return serviceResult(items.filter((item) => !normalized || item.name.toLowerCase().includes(normalized)));
  }
};
