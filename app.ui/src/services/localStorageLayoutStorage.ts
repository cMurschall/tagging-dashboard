import { LayoutStorage, StoredLayoutItem } from "@/types/layout";





export class LocalStorageLayoutStorage implements LayoutStorage {
    constructor(private key: string = 'grid-layouts', private storage: Storage = localStorage) { }

    async load(): Promise<Record<string, StoredLayoutItem[]>> {
        try {
            const item = this.storage.getItem(this.key);
            return item ? JSON.parse(item) : {};
        } catch (e) {
            console.error("Failed to load layouts:", e);
            return {};
        }
    }

    async save(layouts: Record<string, StoredLayoutItem[]>): Promise<void> {
        try {
            const str = JSON.stringify(layouts);
            this.storage.setItem(this.key, str);
        } catch (e) {
            console.error("Failed to save layouts:", e);
        }
    }
}
