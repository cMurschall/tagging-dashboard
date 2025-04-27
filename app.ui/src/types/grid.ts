import { StoredLayoutItem } from "@/types/layout";
import { useToastController } from "bootstrap-vue-next";

export interface GridManagerItem extends StoredLayoutItem {
    dependencies?: Record<string, any> | undefined;
}



export type ShowToastFn = ReturnType<typeof useToastController>['show'];