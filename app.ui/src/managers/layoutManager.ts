import { Observable } from "../observable";
import { GridManagerItem } from "./gridItemManager";

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
    private storageKey: string;
    private storage: Storage | null;

    constructor(config: LayoutManagerConfig = {}) {
        this.storageKey = config.storageKey || 'grid-layouts';
        this.storage = config.storage || (typeof localStorage !== 'undefined' ? localStorage : null);
        this.loadFromStorage();
    }

    private saveToStorage(): void {
        if (this.storage) {
            const currentValue = this._layouts.getValue();
            if (currentValue) {
                const simplifiedLayouts: Record<string, StoredLayoutItem[]> = {};
                for (const layoutName in currentValue) {
                    simplifiedLayouts[layoutName] = currentValue[layoutName].map(item => ({
                        id: item.id,
                        x: item.x,
                        y: item.y,
                        w: item.w,
                        h: item.h,
                        component: item.component,
                        title: item.title,
                        pluginState: item.pluginState,
                    }));
                }
                console.log("Saving layouts to storage:", simplifiedLayouts); // Log the simplified structure
                this.storage.setItem(this.storageKey, JSON.stringify(simplifiedLayouts));
            }
        }
    }


    private loadFromStorage(): void {
        if (this.storage) {
            const storedLayouts = this.storage.getItem(this.storageKey);
            if (storedLayouts) {
                try {
                    const parsedLayouts: Record<string, StoredLayoutItem[]> = JSON.parse(storedLayouts);
                    this._layouts.next(parsedLayouts);
                } catch (error) {
                    console.error("Error loading layouts from storage:", error);
                    this._layouts.next({});
                }
            }
        }
    }


    public saveLayout(name: string, items: GridManagerItem<Record<string, any>>[]): void {
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
}

const layoutManager = new LayoutManager();

export default layoutManager;