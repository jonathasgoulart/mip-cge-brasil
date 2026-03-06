document.addEventListener('DOMContentLoaded', async () => {
    // Initialize particles background
    createParticles();

    // Setup navigation
    setupNavigation();

    // Load dashboard data
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Data loaded successfully:', data);
        renderDashboard(data);
    } catch (err) {
        console.error("Erro ao carregar dados:", err);
        alert('Erro ao carregar os dados: ' + err.message + '\n\nTente abrir o dashboard com um servidor HTTP local (ex: Live Server extension)');
    }
});

// Particle Background Animation
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';

        // Random positioning
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';

        // Random size variation
        const size = Math.random() * 3 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';

        particlesContainer.appendChild(particle);
    }
}

// Smooth Navigation Setup
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));

            // Add active class to clicked link
            link.classList.add('active');

            // Scroll to section
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animated Number Counter
function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            clearInterval(timer);
            current = end;
        }
        element.textContent = Math.round(current).toLocaleString();
    }, 16);
}

function renderDashboard(data) {
    // 1. Stats Gerais
    const avgMult = data.stats.multiplicadores.Sao_Paulo.valor;
    document.getElementById('avg-mult').textContent = avgMult.toFixed(3);

    // Calculate total jobs from simulations
    const totalJobs = data.beyonce.total_empregos + (data.carnaval.total_empregos || 50611);
    document.getElementById('total-jobs').textContent = (totalJobs / 1000).toFixed(0) + 'K+';

    // 2. Beyoncé (RJ)
    const beyProdValue = data.beyonce.impacto_producao;
    const beyEmpValue = Math.round(data.beyonce.total_empregos);

    document.getElementById('bey-prod').textContent = `R$ ${beyProdValue.toFixed(0)}M`;
    document.getElementById('bey-emp').textContent = beyEmpValue.toLocaleString();

    const ctxBey = document.getElementById('beyonce-bar').getContext('2d');
    new Chart(ctxBey, {
        type: 'bar',
        data: {
            labels: data.beyonce.top_setores_prod.map(s => s.nome),
            datasets: [{
                data: data.beyonce.top_setores_prod.map(s => s.valor),
                backgroundColor: 'rgba(168, 85, 247, 0.8)',
                borderRadius: 12,
                barThickness: 20,
                hoverBackgroundColor: 'rgba(168, 85, 247, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleColor: '#00FFFF',
                    bodyColor: '#FFFFFF',
                    borderColor: 'rgba(0, 255, 255, 0.3)',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8a8d9b', font: { size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#8a8d9b', font: { size: 10 } }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });

    // 3. Carnaval (Spillover)
    const carnProdTotal = data.carnaval.impacto_producao_rj + data.carnaval.impacto_spillover;
    document.getElementById('carn-prod').textContent = `R$ ${carnProdTotal.toFixed(1)}B`;
    document.getElementById('carn-leak').textContent = `R$ ${data.carnaval.impacto_spillover.toFixed(0)}M`;

    const ctxCarn = document.getElementById('carnaval-doughnut').getContext('2d');
    new Chart(ctxCarn, {
        type: 'doughnut',
        data: {
            labels: ['Rio (Retained)', 'Spillover (BR)'],
            datasets: [{
                data: [data.carnaval.impacto_producao_rj, data.carnaval.impacto_spillover],
                backgroundColor: ['#00FFFF', '#A855F7'],
                borderWidth: 0,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#8a8d9b',
                        padding: 20,
                        font: { size: 12, weight: '600' }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleColor: '#00FFFF',
                    bodyColor: '#FFFFFF',
                    borderColor: 'rgba(0, 255, 255, 0.3)',
                    borderWidth: 1
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500
            }
        }
    });

    // 4. Regional Ranking
    const rankList = document.getElementById('rank-list');
    data.stats.rank_multiplicadores.forEach((reg, index) => {
        const item = document.createElement('div');
        item.className = 'rank-item';
        item.style.animationDelay = `${index * 0.1}s`;
        item.innerHTML = `<span class="r-name">${reg.nome}</span> <span class="r-val">${reg.valor.toFixed(3)}</span>`;
        rankList.appendChild(item);
    });

    const ctxReg = document.getElementById('region-compare-chart').getContext('2d');
    new Chart(ctxReg, {
        type: 'line',
        data: {
            labels: data.stats.rank_multiplicadores.map(r => r.nome),
            datasets: [{
                label: 'Production Multiplier',
                data: data.stats.rank_multiplicadores.map(r => r.valor),
                borderColor: '#00FFFF',
                backgroundColor: 'rgba(0, 255, 255, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: '#00FFFF',
                pointBorderColor: '#0a0a0f',
                pointBorderWidth: 2,
                pointHoverRadius: 8,
                pointHoverBackgroundColor: '#A855F7',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleColor: '#00FFFF',
                    bodyColor: '#FFFFFF',
                    borderColor: 'rgba(0, 255, 255, 0.3)',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8a8d9b', font: { size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#8a8d9b', font: { size: 10 } }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });


    // 5. Linkages & Key Sectors (RJ)
    const rjLinkages = data.linkages.Rio_de_Janeiro;
    if (rjLinkages) {
        renderKeySectors(rjLinkages.key_sectors);
        renderLinkageChart(rjLinkages.all_indices);
    }

    // 6. [NEW] Initialize Simulator
    if (data.simulator) {
        initSimulator(data.simulator);
    }
}

function renderKeySectors(keySectors) {
    const list = document.getElementById('key-sectors-list');
    if (!list) return;
    list.innerHTML = '';

    keySectors.forEach((sector, index) => {
        const item = document.createElement('div');
        item.className = 'key-item';
        item.style.animationDelay = `${index * 0.1}s`;
        item.innerHTML = `
            <div class="k-name">${sector.nome}</div>
            <div class="k-vals">
                <span class="k-val-tag bl">BL: ${sector.bl.toFixed(2)}</span>
                <span class="k-val-tag fl">FL: ${sector.fl.toFixed(2)}</span>
            </div>
        `;
        list.appendChild(item);
    });
}

function renderLinkageChart(allIndices) {
    const canvas = document.getElementById('linkage-bubble-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const datasets = [
        {
            label: 'Setores Chave',
            data: allIndices.filter(s => s.bl > 1 && s.fl > 1).map(s => ({ x: s.bl, y: s.fl, r: 8 })),
            backgroundColor: 'rgba(0, 255, 255, 0.7)',
            borderColor: '#00FFFF',
            borderWidth: 1
        },
        {
            label: 'Outros Setores',
            data: allIndices.filter(s => s.bl <= 1 || s.fl <= 1).map(s => ({ x: s.bl, y: s.fl, r: 4 })),
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderColor: 'rgba(255, 255, 255, 0.2)',
            borderWidth: 1
        }
    ];

    new Chart(ctx, {
        type: 'bubble',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#8a8d9b' } },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const point = allIndices.find(s => Math.abs(s.bl - ctx.raw.x) < 0.001 && Math.abs(s.fl - ctx.raw.y) < 0.001);
                            return `${point ? point.nome : ''}: BL=${ctx.raw.x.toFixed(2)}, FL=${ctx.raw.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Forward Linkage (FL)', color: '#8a8d9b' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8a8d9b' }
                },
                x: {
                    title: { display: true, text: 'Backward Linkage (BL)', color: '#8a8d9b' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8a8d9b' }
                }
            }
        }
    });
}

// --- DYNAMIC SIMULATOR LOGIC ---
let simulatorChart = null;

function initSimulator(simData) {
    const sectorSelect = document.getElementById('sim-sector');
    const regionSelect = document.getElementById('sim-region');
    const valueInput = document.getElementById('sim-value');
    const btnSimulate = document.getElementById('btn-simulate');

    if (!sectorSelect || !btnSimulate) return;

    // Populate Regions (Dynamic)
    if (simData.regions && simData.regions.length > 0) {
        regionSelect.innerHTML = ''; // Clear hardcoded
        simData.regions.forEach(reg => {
            const option = document.createElement('option');
            option.value = reg;
            option.textContent = reg.replace(/_/g, " ");
            regionSelect.appendChild(option);
        });
    }

    // Populate Sectors
    sectorSelect.innerHTML = '';
    simData.sector_labels.forEach((label, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = label;
        if (index === 0) option.selected = true;
        sectorSelect.appendChild(option);
    });

    // Event Listener
    btnSimulate.addEventListener('click', () => {
        runSimulation(simData, regionSelect.value, parseInt(sectorSelect.value), parseFloat(valueInput.value));
    });
}

function runSimulation(simData, regionKey, sectorIndex, valueMillions) {
    if (isNaN(valueMillions) || valueMillions <= 0) {
        alert("Por favor, insira um valor de choque positivo.");
        return;
    }

    const value = valueMillions;
    let L = null, x = null;
    const isGlobal = simData.l_matrices.GLOBAL ? true : false;

    // Preparation
    const n_sectors = simData.sector_labels.length;

    if (isGlobal) {
        // Global MRIO Mode
        L = simData.l_matrices.GLOBAL;
        const regions = simData.regions;
        const regIdx = regions.indexOf(regionKey);

        if (regIdx === -1) { console.error("Region not found", regionKey); return; }

        // Calculate Global Index of Shock
        const globalShockIdx = (regIdx * n_sectors) + sectorIndex;

        // x is the column of L at globalShockIdx * value
        x = [];
        for (let i = 0; i < L.length; i++) {
            x.push(L[i][globalShockIdx] * value);
        }

    } else {
        // Legacy Mode
        L = simData.l_matrices[regionKey];
        if (!L) { console.error("L not found for", regionKey); return; }

        x = [];
        for (let i = 0; i < L.length; i++) {
            x.push(L[i][sectorIndex] * value);
        }
    }

    // 2. Calculate Aggregates
    const e = simData.employment_vector;
    const t = simData.tax_vector || [];

    let totalOutput = 0;
    let totalJobs = 0;
    let totalTaxes = 0;

    for (let i = 0; i < x.length; i++) {
        totalOutput += x[i];

        // Safety check for vectors length
        const jobs = (e.length > i) ? x[i] * e[i] : 0;
        totalJobs += jobs;

        const tax = (t.length > i) ? x[i] * t[i] : 0;
        totalTaxes += tax;
    }

    // 3. Update UI
    const multiplier = totalOutput / value;

    const outElem = document.getElementById('res-output');
    outElem.textContent = `R$ ${totalOutput.toFixed(2)}M`;
    outElem.parentElement.classList.add('pulse');
    setTimeout(() => outElem.parentElement.classList.remove('pulse'), 1000);

    document.getElementById('res-mult').textContent = multiplier.toFixed(2) + 'x';
    document.getElementById('res-jobs').textContent = Math.round(totalJobs).toLocaleString();

    const taxElem = document.getElementById('res-taxes');
    if (taxElem) {
        taxElem.textContent = `R$ ${totalTaxes.toFixed(2)}M`;
    }

    // 4. Update Chart (Top 5 Indirect Impacts)
    // Pass extra context for Global Mode
    updateSimChart(x, simData.sector_labels, simData.regions, isGlobal, isGlobal ? (simData.regions.indexOf(regionKey) * n_sectors + sectorIndex) : sectorIndex);
}

function updateSimChart(outputVector, labels, regions, isGlobal, shockIdx) {
    const n_sectors = labels.length;

    // Map vector to labeled objects
    const items = outputVector.map((val, idx) => {
        let label = "";
        if (isGlobal) {
            const regI = Math.floor(idx / n_sectors);
            const secI = idx % n_sectors;
            const regName = regions[regI] || "?";
            label = `${regName}: ${labels[secI]}`;
        } else {
            label = labels[idx];
        }
        return { idx, val, label };
    });

    // Filter top 5 excluding the shock itself
    const ranked = items
        .filter(item => item.idx !== shockIdx)
        .sort((a, b) => b.val - a.val)
        .slice(0, 5);

    const ctx = document.getElementById('sim-chart').getContext('2d');

    if (simulatorChart) {
        simulatorChart.destroy();
    }

    simulatorChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ranked.map(r => r.label),
            datasets: [{
                label: 'Impacto Indireto (R$ M)',
                data: ranked.map(r => r.val),
                backgroundColor: 'rgba(0, 255, 255, 0.6)',
                borderColor: '#00FFFF',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8a8d9b' }
                },
                y: {
                    ticks: { color: '#fff', font: { size: 10 } }
                }
            }
        }
    });
}
