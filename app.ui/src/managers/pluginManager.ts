
import { EmptySubscription, Observable, Subscription } from "../observable";
import { TestDriveProjectInfo, WebSocketBasePath } from "../services/utilities";
import { DataManager, EmptyDataManager } from "./dataManager";
import gridManager, { GridManager, GridManagerItem } from './gridItemManager';

import VideoPlayer from './../components/plugins/VideoPlayer.vue';
import ListView from './../components/plugins/ListView.vue';
import Gauge from './../components/plugins/Gauge.vue';
import ScatterPlot from './../components/plugins/ScatterPlot.vue';
import TestGridItem from './../components/plugins/TestGridItem.vue';
import TagTimeline from './../components/plugins/TagTimeline.vue';
import { ApiDataManager } from "./apiDataManager";
import { ShowToastFn } from "../plugins/AppPlugins";
import { WebSocketDataConnection } from "../services/webSocketDataConnection";
import { WebsocketDataManager } from "./websocketDataManager";


export interface PluginServices {
    simulationTime: Observable<number>;
    getProjectInfo: () => TestDriveProjectInfo | undefined;
    getDataManager: () => DataManager,
    showToast: ShowToastFn;
}

export type PluginType = 'ListView' | 'VideoPlayer' | 'Gauge' | 'ScatterPlot' | 'TestGridItem' | 'TagTimeline';



export class PluginManager {

    private showToast: ShowToastFn = () => '';

    private webSocketDataConnection: WebSocketDataConnection;

    private gridItemManager: GridManager;

    public readonly simulationTimeObservable = new Observable<number>(0);

    private pluginSizes = {
        ListView: { w: 3, h: 5 },
        VideoPlayer: { w: 6, h: 7 },
        Gauge: { w: 3, h: 5 },
        ScatterPlot: { w: 7, h: 4 },
        TestGridItem: { w: 5, h: 4 },
        TagTimeline: { w: 6, h: 7 },
    } as Record<PluginType, { w: number; h: number }>;

    private dataManagers = {
        ListView: new EmptyDataManager(),
        VideoPlayer: new EmptyDataManager(),
        Gauge: new EmptyDataManager(),
        ScatterPlot: new EmptyDataManager(),
        TestGridItem: new EmptyDataManager(),
        TagTimeline: new EmptyDataManager(),
    } as Record<PluginType, EmptyDataManager>;


    private loadedProject: TestDriveProjectInfo | undefined = undefined;
    private websocketClockSubscription: Subscription = EmptySubscription


    // constructor
    public constructor(gridItemManager: GridManager) {
        this.gridItemManager = gridItemManager;

        this.registerComponents();

        this.webSocketDataConnection = new WebSocketDataConnection(WebSocketBasePath + '/data');
    }





    public setShowToast(showToast: ShowToastFn) {
        this.showToast = showToast;
    }

    public setCurrentProject(project: TestDriveProjectInfo | undefined): void {
        if (!project) {
            // all data managers back to empty
            for (const key in this.dataManagers) {
                this.dataManagers[key as PluginType] = new EmptyDataManager();
            }
        }

        this.websocketClockSubscription.unsubscribe();

        // for now we only support the api data manager

        if (project?.isLive) {
            this.websocketClockSubscription = this.webSocketDataConnection.data$.subscribe((data) => {
                this.simulationTimeObservable.next(data.timestamp);
            });
            for (const key in this.dataManagers) {
                const dataManager = new WebsocketDataManager(this.webSocketDataConnection)
                dataManager.subscribeToTimestamp(this.simulationTimeObservable);
                this.dataManagers[key as PluginType] = dataManager;
            }
        }
        else {
            for (const key in this.dataManagers) {
                const dataManager = new ApiDataManager();
                dataManager.subscribeToTimestamp(this.simulationTimeObservable);
                this.dataManagers[key as PluginType] = dataManager;
            }
        }



        this.loadedProject = project;
    }




    public restorePlugin(plugin: GridManagerItem): void {

        const service = this.getCurrentService(plugin.component as PluginType);
        // preserve and merge the dependencies
        plugin.dependencies = {
            ...plugin.dependencies,
            pluginService: service
        };

        this.gridItemManager.addNewItem(plugin);
    }


    public showPlugin(pluginName: PluginType, props: Record<string, any>): void {

        const service = this.getCurrentService(pluginName);

        const newItem = {
            id: pluginName + '_' + crypto.randomUUID(),
            // spread x and y from the gridItemManager
            ...this.gridItemManager.suggestFreeSpace(this.pluginSizes[pluginName].w, this.pluginSizes[pluginName].h),
            w: this.pluginSizes[pluginName].w,
            h: this.pluginSizes[pluginName].h,
            component: pluginName,
            title: pluginName,
            props: props,
            dependencies: {
                pluginService: service
            }
        };

        switch (pluginName) {
            case 'VideoPlayer':
                // only one video player is allowed
                newItem.id = 'VideoPlayer';
                break;
            case 'TagTimeline':
                // only one tag timeline is allowed
                newItem.id = 'TagTimeline';
                break;
            default:
                break;

        }

        this.gridItemManager.addNewItem(newItem);
    }



    private registerComponents() {
        this.gridItemManager.setComponentMap({
            ListView: () => (ListView),
            VideoPlayer: () => (VideoPlayer),
            Gauge: () => (Gauge),
            ScatterPlot: () => (ScatterPlot),
            TestGridItem: () => (TestGridItem),
            TagTimeline: () => (TagTimeline),
        });
    }


    private getCurrentService(pluginType: PluginType): PluginServices {
        return {
            simulationTime: this.simulationTimeObservable,
            getProjectInfo: () => this.loadedProject,
            getDataManager: () => this.dataManagers[pluginType],
            showToast: this.showToast,
        };
    }


}


const pluginManager = new PluginManager(gridManager);
// Export a function to get the singleton instance
export default pluginManager;