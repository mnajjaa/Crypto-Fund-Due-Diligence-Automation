document.addEventListener("DOMContentLoaded", function () {
  function formatAbbreviated(value) {
    if (value >= 1_000_000_000) return (value / 1_000_000_000).toFixed(2) + ' B';
    if (value >= 1_000_000) return (value / 1_000_000).toFixed(2) + ' M';
    if (value >= 1_000) return (value / 1_000).toFixed(2) + ' K';
    return value?.toLocaleString() ?? '—';
  }

  const coins_list = JSON.parse(`{{ coins_list|safe }}`);
  const tableBody = document.getElementById("coinTableBody");
  const paginationContainer = document.getElementById("pagination");
  const searchInput = document.getElementById("coinSearch");
  const searchBtn = document.getElementById("searchBtn");

  let filteredCoins = [...coins_list];
  let currentPage = 1;
  const rowsPerPage = 10;

  function renderTable(data, page = 1) {
    tableBody.innerHTML = "";
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedCoins = data.slice(start, end);

    if (paginatedCoins.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="8">No matching coins found.</td></tr>`;
      return;
    }

    paginatedCoins.forEach((coin, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${start + index + 1}</td>
        <td class="text-start">
          <img src="${coin["image.icon"]}" alt="${coin.symbol}" style="width: 24px; height: 24px; border-radius: 50%; margin-right: 8px;">
          <strong>${coin.name}</strong> <span class="text-muted">(${coin.symbol})</span>
        </td>
        <td>$${parseFloat(coin["athPrice.USD"] || 0).toFixed(4)}</td>
      
        <td>$${formatAbbreviated(Number(coin.marketCap))}</td>
        <td>$${formatAbbreviated(Number(coin.volume24h))}</td>
        <td>${formatAbbreviated(Number(coin.availableSupply))}</td>
      `;
      tableBody.appendChild(row);
    });

    renderPagination(data.length, page);
  }

  function renderPagination(totalRows, current) {
    paginationContainer.innerHTML = "";
    const totalPages = Math.ceil(totalRows / rowsPerPage);
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.className = `btn btn-sm ${i === current ? 'btn-primary' : 'btn-outline-primary'} m-1`;
      btn.textContent = i;
      btn.addEventListener("click", () => {
        currentPage = i;
        renderTable(filteredCoins, currentPage);
      });
      paginationContainer.appendChild(btn);
    }
  }

  searchBtn.addEventListener("click", function () {
    const query = searchInput.value.trim().toLowerCase();
    filteredCoins = coins_list.filter(coin =>
      coin.name.toLowerCase().includes(query)
    );
    currentPage = 1;
    renderTable(filteredCoins, currentPage);
  });

  // Initial render
  renderTable(filteredCoins, currentPage);
});

