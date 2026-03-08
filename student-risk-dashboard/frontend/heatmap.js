let map;
let markerGroup;
let allSchoolData = []; // Store fetched data

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/api/analytics/heatmap');
        if(!res.ok) throw new Error("Failed to fetch heatmap data");
        allSchoolData = await res.json();
        
        initMap();
        populateBlockFilter();
        renderMarkers(allSchoolData);

        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('dashboardContent').classList.remove('hidden');

        // Force a map cache invalidate to prevent gray tiles on hidden->shown transitions
        setTimeout(() => {
            map.invalidateSize();
        }, 100);

    } catch (e) {
        console.error(e);
        document.getElementById('loadingState').innerHTML = `<p class="text-red-500 text-2xl font-black">Error loading data. Is the server running?</p>`;
    }
});

function initMap() {
    // Center roughly on Kanchipuram
    map = L.map('map').setView([12.83, 79.70], 10);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    markerGroup = L.layerGroup().addTo(map);
}

function renderMarkers(data) {
    markerGroup.clearLayers();

    data.forEach(school => {
        let color = '#ec4899'; // Default
        if (school.risk_concentration === 'High') color = '#dc2626'; // red-600
        else if (school.risk_concentration === 'Moderate') color = '#eab308'; // yellow-500
        else if (school.risk_concentration === 'Low') color = '#10b981'; // emerald-500

        const circleMarker = L.circleMarker([school.lat, school.lng], {
            radius: Math.max(10, Math.min(30, school.total_students / 2)), // Size implies volume
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        // Simple tooltip
        circleMarker.bindTooltip(`<b>${school.school_name}</b><br>High Risk: ${school.high_risk_pct}%`);

        // Click event to update side panel
        circleMarker.on('click', () => {
            updateSidePanel(school);
            // Highlight selected marker visually
            map.setView([school.lat, school.lng], map.getZoom(), { animate: true });
        });

        circleMarker.addTo(markerGroup);
    });
}

function updateSidePanel(school) {
    document.getElementById('schoolDetailsPlaceholder').classList.add('hidden');
    document.getElementById('schoolDetailsPanel').classList.remove('hidden');

    document.getElementById('panelSchoolName').textContent = school.school_name;
    document.getElementById('panelBlockName').textContent = school.block_name + " Block";
    document.getElementById('panelTotal').textContent = school.total_students;
    document.getElementById('panelHighRisk').textContent = `${school.high_risk_count} (${school.high_risk_pct}%)`;
    document.getElementById('panelAvgRisk').textContent = school.avg_risk_score;
    document.getElementById('panelAvgAtt').textContent = `${school.avg_attendance}%`;

    const factorsContainer = document.getElementById('panelFactors');
    factorsContainer.innerHTML = '';
    
    if (school.top_factors && school.top_factors.length > 0) {
        school.top_factors.forEach(f => {
            const span = document.createElement('span');
            span.className = "text-xs font-bold bg-white/10 text-white px-3 py-1.5 rounded-lg border border-white/20";
            span.textContent = f;
            factorsContainer.appendChild(span);
        });
    } else {
        factorsContainer.innerHTML = `<span class="text-xs text-gray-400 italic">No dominating risk factors</span>`;
    }
}

function populateBlockFilter() {
    const filter = document.getElementById('blockFilter');
    const blocks = new Set(allSchoolData.map(s => s.block_name));
    
    blocks.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b;
        opt.textContent = b;
        filter.appendChild(opt);
    });

    filter.addEventListener('change', applyFilters);
    document.getElementById('riskFilter').addEventListener('change', applyFilters);
}

function applyFilters() {
    const blockFilter = document.getElementById('blockFilter').value;
    const riskFilter = document.getElementById('riskFilter').value;

    let filtered = allSchoolData;

    if (blockFilter !== 'All') {
        filtered = filtered.filter(s => s.block_name === blockFilter);
    }

    if (riskFilter !== 'All') {
        filtered = filtered.filter(s => s.risk_concentration === riskFilter);
    }

    renderMarkers(filtered);
    
    // Fit bounds if we have points, else ignore
    if (filtered.length > 0) {
        const lats = filtered.map(f => f.lat);
        const lngs = filtered.map(f => f.lng);
        const minLat = Math.min(...lats);
        const maxLat = Math.max(...lats);
        const minLng = Math.min(...lngs);
        const maxLng = Math.max(...lngs);
        map.fitBounds([[minLat, minLng], [maxLat, maxLng]], { padding: [50, 50] });
    }
}
