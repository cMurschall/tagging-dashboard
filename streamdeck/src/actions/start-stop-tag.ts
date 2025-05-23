import streamDeck, { action, KeyUpEvent, SingletonAction, WillAppearEvent } from "@elgato/streamdeck";
import { WebSocketHandler } from "../webSocketHandler";
import { Tagger } from "../tagger";


type ButtonState = "Stop" | "Recording";

/**
 * An example action class that displays a count that increments by one each time the button is pressed.
 */
@action({ UUID: "de.hs-harz.fahrsimulator-tagger.start-stop" })
export class StartStopTagger extends SingletonAction<TaggerSettings> {

    private buttonState: ButtonState = "Stop";

    private startTime: number | null = null;
    private endTime: number | null = null;

    constructor(private webSocketHandler: WebSocketHandler, private tagger: Tagger) {
        super();
    }


    override onWillAppear(ev: WillAppearEvent<TaggerSettings>): void | Promise<void> {
        // return ev.action.setTitle(`${ev.payload.settings.count ?? 0}`);
    }

    override async onKeyUp(ev: KeyUpEvent<TaggerSettings>): Promise<void> {

        const stateIndex = ev.payload.state
        this.buttonState = stateIndex === 0 ? "Stop" : "Recording";

        if (this.buttonState === "Stop") {
            this.startTime = this.webSocketHandler.getLatestTimestamp();
            //   await ev.action.setTitle("Recording...");
        }
        if (this.buttonState === "Recording") {
            const isConnected = this.webSocketHandler.isConnected();
            if (!isConnected) {
                streamDeck.logger.error("WebSocket is not connected. Cannot post tag.");
                await ev.action.showAlert();
                return;
            }

            this.endTime = this.webSocketHandler.getLatestTimestamp();

            const hasTimeRange = this.startTime !== null && this.endTime !== null;
            if (hasTimeRange) {
                const success = await this.tagger.postTag({
                    timestamp_start_s: this.startTime!,
                    timestamp_end_s: this.endTime!,
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
            this.startTime = null;
            this.endTime = null;
        }
    }
}


type TaggerSettings = {
    tagCategory?: string;
};
