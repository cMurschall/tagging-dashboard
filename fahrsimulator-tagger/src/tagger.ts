import streamDeck from "@elgato/streamdeck";

export interface TagFields {
    timestamp_start_s: number;
    timestamp_end_s: number;
    category: string;
}

export interface TagPayload {
    tag: TagFields & {
        notes: string;
    };
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

    async postTag({ timestamp_start_s, timestamp_end_s, category, }: TagFields): Promise<void> {
        try {

            const payload: TagPayload = {
                tag: {
                    timestamp_start_s,
                    timestamp_end_s,
                    category,
                    notes: "", // Default to empty string
                },
            };

            const response = await fetch(this.apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Failed to post tag: ${response.status} ${text}`);
            }

            streamDeck.logger.info("Tag posted successfully.");
        } catch (error) {
            streamDeck.logger.error("Error posting tag:", error);
        }
    }
}
