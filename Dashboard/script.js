document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:5000/api/optimize';
    const PRIORITY_COLORS = { 1: '#e57373', 2: '#64b5f6', 3: '#81c784' };
    const CHART_START_HOUR = 9;
    const CHART_END_HOUR = 15;

    const optimizeButton = document.getElementById('optimizeButton');
    const statusElement = document.getElementById('status');
    const chartSvg = document.getElementById('ganttChart');

    optimizeButton.addEventListener('click', getOptimizedSchedule);

    async function getOptimizedSchedule() {
        statusElement.innerText = "🧠 Calling optimizer...";
        optimizeButton.disabled = true;
        try {
            const scheduleData = await fetch(API_URL).then(res => res.json());
            statusElement.innerText = "✅ Success! Rendering schedule.";
            drawGanttChart(scheduleData);
        } catch (error) {
            console.error("Could not fetch data:", error);
            statusElement.innerText = "❌ Error fetching data. Did the optimizer fail?";
        } finally {
            optimizeButton.disabled = false;
        }
    }

    function drawGanttChart(scheduleData) {
        chartSvg.innerHTML = '';
        // This should be dynamically loaded in a real app, but is fine for the prototype
        const STATIONS = ['CSTM', 'DR', 'KYN', 'KJT', 'LNL', 'TGN', 'DVR', 'KAD', 'SVJR', 'PUNE'];

        const margin = { top: 40, right: 30, bottom: 20, left: 60 };
        const width = chartSvg.parentElement.clientWidth - margin.left - margin.right;
        const height = STATIONS.length * 50;

        chartSvg.setAttribute('width', width + margin.left + margin.right);
        chartSvg.setAttribute('height', height + margin.top + margin.bottom);

        const g = createSvgElement('g', { transform: `translate(${margin.left},${margin.top})` });
        chartSvg.appendChild(g);

        const timeToX = (timeStr) => {
            const [h, m, s] = timeStr.split(':').map(Number);
            const startTimeInSeconds = CHART_START_HOUR * 3600;
            const endTimeInSeconds = CHART_END_HOUR * 3600;
            const totalVisibleSeconds = endTimeInSeconds - startTimeInSeconds;
            const seconds = h * 3600 + m * 60 + s;
            return ((seconds - startTimeInSeconds) / totalVisibleSeconds) * width;
        };
        const stationY = (stationCode) => STATIONS.indexOf(stationCode) * 50;

        for (let hour = CHART_START_HOUR; hour <= CHART_END_HOUR; hour++) {
            const xPos = timeToX(`${hour}:00:00`);
            g.appendChild(createSvgElement('line', { x1: xPos, x2: xPos, y1: -10, y2: height, class: 'time-axis-line' }));
            g.appendChild(createSvgElement('text', { x: xPos, y: -15, 'text-anchor': 'middle', class: 'time-axis-label' }, `${hour}:00`));
        }

        STATIONS.forEach((station, i) => {
            const yPos = i * 50 + 25;
            g.appendChild(createSvgElement('text', { x: -10, y: yPos, 'text-anchor': 'end', class: 'station-label' }, station));
        });

        // --- NEW DRAWING LOGIC ---
        // Draw a bar for each stop (halt) in the schedule
        scheduleData.forEach(stop => {
            const startX = timeToX(stop.optimized_arrival);
            const endX = timeToX(stop.optimized_departure);
            const y = stationY(stop.station_code) + 5;
            const barWidth = endX - startX;

            // Only draw a bar if the halt time is meaningful
            if (barWidth > 0 && STATIONS.includes(stop.station_code)) {
                const trainNum = parseInt(stop.train_id.match(/\d+/)[0]);
                const priority = (trainNum % 3) + 1;

                const rect = createSvgElement('rect', { x: startX, y: y, width: barWidth, height: 40, fill: PRIORITY_COLORS[priority], class: 'train-bar'});
                const text = createSvgElement('text', { x: startX + barWidth / 2, y: y + 25, class: 'train-label' }, stop.train_id.replace('Train_', 'T-'));

                g.appendChild(rect);
                g.appendChild(text);
            }
        });
    }

    function createSvgElement(tag, attrs, textContent) {
        const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        for (let key in attrs) {
            el.setAttribute(key, attrs[key]);
        }
        if (textContent) {
            el.textContent = textContent;
        }
        return el;
    }
});