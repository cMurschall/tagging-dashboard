import streamDeck, { LogLevel } from "@elgato/streamdeck";
import { InstantaneousTagger } from "./actions/instantaneous-tag";
import { StartStopTagger } from "./actions/start-stop-tag";
import { WebSocketHandler } from "./webSocketHandler"
import { Tagger } from "./tagger";



const websocketHandler = new WebSocketHandler("ws://127.0.0.1:8888/api/v1/ws/simulationTime");
const tagger = new Tagger("127.0.0.1:8888/api/v1/tag/create");


type ApplicationSettings = {
    websocketUrl: string;
    tagEndpointUrl: string;
};

streamDeck.settings.onDidReceiveGlobalSettings<ApplicationSettings>((ev) => {
    websocketHandler.setUrl(ev.settings.websocketUrl);
    tagger.setUrl(ev.settings.tagEndpointUrl);
});

// We can enable "trace" logging so that all messages between the Stream Deck, and the plugin are recorded. When storing sensitive information
streamDeck.logger.setLevel(LogLevel.INFO);

// Register the increment action.
streamDeck.actions.registerAction(new InstantaneousTagger(websocketHandler, tagger));
streamDeck.actions.registerAction(new StartStopTagger(websocketHandler, tagger));

// Finally, connect to the Stream Deck.
streamDeck.connect();
