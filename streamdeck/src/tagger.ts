import streamDeck from "@elgato/streamdeck";

export interface TagFields {
    timestamp_start_s: number;
    timestamp_end_s: number;
    category: string;
}


export interface TagPayload extends TagFields {
    notes: string;
}



export class Tagger {
    private apiUrl: string;

    constructor(initialUrl: string) {
        this.apiUrl = initialUrl;
    }

    setUrl(newUrl: string): void {
        if (this.apiUrl != newUrl) {
            this.apiUrl = newUrl;
        }
    }

    async postTag({ timestamp_start_s, timestamp_end_s, category, }: TagFields): Promise<boolean> {
        try {

            const payload: TagPayload = {
                timestamp_start_s,
                timestamp_end_s,
                category,
                notes: "", // Default to empty string
            };

            streamDeck.logger.info("Posting tag:", payload);
            streamDeck.logger.info("API URL:", this.apiUrl);

            const response = await fetch(this.apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const text = await response.text();
                streamDeck.logger.error(`Failed to post tag: ${response.status} ${text}`);
                return false;
            }

            streamDeck.logger.info("Tag posted successfully.");
            return true;
        } catch (error) {
            streamDeck.logger.error("Error posting tag:", error);
            return false;
        }
    }
}
