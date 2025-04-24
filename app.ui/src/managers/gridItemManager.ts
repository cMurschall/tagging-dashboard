import { Observable } from "../observable";
import { StoredLayoutItem } from "./layoutManager";

export interface GridManagerItem extends StoredLayoutItem {
    dependencies?: Record<string, any> | undefined;
}

export class GridManager {
    private GridManagerItems: GridManagerItem[] = [];
    private componentMap: Record<string, () => any> = {};

    public static newItemObservable = new Observable<GridManagerItem>();
    public static removeItemObservable = new Observable<string>();

    public getGridItems(): GridManagerItem[] {
        return this.GridManagerItems;
    }

    public getComponentMap(): Record<string, () => any> {
        return this.componentMap;
    }

    public setComponentMap(map: Record<string, () => any>): void {
        this.componentMap = map;
    }

    public registerComponent(key: string, componentFactory: () => any): void {
        if (this.componentMap[key]) {
            console.warn(`Warning: Component with key "${key}" is already registered.`);
        }
        this.componentMap[key] = componentFactory;
    }

    public addNewItem(item: GridManagerItem): void {
        if (this.GridManagerItems.find((i) => i.id === item.id)) {
            console.error(`Error: item with id ${item.id} already exists`);
            return;
        }

        this.GridManagerItems.push(item);
        GridManager.newItemObservable.next(item);
    }

    public updateItemById(id: string, item: Partial<GridManagerItem>): void {
        const index = this.GridManagerItems.findIndex((i) => i.id === id);
        if (index === -1) {
            console.error(`Error: item with id ${id} does not exist`);
            return;
        }
        const existingItem = this.GridManagerItems[index];

        // Merge the existing item with the new properties
        this.GridManagerItems[index] = {
            ...existingItem,
            ...item,
        };
    }

    public getItemById(id: string): GridManagerItem | undefined {
        return this.GridManagerItems.find((item) => item.id === id);
    }

    public removeItemById(id: string): void {
        const index = this.GridManagerItems.findIndex((i) => i.id === id);
        if (index === -1) {
            console.error(`Error: item with id ${id} does not exist`);
            return;
        }

        const removedItem = this.GridManagerItems.splice(index, 1)[0];
        GridManager.removeItemObservable.next(removedItem.id);
    }

    public removeAllItems(): void {
        const items = [...this.GridManagerItems];
        this.GridManagerItems = [];
        items.forEach((item) => GridManager.removeItemObservable.next(item.id));
    }

}

let instance: GridManager | undefined;

export const getGridManager = (): GridManager => {
    if (!instance) {
        instance = new GridManager();
    }
    return instance;
}
