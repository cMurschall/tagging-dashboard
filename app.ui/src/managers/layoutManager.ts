import { Observable } from "../observable";
import { GridManagerItem } from "./gridItemManager";
import { LayoutStorage, LocalStorageLayoutStorage } from "./localStorageLayoutStorage";




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



export class LayoutManager {

    private _layouts = new Observable<Record<string, StoredLayoutItem[]>>({});
    private storage: LayoutStorage;

    constructor(storage: LayoutStorage) {
        this.storage = storage;
        this.loadFromStorage();
    }
    private async loadFromStorage() {
        const layouts = await this.storage.load();
        this._layouts.next(layouts);
    }

    private async saveToStorage() {
        await this.storage.save(this._layouts.getValue() ?? {});
    }




    public saveLayout(name: string, items: GridManagerItem[]): void {
        const simplifiedItems: StoredLayoutItem[] = items.map(item => ({
            id: item.id,
            x: item.x,
            y: item.y,
            w: item.w,
            h: item.h,
            component: item.component,
            title: item.title,
            pluginState: item.pluginState,
        }));
        const currentLayouts = { ...this._layouts.getValue() };
        currentLayouts[name] = simplifiedItems;
        this._layouts.next(currentLayouts);
        this.saveToStorage();
    }



    public getLayoutNames(): string[] {
        const currentValue = this._layouts.getValue();
        return currentValue ? Object.keys(currentValue) : [];
    }

    public getLayout(name: string): StoredLayoutItem[] | undefined {
        return this._layouts.getValue()?.[name];
    }

    public get layouts$(): Observable<Record<string, StoredLayoutItem[]>> {
        return this._layouts;
    }

    public removeLayout(name: string): void {
        const currentLayouts = { ...this._layouts.getValue() };
        if (currentLayouts && currentLayouts[name]) {
            delete currentLayouts[name];
            this._layouts.next(currentLayouts);
            this.saveToStorage();
        } else {
            console.error(`Error: Layout with name "${name}" not found.`);
        }
    }

    public renameLayout(oldName: string, newName: string): void {
        const currentLayouts = { ...this._layouts.getValue() };
        if (currentLayouts && currentLayouts[oldName]) {
            const layoutData = currentLayouts[oldName];
            delete currentLayouts[oldName];
            currentLayouts[newName] = layoutData;
            this._layouts.next(currentLayouts);
            this.saveToStorage();
        } else {
            console.error(`Error: Layout with name "${oldName}" not found.`);
        }
    }

    public clearAllLayouts(): void {
        this._layouts.next({});
        this.saveToStorage();
    }
}


// Export a function to get the singleton instance
let instance: LayoutManager | undefined;

export const getLayoutManager = (): LayoutManager => {
    if (!instance) {
        instance = new LayoutManager(new LocalStorageLayoutStorage('grid-layouts', localStorage));
    }
    return instance;
}