
import { EmptySubscription, Observable, Subscription } from "../observable";
import { isNotNullOrUndefined, isNullOrUndefined, ShowToastFn, TestDriveProjectInfo, WebSocketBasePath } from "../services/utilities";
import { DataManager } from "./dataManager";
import { getGridManager, GridManager, GridManagerItem } from './gridItemManager';

import VideoPlayer from './../components/plugins/VideoPlayer.vue';
import ListView from './../components/plugins/ListView.vue';
import Gauge from './../components/plugins/Gauge.vue';
import ScatterPlot from './../components/plugins/ScatterPlot.vue';
import TestGridItem from './../components/plugins/TestGridItem.vue';
import TagTimeline from './../components/plugins/TagTimeline.vue';
import LiveScatterPlot from "../components/plugins/LiveScatterPlot.vue";
import VectorComponentsChart from "../components/plugins/VectorComponentsChart.vue";


import { ApiDataManager } from "./apiDataManager";
import { WebSocketDataConnection } from "../services/webSocketDataConnection";
import { WebsocketDataManager } from "./websocketDataManager";
import { WebSocketSimulationTimeConnection } from "../services/webSocketSimulationTimeConnection";


import { isProxy, toRaw } from "vue";

import { VideoControl } from "./videoControl";



export interface Plugin {
    // The render function receives a container HTMLElement and the PluginService.
    render: (container: HTMLElement, pluginService: PluginServices) => void;

    // Optional lifecycle hooks for additional setup/cleanup.
    onMounted?: () => void;
    onUnmounted?: () => void;
  }


export interface PluginServices {
    getId: () => string;

    showMenu$ : Observable<boolean>;
    cardTitle$ : Observable<string>;

    simulationTime: Observable<number>;
    getProjectInfo: () => TestDriveProjectInfo | undefined;
    getDataManager: () => DataManager,
    showToast: ShowToastFn;
    savePluginState: ( state: Record<string, any>) => void;
    getPluginState: () => Record<string, any> | undefined;
    getVideoControl : () => VideoControl;

}

export type PluginType = 'ListView' | 'VideoPlayer' | 'Gauge' | 'ScatterPlot' | 'TestGridItem' | 'TagTimeline' | 'VectorComponents';



export class PluginManager {

    private showToast: ShowToastFn = () => '';

    private webSocketDataConnection: WebSocketDataConnection;
    private webSocketSimulationTimeConnection: WebSocketSimulationTimeConnection;

    private gridItemManager: GridManager;

    public readonly simulationTimeObservable = new Observable<number>(0);

    private timeStampSubscription: Subscription = EmptySubscription

    private readonly videoControl = new VideoControl()

    private pluginSizes = {
        ListView: { w: 3, h: 5 },
        VideoPlayer: { w: 6, h: 7 },
        Gauge: { w: 3, h: 5 },
        ScatterPlot: { w: 7, h: 4 },
        VectorComponents: { w: 7, h: 4 },
        TestGridItem: { w: 5, h: 4 },
        TagTimeline: { w: 6, h: 7 },
    } as Record<PluginType, { w: number; h: number }>;


    private dataManagers = new Map<string, DataManager>();

    private loadedProject: TestDriveProjectInfo | undefined = undefined;


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

        if (isNullOrUndefined(project)) {
            // all data managers back to empty
            this.dataManagers.clear();

            this.loadedProject = undefined;

            // clear all plugins
            this.gridItemManager.removeAllItems();
            return;
        }

        this.registerComponents(project);

        const isLiveProject = project.isLive
        if (isLiveProject) {
            // unsubscribe from old data connection todo!!
            this.timeStampSubscription = this.webSocketDataConnection.data$.subscribe((data) => {
                // in a live project we have to set the internal simulation clock  to the current time
                // every time we receive a new data point
                this.simulationTimeObservable.next(data.timestamp);
            });
        }
        else {
            this.timeStampSubscription = this.simulationTimeObservable.subscribe((time) => {
                // if we have a non live project we can set the time to an arbitrary value.
                // so we need to inform the simulation time connection about the current time
                this.webSocketSimulationTimeConnection.sendCurrentTimeStamp(time);
            });
        }

