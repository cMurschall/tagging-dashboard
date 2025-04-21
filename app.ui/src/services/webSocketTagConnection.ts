import { Tag, TagFromJSONTyped } from "../../services/restclient";
import { BaseWebSocketConnection } from "./baseWebSocketConnection";



export class WebSocketTagConnection extends BaseWebSocketConnection<Tag> {
    protected handleMessage(data: string): void {

        try {
            const jsonTag = JSON.parse(data);
            const tag = TagFromJSONTyped(jsonTag, false);
            this.data$.next(tag);
        } catch (error) {

            console.error("Error parsing tag data:", error);
        }
    }
}