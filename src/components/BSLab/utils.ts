import { type BSLabSettings, DEFAULT_SETTINGS } from './types';

export function settingsToParams(settings: BSLabSettings): URLSearchParams {
    const p = new URLSearchParams();
    p.set('tickers', settings.tickers.join(','));

    // Compact encoded params? Or explicit?
    // Explicit is readable but long.
    // Using JSON for complex objects is easier but ugly URL.
    // Prompt asks for "Copy shareable link".
    // Let's use a compressed JSON string for the complex parts or just individual fields?
    // Individual fields are better for partial updates but tedious.
    // Let's use JSON param 's' for settings to be robust.
    // But strictly, "support sharing via URL query params" implies readability? 
    // "Input exactly 3 tickers... Tweak all settings".
    // I'll stick to a json parameter `data` which is base64 encoded or just plain URI encoded json.

    const json = JSON.stringify(settings);
    p.set('data', btoa(json)); // Base64 to avoid encoding mess
    return p;
}

export function paramsToSettings(p: URLSearchParams): BSLabSettings {
    const data = p.get('data');
    if (data) {
        try {
            const json = atob(data);
            const parsed = JSON.parse(json);
            return { ...DEFAULT_SETTINGS, ...parsed }; // Merge to ensure new fields if any
        } catch (e) {
            console.error("Failed to parse settings from URL", e);
        }
    }
    return DEFAULT_SETTINGS;
}

export function saveToLocal(settings: BSLabSettings) {
    if (settings.persistence.autosave) {
        localStorage.setItem('bs_lab_settings', JSON.stringify(settings));
    }
}

export function loadFromLocal(): BSLabSettings | null {
    const s = localStorage.getItem('bs_lab_settings');
    if (s) {
        try {
            return JSON.parse(s);
        } catch (e) {
            return null;
        }
    }
    return null;
}