        this.loadedProject = project;
    }


    public restorePlugin(plugin: GridManagerItem, pluginState : Record<string, any> | undefined): void {

        const service = this.getCurrentService(plugin.id);

        if (isNotNullOrUndefined(pluginState)) {
            service.getPluginState = () => pluginState;
        }
        // preserve and merge the dependencies
        plugin.dependencies = {
            pluginService: service
        };

        this.gridItemManager.addNewItem(plugin);
    }


    public showPlugin(pluginName: PluginType, props: Record<string, any>): void {
        let id: string;
        switch (pluginName) {
            case 'VideoPlayer':
                // only one video player is allowed
                id = 'VideoPlayer';
                break;
            case 'TagTimeline':
                // only one tag timeline is allowed
                id = 'TagTimeline';
                break;
            default:
                id = pluginName + '_' + crypto.randomUUID();
                break;

        }
        const service = this.getCurrentService(id);

        const newItem = {
            id: id,
            // spread x and y from the gridItemManager (does not really work well yet)
            //...this.gridItemManager.suggestFreeSpace(this.pluginSizes[pluginName].w, this.pluginSizes[pluginName].h),
            w: this.pluginSizes[pluginName].w ,
            h: this.pluginSizes[pluginName].h  * 4,
            component: pluginName,
            title: pluginName,
            props: props,
            dependencies: {
                pluginService: service
            }
        };

        this.gridItemManager.addNewItem(newItem);
    }



    private registerComponents(project: TestDriveProjectInfo) {
        this.gridItemManager.setComponentMap({
            ListView: () => (ListView),
            VideoPlayer: () => (VideoPlayer),
            Gauge: () => (Gauge),
            ScatterPlot: () => project.isLive ? (LiveScatterPlot) : (ScatterPlot),
            TestGridItem: () => (TestGridItem),
            TagTimeline: () => (TagTimeline),
            VectorComponents: () => (VectorComponentsChart),
        });


    }


    private getCurrentService(pluginId: string): PluginServices {

        let dataManager = this.dataManagers.get(pluginId);
        if (!dataManager) {
            dataManager = this.loadedProject?.isLive
                ? new WebsocketDataManager(this.webSocketDataConnection)
                : new ApiDataManager();

            dataManager.subscribeToTimestamp(this.simulationTimeObservable);
            this.dataManagers.set(pluginId, dataManager);
        }

        const showMenu$ = new Observable<boolean>(false);
        const cardTitle$ = new Observable<string>("");


        return {
            getId: () => pluginId,

            showMenu$: showMenu$,
            cardTitle$ : cardTitle$,

            simulationTime: this.simulationTimeObservable,
            getProjectInfo: () => this.loadedProject,
            getDataManager: () => {
                if (!dataManager) throw new Error(`No dataManager found for pluginId=${pluginId}`);
                return dataManager;
            },
            showToast: this.showToast,
            savePluginState: (state: Record<string, any>) => {
                const item = this.gridItemManager.getGridItems().find(i => i.id === pluginId);
                if (!item) {
                    console.warn(`Plugin state update failed: no item found with id '${pluginId}'`);
                    return;
                }

                const rawState = isProxy(state) ? toRaw(state) : state;
                this.gridItemManager.updateItemById(pluginId, {
                    pluginState: { ...JSON.parse(JSON.stringify(rawState)) },
                });
            },
            getPluginState: () => {
                const item = this.gridItemManager.getGridItems().find(i => i.id === pluginId);
                if (!item) {
                    console.warn(`Plugin state retrieval failed: no item found with id '${pluginId}'`);
                    return undefined;
                }
                return item.pluginState;
            },
            getVideoControl: () => this.videoControl,
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