
import { EmptySubscription, Observable, Subscription } from "../observable";
import { TestDriveProjectInfo, WebSocketBasePath } from "../services/utilities";
import { DataManager, EmptyDataManager } from "./dataManager";
import { getGridManager, GridManager, GridManagerItem } from './gridItemManager';

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
import { WebSocketSimulationTimeConnection } from "../services/webSocketSimulationTimeConnection";
import LiveScatterPlot from "../components/plugins/LiveScatterPlot.vue";


export interface PluginServices {
    simulationTime: Observable<number>;
    getProjectInfo: () => TestDriveProjectInfo | undefined;
    getDataManager: () => DataManager,
    showToast: ShowToastFn;
    savePluginState: (id: string, state: Record<string, any>) => void;
}

export type PluginType = 'ListView' | 'VideoPlayer' | 'Gauge' | 'ScatterPlot' | 'TestGridItem' | 'TagTimeline';



export class PluginManager {

    private showToast: ShowToastFn = () => '';

    private webSocketDataConnection: WebSocketDataConnection;
    private webSocketSimulationTimeConnection: WebSocketSimulationTimeConnection;

    private gridItemManager: GridManager;

    public readonly simulationTimeObservable = new Observable<number>(0);

    private timeStampSubscription: Subscription =  EmptySubscription

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

    // subscriptions and unsubscriptions:  todo



    // constructor
    public constructor(gridItemManager: GridManager) {
        this.gridItemManager = gridItemManager;

        this.webSocketDataConnection = new WebSocketDataConnection(WebSocketBasePath + '/data');
        this.webSocketSimulationTimeConnection = new WebSocketSimulationTimeConnection(WebSocketBasePath + '/simulationTime');
    }





    public setShowToast(showToast: ShowToastFn) {
        this.showToast = showToast;
    }

    public setCurrentProject(project: TestDriveProjectInfo | undefined): void {

        this.timeStampSubscription?.unsubscribe();

        if (!project) {
            // all data managers back to empty
            for (const key in this.dataManagers) {
                this.dataManagers[key as PluginType] = new EmptyDataManager();
            }
            this.loadedProject = undefined;

            // clear all plugins
            this.gridItemManager.removeAllItems();
            return;
        }

        this.registerComponents(project);

        const isLiveProject = project?.isLive
        if (isLiveProject) {
            // unsubscribe from old data connection todo!!
            this.timeStampSubscription = this.webSocketDataConnection.data$.subscribe((data) => {
                // in a live project we have to set the internal simulation clock  to the current time
                // every time we receive a new data point
                this.simulationTimeObservable.next(data.timestamp);
            });
            for (const key in this.dataManagers) {
                const dataManager = new WebsocketDataManager(this.webSocketDataConnection)
                dataManager.subscribeToTimestamp(this.simulationTimeObservable);
                this.dataManagers[key as PluginType] = dataManager;
            }
        }
        else {
            this.timeStampSubscription =   this.simulationTimeObservable.subscribe((time) => {
                // if we have a non live project we can set the time to an arbitrary value.
                // so we need to inform the simulation time connection about the current time
                this.webSocketSimulationTimeConnection.sendCurrentTimeStamp(time);
            });

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



    private registerComponents(project: TestDriveProjectInfo) {
        this.gridItemManager.setComponentMap({
            ListView: () => (ListView),
            VideoPlayer: () => (VideoPlayer),
            Gauge: () => (Gauge),
            ScatterPlot: () => project.isLive ? (LiveScatterPlot) :  (ScatterPlot) ,
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
            savePluginState: (id: string, state: Record<string, any>) => {
                const item = this.gridItemManager.getGridItems().find(i => i.id === id);
                if (!item) {
                    console.warn(`Plugin state update failed: no item found with id '${id}'`);
                    return;
                }

                this.gridItemManager.updateItemById(id, {
                    pluginState: { ...state },
                });
            }
        };
    }
}


// Export a function to get the singleton instance
let instance: PluginManager | undefined;

export const getPluginManager = (): PluginManager => {
    if (!instance) {
        instance = new PluginManager(getGridManager());
    }
    return instance;
}