document.addEventListener('DOMContentLoaded', () => {
// IDO Chart
let idochart;
const ctx2 = document.getElementById('idoChart').getContext('2d');
const IDO_TREND = JSON.parse('{{ funding_ido|escapejs }}');

const labels1 = IDO_TREND.map(entry => {
const date = new Date(entry.date);
return `${date.toLocaleString('default', { month: 'short' })} ${date.getFullYear()}`;
});
const sumData1 = IDO_TREND.map(entry => entry.sum / 1e6); // convert to millions
const countData1 = IDO_TREND.map(entry => entry.count);

idochart = new Chart(ctx2, {
type: 'bar',
data: {
  labels: labels1,
  datasets: [
    {
      label: "Raised in USD value",
      data: sumData1,
      backgroundColor: "#021b59",
      borderRadius: 6,
      barThickness: 20,
      yAxisID: 'y1'
    },
    {
      label: "IDO/ICO/IEO by month",
      data: countData1,
      type: 'line',
      borderColor: "#007bff",
      backgroundColor: "#007bff",
      pointRadius: 4,
      pointHoverRadius: 6,
      fill: false,
      tension: 0.4,
      yAxisID: 'y2'
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        font: { size: 13 },
        color: '#828181'
      }
    },
    tooltip: {
      backgroundColor: '#fff',
      borderColor: '#ccc',
      borderWidth: 1,
      titleColor: '#222',
      bodyColor: '#444',
      padding: 10,
      callbacks: {
        label: function (context) {
          const value = context.raw;
          return context.dataset.label.includes("Raised")
            ? `$${value.toFixed(2)}M`
            : `${value} rounds`;
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#828181',
        font: { size: 12 }
      },
      grid: {
        drawBorder: false,
        color: 'rgba(0,0,0,0.05)'
      }
    },
    y1: {
      position: 'left',
      beginAtZero: true,
      ticks: {
        color: '#808080',
        callback: v => `$${v.toFixed(0)}M`
      },
      title: {
        display: true,
        text: 'Raised Amount',
        color: '#a1a1a1',
        font: { size: 12 }
      }
    },
    y2: {
      position: 'right',
      beginAtZero: true,
      grid: { drawOnChartArea: false },
      ticks: {
        color: '#808080'
      },
      title: {
        display: true,
        text: 'Number of IDO/ICO/IEO',
        color: '#a1a1a1',
        font: { size: 12 }
      }
    }
  }
}
});

// Fundraising Chart
const ctx1 = document.getElementById('fundraisingChart').getContext('2d');
const FUNDING_TREND = JSON.parse('{{ funding_trend|escapejs }}');

const labels = FUNDING_TREND.map(entry => {
const date = new Date(entry.date);
return `${date.toLocaleString('default', { month: 'short' })} ${date.getFullYear()}`;
});

const raiseData = FUNDING_TREND.map(entry => entry.raise / 1e6); // in millions
const countData = FUNDING_TREND.map(entry => entry.count);

let fundraisingChart = new Chart(ctx1, {
type: 'bar',
data: {
  labels,
  datasets: [
    {
      label: "Raised in USD value",
      data: raiseData,
      backgroundColor: "#007bff",
      borderRadius: 6,
      barThickness: 20,
      yAxisID: 'y1'
    },
    {
      label: "Number of fundraising rounds",
      data: countData,
      type: 'line',
      borderColor: "#7cb342",
      backgroundColor: "#7cb342",
      pointRadius: 4,
      pointHoverRadius: 6,
      fill: false,
      tension: 0.4,
      yAxisID: 'y2'
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: 0
  },
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        font: { size: 13 },
        color: '#828181'
      }
    },
    tooltip: {
      backgroundColor: '#fff',
      borderColor: '#ccc',
      borderWidth: 1,
      titleColor: '#222',
      bodyColor: '#444',
      padding: 10,
      callbacks: {
        label: function(context) {
          const value = context.raw;
          return context.dataset.label.includes("Raised")
            ? `$${(value/1000).toFixed(2)}B`
            : `${value} rounds`;
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#828181',
        font: { size: 12 }
      },
      grid: {
        drawBorder: false,
        color: 'rgba(0,0,0,0.0)'
      }
    },
    y1: {
      position: 'left',
      beginAtZero: true,
      ticks: {
        color: '#808080',
        callback: v => `$${v/1000}B`
      },
      grid: {
        drawBorder: false,
        color: 'rgba(0,0,0,0.0)'
      },
      title: {
        display: true,
        text: 'Raised Amount',
        color: '#a1a1a1',
        font: { size: 12 }
      }
    },
    y2: {
      position: 'right',
      beginAtZero: true,
      grid: { drawOnChartArea: false },
      ticks: { color: '#808080' },
      title: {
        display: true,
        text: 'Number of Rounds',
        color: '#a1a1a1',
        font: { size: 12 }
      }
    }
  }
}
});

// Fear & Greed Index
const levels = {
0: "Extreme fear",
25: "Fear",
50: "Neutral",
75: "Greed",
100: "Extreme greed"
};

const interpret = (score) => {
if (score < 25) return "Extreme fear";
if (score < 50) return "Fear";
if (score < 75) return "Greed";
return "Extreme greed";
};

const fearGreed = JSON.parse('{{ fear_greed|escapejs }}');
const data = fearGreed[0] || {};

const today = data.today;
const yesterday = data.yesterday;
const lastWeek = data.lastWeek;
const lastMonth = data.lastMonth;

document.getElementById("fg-today").innerText = today;
document.getElementById("fg-sentiment").innerText = interpret(today);
document.getElementById("fg-desc").innerText =
interpret(today) === "Extreme fear"
  ? "Market sentiment is very bearish, many assets may be undervalued."
  : "Market sentiment is improving, but volatility remains.";

document.getElementById("fg-yesterday").innerText = yesterday;
document.getElementById("fg-sentiment-yesterday").innerText = interpret(yesterday);

document.getElementById("fg-week").innerText = lastWeek;
document.getElementById("fg-sentiment-week").innerText = interpret(lastWeek);

document.getElementById("fg-month").innerText = lastMonth;
document.getElementById("fg-sentiment-month").innerText = interpret(lastMonth);

function placeDotIndicator(score) {
const dot = document.getElementById("dot-indicator");
const percentage = Math.min(100, Math.max(0, score));
dot.style.left = `calc(${percentage}% - 8px)`;
}

placeDotIndicator(today);

// Upcoming IDOs
const container = document.getElementById("upcoming-list");
container.innerHTML = "<p>Loading...</p>";

try {
const items = upcomingData || [];

if (items.length === 0) {
  container.innerHTML = "<p>No upcoming IDOs found.</p>";
  return;
}

container.innerHTML = ""; // Clear loading

items.slice(0, 5).forEach(item => {
  const name = item.name || item.name;
  const symbol = item.symbol || item.symbol;
  const image = item.image || item.image;
  const category = item.category_name;
  const date = new Date(item.startDate || item.when).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short"
  });
  
  const raise = item.raise
    ? `$ ${formatRaise(item.raise)}`
    : "TBA";
  const launchpad = item.launchpad;
  const launchpadLogo = item.launchpad_logo;

  const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center py-3 px-2";
      li.style.border = "none";

  li.innerHTML = `
    <div class="ido-col ido-left">
      <div class="ido-logo-wrapper">
        <img src="${image}" alt="${name}" class="ido-logo">
      </div>
      <div class="ido-info">
        <div class="ido-name">
          <strong>${name}</strong> <span class="ido-symbol">${symbol}</span>
        </div>
        <div class="ido-date">${date}</div>
      </div>
    </div>

    <div class="ido-col ido-middle text-end d-flex flex-column align-items-end">
      <div class="ido-raise">${raise}</div>
      <div class="ido-category">${category}</div>
    </div>

    <div class="ido-col ido-right d-flex align-items-center gap-2">
      ${launchpadLogo ? `<img src="${launchpadLogo}" alt="${launchpad}" class="ido-launchpad-logo">` : ""}
      <div class="ido-launchpad-name">${launchpad}</div>
    </div>
  `;

  container.appendChild(li);
});
} catch (err) {
console.error("Error rendering upcoming IDOs:", err);
container.innerHTML = "<p>Error loading IDO list.</p>";
}

