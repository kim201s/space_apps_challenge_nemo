
import { API_BASE_URL } from "./config.js";

export async function fetchFires(date, bbox, signal) {
    const url = new URL("/fires", API_BASE_URL);

    const params = {
        min_lon: bbox.minLon,
        min_lat: bbox.minLat,
        max_lon: bbox.maxLon,
        max_lat: bbox.maxLat,
        date: date
    };

    url.search = new URLSearchParams(params).toString();

    const response = await fetch(url, { signal });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    if (!Array.isArray(data.fires)) {
        throw new Error("Unexpected API response format");
    }

    return data.fires;
}

export async function fetchFireStats(from, to, bbox, interval) {
    const url = new URL("/fire_stats", API_BASE_URL);

    const params = {
        min_lon: bbox.minLon,
        min_lat: bbox.minLat,
        max_lon: bbox.maxLon,
        max_lat: bbox.maxLat,
        min_date: from,
        max_date: to,
        interval: interval
    };

    url.search = new URLSearchParams(params).toString();

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    if (!Array.isArray(data.statistics)) {
        throw new Error("Unexpected statistics response");
    }

    return data.statistics;
}