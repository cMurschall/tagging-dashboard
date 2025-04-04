import { Observable } from "../observable";

export interface GridManagerItem<T = Record<string, any>> {
    id: string;
    x?: number;
    y?: number;
    w?: number;
    h?: number;
    component?: string;
    title?: string;
    props?: T;
    pluginState?: Record<string, any> | undefined;
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

    public addNewItem<T extends Record<string, any>>(
        item: Omit<GridManagerItem<T>, 'props'> & { props: T }
    ): void {
        if (this.GridManagerItems.find((i) => i.id === item.id)) {
            console.error(`Error: item with id ${item.id} already exists`);
            return;
        }

        if (item.dependencies) {
            item.dependencies = (item.dependencies);
        }

        this.GridManagerItems.push(item);
        GridManager.newItemObservable.next(item);
    }

    public updateItemById<T extends Record<string, any>>(id: string, item: Partial<Omit<GridManagerItem<T>, 'props'> & { props: T }>): void {
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
            props: { ...existingItem.props, ...item.props },
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

const gridManager = new GridManager();

export default gridManager;