function formatRaise(amount) {
if (amount >= 1e6) return (amount / 1e6).toFixed(2) + "M";
if (amount >= 1e3) return (amount / 1e3).toFixed(2) + "K";
return amount.toFixed(0);
}

// BTC Dominance Chart
const BTC_DOMINANCE = JSON.parse('{{ btc_data|escapejs }}');
const SELECTED_PERIOD = "{{ selected_period }}";

const ctx = document.getElementById('btcDominanceChart').getContext('2d');
const periodSelect = document.getElementById("period-select");
const valueEl = document.getElementById("btc-dominance-value");
const changeEl = document.getElementById("btc-dominance-change");
let btcChart;

renderBtcChartFromViewData(SELECTED_PERIOD);

periodSelect.addEventListener("change", () => {
renderBtcChartFromViewData(periodSelect.value);
});

function renderBtcChartFromViewData(period) {
const data = BTC_DOMINANCE[period];

if (!data || data.length < 2) {
  console.warn("No data for selected period:", period);
  return;
}

const values = data.map(d => parseFloat(d.dominance));
const timestamps = data.map(d => new Date(d.timestamp));

const current = values.at(-1);
const previous = values.at(-2);
const change = ((current - previous) / previous) * 100;
const sign = change >= 0 ? "+" : "";
const direction = change >= 0 ? "↑" : "↓";

valueEl.textContent = `${current.toFixed(2)}%`;
changeEl.innerHTML = `${sign}${change.toFixed(2)}% <span class="arrow">${direction}</span>`;
changeEl.style.color = change >= 0 ? "green" : "red";

if (btcChart) btcChart.destroy();

btcChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: timestamps,
    datasets: [{
      data: values,
      borderColor: '#f27935',
      backgroundColor: 'rgba(242, 121, 53, 0.1)',
      tension: 0.3,
      fill: true,
      pointRadius: 0,
      borderWidth: 2
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        enabled: true,
        backgroundColor: '#fff',
        titleColor: '#222',
        bodyColor: '#222',
        borderColor: '#ddd',
        borderWidth: 1,
        usePointStyle: true,
        padding: 12,
        cornerRadius: 6,
        callbacks: {
          title: function (tooltipItems) {
            const date = new Date(tooltipItems[0].label);
            return `Date: ${date.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}, ${date.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              hour12: false
            })}`;
          },
          label: function (tooltipItem) {
            return `Dominance: ${tooltipItem.formattedValue}%`;
          }
        }
      }
    },
    scales: {
      x: { display: false },
      y: {
        position: 'right',
        display: true,
        ticks: {
          callback: value => value.toFixed(1) + "%",
          color: "#aaa",
          font: { size: 10 },
          stepSize: 0.5
        },
        border: { display: false },
        grid: {
          drawTicks: false,
          drawBorder: false,
          color: "rgba(0,0,0,0.05)"
        }
      }
    }
  }
});
}

