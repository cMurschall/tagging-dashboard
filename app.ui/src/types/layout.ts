


export interface LayoutManagerConfig {
    storageKey?: string;
    storage?: Storage;
}

// Define a type for the simplified layout item to be stored
export interface StoredLayoutItem {
    id: string;
    x?: number;
    y?: number;
    w?: number;
    h?: number;
    component?: string;
    title?: string;
    pluginState?: Record<string, any> | undefined;
}

export interface LayoutStorage {
    load(): Promise<Record<string, StoredLayoutItem[]>>;
    save(layouts: Record<string, StoredLayoutItem[]>): Promise<void>;
}