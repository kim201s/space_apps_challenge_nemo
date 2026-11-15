
import {
    MAX_VIEW_LAT_SPAN,
    MAX_VIEW_LON_SPAN
} from "./config.js";

export function createGlobe() {
    Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IlZxVS1SUTlldUFXbVg5azYiLCJqdGkiOiIwZDdhYzc4Ni1mMjkxLTQyZDctOWRmYi1mNDA1Y2RlMWVkZDgiLCJpZCI6NTUwMTExLCJzdWIiOiJyYW5kb21fZ3V5XzExMSIsImlzcyI6Imh0dHBzOi8vYXBpLmNlc2l1bS5jb20iLCJhdWQiOiJ0aXRsZWQiLCJpYXQiOjE3OTQ3NjI3MTJ9._0w_zSYMPI6CYWdM4d9T-ltwn--0lRbCXgC0YVoXxo4";

    const viewer = new Cesium.Viewer("cesiumContainer", {
        terrain: Cesium.Terrain.fromWorldTerrain(),
        animation: false,
        timeline: false,
        geocoder: false,
        sceneModePicker: false,
        homeButton: false,
        baseLayerPicker: false, 
         navigationHelpButton: false,
    });

    const fireLayer = new Cesium.CustomDataSource("hotspots");

    viewer.dataSources.add(fireLayer);

    return { viewer, fireLayer };
}


function normalizeLongitude(lon) {
    return ((lon + 180) % 360 + 360) % 360 - 180;
}


export function getVisibleBboxes(viewer) {
    const rectangle = viewer.camera.computeViewRectangle(
        viewer.scene.globe.ellipsoid
    );

    if (!rectangle) {
        return { boxes: [], reason: "no-visible-region" };
    }

    const minLat = Cesium.Math.toDegrees(rectangle.south);
    const maxLat = Cesium.Math.toDegrees(rectangle.north);

    let spanRad = rectangle.east - rectangle.west;

    if (spanRad <= 0) {
        spanRad += 2 * Math.PI;
    }

    const lonSpan = Cesium.Math.toDegrees(spanRad);
    const west = normalizeLongitude(
        Cesium.Math.toDegrees(rectangle.west)
    );

    const east = west + lonSpan;

    if (
        maxLat - minLat > MAX_VIEW_LAT_SPAN ||
        lonSpan > MAX_VIEW_LON_SPAN
    ) {
        return { boxes: [], reason: "zoom-in" };
    }

    const boxes = [];

    if (east <= 180) {
        boxes.push({
            minLon: west,
            maxLon: east,
            minLat,
            maxLat
        });
    } else {

        boxes.push({
            minLon: west,
            maxLon: 180,
            minLat,
            maxLat
        });

        boxes.push({
            minLon: -180,
            maxLon: east - 360,
            minLat,
            maxLat
        });
    }

    return { boxes, reason: null };
}

export function renderFires(fireLayer, fires) {
    fireLayer.entities.removeAll();

    for (const fire of fires) {
        const frp = Number(fire.frp ?? 0);

        let color = Cesium.Color.YELLOW;

        if (frp >= 100) {
            color = Cesium.Color.RED;
        } else if (frp >= 30) {
            color = Cesium.Color.ORANGE;
        }

        fireLayer.entities.add({
            id: `fire-${fire.id}`,

            position: Cesium.Cartesian3.fromDegrees(
                fire.longitude,
                fire.latitude,
                100
            ),

            point: {
                pixelSize: frp >= 100 ? 10 : 7,
                color,
                outlineColor: Cesium.Color.WHITE,
                outlineWidth: 1
            },

            description: `
                <b>FRP:</b> ${fire.frp} MW<br>
                <b>Instrument:</b> ${fire.instrument}<br>
                <b>Date:</b> ${fire.acq_date}<br>
                <b>Confidence:</b> ${fire.confidence}
            `
        });
    }
}