// Gainers and Losers
function renderGainers(gainers = TOP_GAINERS) {
const list = document.getElementById("gainers-list");
list.innerHTML = "";
gainers.slice(0, 5).forEach((coin, i) => {
  const li = document.createElement("li");
  li.classList.add("gainer-item");
  li.innerHTML = `
    <div class="market-rank">${i + 1}</div>
    <img class="market-logo" src="${coin.image}" alt="${coin.symbol}">
    <div class="market-info">
      <div><strong>${coin.name}</strong> 
        <span class="symbol">${coin.symbol}</span></div>
      <div class="market-category">${coin.category || '—'}</div>
    </div>
    <div class="market-change" style="color:green;">+${parseFloat(coin.gainPercent).toFixed(1)}%</div>
  `;
  list.appendChild(li);
});
}

function renderLosers(losers = TOP_LOSERS) {
const list = document.getElementById("losers-list");
list.innerHTML = "";
losers.slice(0, 5).forEach((coin, i) => {
  const li = document.createElement("li");
  li.classList.add("losers-item");
  li.innerHTML = `
    <div class="market-rank">${i + 1}</div>
    <img class="market-logo" src="${coin.image}" alt="${coin.symbol}">
    <div class="market-info">
      <div><strong>${coin.name}</strong> <span class="symbol">${coin.symbol}</span></div>
      <div class="market-category">${coin.category || '—'}</div>
    </div>
    <div class="market-change" style="color:red;">+${parseFloat(coin.losePercent).toFixed(1)}%</div>
  `;
  list.appendChild(li);
});
}

renderGainers();
renderLosers();

// Featured Project Slider

let sliderInterval;

function resetSliderInterval() {
clearInterval(sliderInterval);
sliderInterval = setInterval(() => {
  currentIndex = (currentIndex + 1) % projects.length;
  renderProject(currentIndex);
}, 30000);
}

function startSlider() {
renderProject(currentIndex);
sliderInterval = setInterval(() => {
  currentIndex = (currentIndex + 1) % projects.length;
  renderProject(currentIndex);
}, 30000);
}

if (projects.length > 0) {
startSlider();
} else {
slider.innerHTML = "<p>No projects found</p>";
}

