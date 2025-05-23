import streamDeck, { action, KeyUpEvent, SingletonAction, WillAppearEvent } from "@elgato/streamdeck";
import { WebSocketHandler } from "../webSocketHandler";
import { Tagger } from "../tagger";

/**
 * An example action class that displays a count that increments by one each time the button is pressed.
 */
@action({ UUID: "de.hs-harz.fahrsimulator-tagger.instantaneous" })
export class InstantaneousTagger extends SingletonAction<TaggerSettings> {


    constructor(private webSocketHandler: WebSocketHandler, private tagger: Tagger) {
        super();
    }


    override onWillAppear(ev: WillAppearEvent<TaggerSettings>): void | Promise<void> {
        // return ev.action.setTitle(`${ev.payload.settings.count ?? 0}`);
    }

    override async onKeyUp(ev: KeyUpEvent<TaggerSettings>): Promise<void> {

        const isConnected = this.webSocketHandler.isConnected();
        if (!isConnected) {
            streamDeck.logger.error("WebSocket is not connected. Cannot post tag.");
            await ev.action.showAlert();
            return;
        }

        const currentTimeStamp = this.webSocketHandler.getLatestTimestamp();
        if (currentTimeStamp) {
            const success = await this.tagger.postTag({
                timestamp_start_s: currentTimeStamp,
                timestamp_end_s: currentTimeStamp,
                category: ev.payload.settings.tagCategory ?? "",
            });

            if (success) {
                await ev.action.showOk();
            } else {
                await ev.action.showAlert();
            }
        } else {
            streamDeck.logger.error("No timestamp available. Cannot post tag.");
            await ev.action.showAlert();
        }
    }
}


type TaggerSettings = {
    tagCategory?: string;

};
