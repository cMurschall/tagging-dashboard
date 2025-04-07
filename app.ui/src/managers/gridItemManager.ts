import { Observable } from "../observable";

export interface GridManagerItem<T = Record<string, any>> {
    id: string;
    x?: number;
    y?: number;
    w?: number;
    h?: number;
    noMove?: boolean;
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


    public suggestFreeSpace(width: number, height: number): { x: number; y: number } {
        if (width <= 0 || height <= 0) {
            console.warn("Warning: Width and height must be positive values.");
            return { x: 0, y: 0 };
        }

        const occupiedSpaces = this.GridManagerItems.filter(item => item.x !== undefined && item.y !== undefined && item.w !== undefined && item.h !== undefined) as Required<GridManagerItem>[];

        // If there are no existing items, the top-left corner (0, 0) is free.
        if (occupiedSpaces.length === 0) {
            return { x: 0, y: 0 };
        }

        let maxX = 0;
        let maxY = 0;
        for (const item of occupiedSpaces) {
            maxX = Math.max(maxX, (item.x || 0) + (item.w || 0));
            maxY = Math.max(maxY, (item.y || 0) + (item.h || 0));
        }

        // Determine a reasonable upper bound for the search.
        // We'll search in a grid that extends beyond the currently occupied items.
        const searchWidth = maxX + width + 1;
        const searchHeight = maxY + height + 1;


        for (let x = 0; x < searchWidth; x++) {
            for (let y = 0; y < searchHeight; y++) {
                const potentialNewItem = { x, y, w: width, h: height };
                let isOverlap = false;

                for (const occupiedItem of occupiedSpaces) {
                    if (
                        potentialNewItem.x < (occupiedItem.x || 0) + (occupiedItem.w || 0) &&
                        potentialNewItem.x + potentialNewItem.w > (occupiedItem.x || 0) &&
                        potentialNewItem.y < (occupiedItem.y || 0) + (occupiedItem.h || 0) &&
                        potentialNewItem.y + potentialNewItem.h > (occupiedItem.y || 0)
                    ) {
                        isOverlap = true;
                        break;
                    }
                }

                if (!isOverlap) {
                    return { x, y };
                }
            }
        }

        return { x: 0, y: 0 };
    }

}


const gridManager = new GridManager();

export default gridManager;