// Coins Table
function formatAbbreviated(value) {
if (value >= 1_000_000_000) return (value / 1_000_000_000).toFixed(2) + ' B';
if (value >= 1_000_000) return (value / 1_000_000).toFixed(2) + ' M';
if (value >= 1_000) return (value / 1_000).toFixed(2) + ' K';
return value?.toLocaleString() ?? '—';
}

const coins_list = JSON.parse(`{{ coins_list|safe }}`);
const tableBody = document.getElementById("coinTableBody");
const paginationContainer = document.getElementById("pagination");
const searchInput = document.getElementById("coinSearch");
const searchBtn = document.getElementById("searchBtn");

let filteredCoins = [...coins_list];
let currentPage = 1;
const rowsPerPage = 10;

function renderTable(data, page = 1) {
tableBody.innerHTML = "";
const start = (page - 1) * rowsPerPage;
const end = start + rowsPerPage;
const paginatedCoins = data.slice(start, end);

if (paginatedCoins.length === 0) {
  tableBody.innerHTML = `<tr><td colspan="8">No matching coins found.</td></tr>`;
  return;
}

paginatedCoins.forEach((coin, index) => {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${start + index + 1}</td>
    <td class="text-start">
      <img src="${coin["image.icon"]}" alt="${coin.symbol}" style="width: 24px; height: 24px; border-radius: 50%; margin-right: 8px;">
      <strong>${coin.name}</strong> <span class="text-muted">(${coin.symbol})</span>
    </td>
    <td>$${parseFloat(coin["athPrice.USD"] || 0).toFixed(4)}</td>
    <td>$${formatAbbreviated(Number(coin.marketCap))}</td>
    <td>$${formatAbbreviated(Number(coin.volume24h))}</td>
    <td>${formatAbbreviated(Number(coin.availableSupply))}</td>
  `;
  tableBody.appendChild(row);
});

renderPagination(data.length, page);
}

function renderPagination(totalRows, current) {
paginationContainer.innerHTML = "";
const totalPages = Math.ceil(totalRows / rowsPerPage);
for (let i = 1; i <= totalPages; i++) {
  const btn = document.createElement("button");
  btn.className = `btn btn-sm ${i === current ? 'btn-primary' : 'btn-outline-primary'} m-1`;
  btn.textContent = i;
  btn.addEventListener("click", () => {
    currentPage = i;
    renderTable(filteredCoins, currentPage);
  });
  paginationContainer.appendChild(btn);
}
}/*  */

searchBtn.addEventListener("click", function () {
const query = searchInput.value.trim().toLowerCase();
filteredCoins = coins_list.filter(coin =>
  coin.name.toLowerCase().includes(query)
);
currentPage = 1;
renderTable(filteredCoins, currentPage);
});

renderTable(filteredCoins, currentPage);
  });

const slider = document.getElementById("featured-project-slider");
let currentIndex = 0;
let projects = [];

// Get data from the injected script tag
const raw = JSON.parse(document.getElementById("hot-events-data").textContent);

// Group backers by project_key
const projectMap = new Map();

raw.forEach(row => {
const key = row.project_key;
if (!projectMap.has(key)) {
  projectMap.set(key, {
    name: row.project_name,
    logo: row.project_logo,
    totalRaise: row.totalRaise,
    taskTypes: row.taskTypes.split(",")[0].trim(),
    topFunds: []
  });
}
projectMap.get(key).topFunds.push({
  name: row.backer_name,
  logo: row.backer_logo
});
});

projects = Array.from(projectMap.values());

function renderProject(index) {
const proj = projects[index];

const tag = proj.taskTypes || '—';
const backerLogo = proj.topFunds?.[0]?.logo || '';
const raised = (proj.totalRaise / 1e6).toFixed(2);

slider.innerHTML = `
  <div class="project-card hot-event-card">
    <div class="hot-event-main">
      <img src="${proj.logo}" class="event-logo" alt="${proj.name}">
      <div class="event-info">
        <h4 class="event-title">${proj.name}</h4>
        <span class="event-tag">${tag}</span>
      </div>
      <div class="event-rank">
        <div class="nav-up" style="cursor:pointer;">↑</div>
        <div class="nav-down" style="cursor:pointer;">↓</div>
      </div>
    </div>

    <div class="hot-event-footer">
      <div class="event-backers">
        <span>Backers:</span>
        <img src="${backerLogo}" alt="backer" class="backer-icon">
      </div>
      <div class="event-raised">
        Raised: <strong>$ ${raised}M</strong>
      </div>
    </div>
  </div>
`;

document.querySelector('.nav-up').addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + projects.length) % projects.length;
  renderProject(currentIndex);
  resetSliderInterval();
});

document.querySelector('.nav-down').addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % projects.length;
  renderProject(currentIndex);
  resetSliderInterval();
});
}

let sliderInterval;

function resetSliderInterval() {
clearInterval(sliderInterval);
sliderInterval = setInterval(() => {
  currentIndex = (currentIndex + 1) % projects.length;
  renderProject(currentIndex);
}, 30000);
}

function startSlider() {
renderProject(currentIndex);
sliderInterval = setInterval(() => {
  currentIndex = (currentIndex + 1) % projects.length;
  renderProject(currentIndex);
}, 30000);
}

// ✅ Now use the preloaded data
if (projects.length > 0) {
startSlider();
} else {
slider.innerHTML = "<p>No projects found</p>";
}


document.addEventListener("DOMContentLoaded", () => {
const gainers = JSON.parse(document.getElementById("gainers-data").textContent);
const list = document.getElementById("gainers-list");
list.innerHTML = "";

gainers
  .slice(0, 5)  // Optional: top 5
  .forEach((coin, index) => {
    const li = document.createElement("li");
    li.className = "d-flex justify-content-between align-items-center mb-3";

    const priceFormatted = parseFloat(coin.current_price).toLocaleString("en-US", {
      minimumFractionDigits: 4,
      maximumFractionDigits: 6,
    });

    li.innerHTML = `
      <div class="d-flex align-items-center gap-3">
        <strong class="text-muted">${index + 1}</strong>
        <img src="${coin.image}" alt="${coin.name}" style="width: 32px; height: 32px; border-radius: 50%;">
        <div>
          <div><strong>${coin.name}</strong> <span class="text-muted">${coin.symbol}</span></div>
          <div class="text-muted small">${coin.category}</div>
        </div>
      </div>
      <span class="badge bg-success-subtle text-success fw-bold" style="font-size: 0.9rem;">$${priceFormatted}</span>
    `;
    list.appendChild(li);
  });
});
  document.addEventListener("DOMContentLoaded", () => {
    const rounds = JSON.parse(`{{ upcoming_funds|escapejs }}`);  // Or use a `<script>` tag with ID if passing manually
    const list = document.getElementById("funding-rounds-list");
  
    rounds.slice(0, 5).forEach(item => {
      const name = item.name || "—";
      const icon = item.icon || "";
      const date = new Date(item.date).toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short"
      });
      const raise = item.raise
        ? `$ ${(item.raise / 1e6).toFixed(2)}M`
        : "N/A";
  
      const fundName = item.fund_name || "—";
      const fundLogo = item.fund_image || "";
      const stage = item.stage || "Undisclosed";
  
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center py-3 px-2";
      li.style.border = "none";

      li.innerHTML = `
       <div class="ido-col ido-left">
      <div class="ido-logo-wrapper">
        <img src="${icon}" alt="${name}" class="ido-logo">
      </div>
      <div class="ido-info">
        <div class="ido-name">
          <strong>${name}</strong> 
        </div>
        <div class="ido-info">${stage}</div>
      </div>
    </div>

    <div class="ido-col ido-middle text-end d-flex flex-column align-items-end">
      <div class="ido-raise">${raise}</div>
      <div class="ido-date">${date}</div>
    </div>

    <div class="ido-col ido-right d-flex align-items-center gap-2">
      ${fundLogo ? `<img src="${fundLogo}" alt="${fundName}" class="ido-launchpad-logo">` : ""}
      <div class="ido-launchpad-name">${fundName}</div>
    </div>
  `;
  
      list.appendChild(li);
    });
  });