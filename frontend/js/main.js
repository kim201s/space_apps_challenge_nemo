
import { fetchFires, fetchFireStats } from "./api.js";

import {
    createGlobe,
    getVisibleBboxes,
    renderFires
} from "./globe.js";

// =============================
// GLOBE
// =============================

const dateInput = document.getElementById("dateFilter");
const updateButton = document.getElementById("updateMapBtn");
const status = document.getElementById("status");

const { viewer, fireLayer } = createGlobe();

let activeController = null;

async function updateMap() {
    const date = dateInput.value;

    if (!date) {
        status.textContent = "Select a date";
        return;
    }

    const { boxes, reason } = getVisibleBboxes(viewer);

    if (reason || boxes.length === 0) {
        status.textContent = "Zoom in to select a smaller region";
        return;
    }

    activeController?.abort();

    const controller = new AbortController();
    activeController = controller;

    status.textContent = "Loading...";

    try {
        const results = await Promise.all(
            boxes.map(box =>
                fetchFires(date, box, controller.signal)
            )
        );

        if (controller.signal.aborted) return;

        const uniqueFires = new Map();

        for (const fires of results) {
            for (const fire of fires) {
                uniqueFires.set(fire.id, fire);
            }
        }

        const fires = [...uniqueFires.values()];

        renderFires(fireLayer, fires);

        status.textContent =
            `${fires.length} detections loaded`;

    } catch (error) {
        if (error.name === "AbortError") return;

        console.error(error);
        status.textContent = "API request failed";
    }
}

updateButton.addEventListener("click", updateMap);


// =============================
// STATISTICS CHART
// =============================

const loadStatsButton = document.getElementById("loadStatsBtn");
const statsStatus = document.getElementById("statsStatus");
const statsMetric = document.getElementById("statsMetric");

let currentStatistics = [];
let statsChart = null;


function renderStatsChart(statistics) {
    const metric = statsMetric.value;

    const metricNames = {
        bucket_fire_count: "Hotspot detections",
        total_frp: "Total FRP (MW)",
        mean_frp: "Mean FRP (MW)"
    };

    const labels = statistics.map(item =>
        `${item.start_point} – ${item.end_point}`
    );

    const values = statistics.map(item =>
        Number(item[metric])
    );

    const ctx = document.getElementById("statsChart");

    if (statsChart) {
        statsChart.destroy();
    }

    statsChart = new Chart(ctx, {
        type: "bar",

        data: {
            labels: labels,
            datasets: [{
                label: metricNames[metric],
                data: values,
                borderWidth: 1,
                borderRadius: 5
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    labels: {
                        color: "#ffffff"
                    }
                }
            },

            scales: {
                x: {
                    ticks: {
                        color: "#ffffff"
                    },
                    grid: {
                        display: false
                    }
                },

                y: {
                    beginAtZero: true,
                    ticks: {
                        color: "#ffffff"
                    },
                    grid: {
                        color: "rgba(255,255,255,0.1)"
                    }
                }
            }
        }
    });
}


loadStatsButton.addEventListener("click", async () => {
    const from = document.getElementById("statsFrom").value;
    const to = document.getElementById("statsTo").value;
    const interval = Number(
        document.getElementById("statsInterval").value
    );

    if (!from || !to || from > to || !Number.isInteger(interval) || interval < 1) {
        statsStatus.textContent = "Check dates and interval";
        return;
    }

    statsStatus.textContent = "Loading statistics...";
    loadStatsButton.disabled = true;

    try {
       const { boxes, reason } = getVisibleBboxes(viewer);

if (reason || boxes.length === 0) {
    statsStatus.textContent = "Zoom in to select a region";
    return;
}

const results = await Promise.all(
    boxes.map(box =>
        fetchFireStats(from, to, interval, box)
    )
);

const merged = new Map();

for (const statistics of results) {
    for (const item of statistics) {
        const key = `${item.start_point}_${item.end_point}`;

        if (!merged.has(key)) {
            merged.set(key, {
                ...item,
                bucket_fire_count: 0,
                total_frp: 0
            });
        }

        const bucket = merged.get(key);

        bucket.bucket_fire_count += item.bucket_fire_count;
        bucket.total_frp += item.total_frp;
    }
}

currentStatistics = [...merged.values()].map(item => ({
    ...item,
    mean_frp: item.bucket_fire_count
        ? item.total_frp / item.bucket_fire_count
        : 0
}));

renderStatsChart(currentStatistics);

        if (currentStatistics.length === 0) {
            statsStatus.textContent = "No statistics available";
            return;
        }

        renderStatsChart(currentStatistics);

        statsStatus.textContent =
            `${currentStatistics.length} intervals loaded`;

    } catch (error) {
        console.error(error);
        statsStatus.textContent = "Failed to load statistics";

    } finally {
        loadStatsButton.disabled = false;
    }
});


statsMetric.addEventListener("change", () => {
    if (currentStatistics.length > 0) {
        renderStatsChart(currentStatistics);
    }
});
