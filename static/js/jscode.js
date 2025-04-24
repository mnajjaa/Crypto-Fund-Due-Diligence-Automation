document.addEventListener('DOMContentLoaded', () => {
    const ITEMS_PER_PAGE = 10;
    const MAX_ITEMS = 1000;
    let currentPage = 1;
    let coins = [];
  
    const tbody = document.getElementById('coinTableBody');
    const paginationContainer = document.getElementById('pagination');
  
    // Fetch and store coins
    fetch('/api/coin-list/')
      .then(res => res.json())
      .then(data => {
        coins = data.pageProps.coins.slice(0, MAX_ITEMS);
        renderTable();
        renderPagination();
      })
      .catch(err => {
        console.error("Failed to load coin list:", err);
      });
  
    // Render table for current page
    function renderTable() {
      tbody.innerHTML = '';
      const start = (currentPage - 1) * ITEMS_PER_PAGE;
      const end = start + ITEMS_PER_PAGE;
      const currentCoins = coins.slice(start, end);
  
      currentCoins.forEach((coin, index) => {
        const price = coin.price.usd / 1e3 || 0;
        const marketCap = coin.marketCap / 1e12 || 0;
        const change24h = coin.values?.USD?.change24h || 0;
  
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${start + index + 1}</td>
          <td class="coin-name">
            <img src="${coin.image}" alt="${coin.symbol}">
            <div>
              <span>${coin.name}</span>
              <span class="coin-symbol">(${coin.symbol})</span>
            </div>
          </td>
          <td>$${price.toFixed(2)}</td>
          <td class="${change24h >= 0 ? 'up' : 'down'}">${change24h.toFixed(2)}%</td>
          <td>$${marketCap.toFixed(2)}B</td>
          <td>$${(coin.volume24h / 1e9).toFixed(2)}B</td>
          <td>${(coin.availableSupply / 1e6).toFixed(2)}M</td>
          <td><canvas id="chart${start + index}" width="100" height="40"></canvas></td>`
        ;
        tbody.appendChild(row);
      });
    }
    // Render pagination buttons
    function renderPagination() {
    paginationContainer.innerHTML = '';
    const totalPages = Math.ceil(coins.length / ITEMS_PER_PAGE);
  
    // Prev button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'prev';
    prevBtn.classList.add('page__btn');
    if (currentPage > 1) {
      prevBtn.addEventListener('click', () => {
        currentPage--;
        renderTable();
        renderPagination();
      });
    } else {
      prevBtn.setAttribute('disabled', true);
    }
    paginationContainer.appendChild(prevBtn);
  
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
      const pageNum = document.createElement('button');
      pageNum.textContent = i;
      pageNum.classList.add('page__numbers');
      if (i === currentPage) pageNum.classList.add('active');
  
      pageNum.addEventListener('click', () => {
        currentPage = i;
        renderTable();
        renderPagination();
      });
  
      paginationContainer.appendChild(pageNum);
    }
  
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'next';
    nextBtn.classList.add('page__btn');
    if (currentPage < totalPages) {
      nextBtn.addEventListener('click', () => {
        currentPage++;
        renderTable();
        renderPagination();
      });
    } else {
      nextBtn.setAttribute('disabled', true);
    }
    paginationContainer.appendChild(nextBtn);
  }
  
    // BTC Dominance section
   
  
  
  const searchInput = document.getElementById("coinSearch");
  const searchBtn = document.getElementById("searchBtn");
  const filteredCoins = [];
  searchBtn.addEventListener("click", () => {
    const query = searchInput.value.trim().toLowerCase();
  
    filteredCoins = coins.filter(coin => {
      const name = coin.name?.toLowerCase() || "";
      const symbol = coin.symbol?.toLowerCase() || "";
      return name.includes(query) || symbol.includes(query);
    });
  
    currentPage = 1;
    renderTable();
    renderPagination();
  });
    // Exemple de graphique
  /* const ctx = document.getElementById('fundChart');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['2024-10', '2024-11', '2024-12', '2025-01'],
      datasets: [{
        label: 'Monthly Raise (M$)',
        data: [12, 18, 22, 16],
        backgroundColor: '#007bff'
      }]
    }
  }); */
  
  
  fetch('/api/topgainers/')
    .then(res => res.json())
    .then(async data => {
      const gainers = data.data.slice(0, 5); // ✅ fixed
      const list = document.getElementById('gainers-list');
  
      list.innerHTML = '<li>Loading...</li>';
  
      const gainerData = await Promise.all(
        gainers.map(async (coin) => {
          const coinKey = coin.key;
          const currentPrice = coin.price?.USD;
  
          try {
            const histRes = await fetch(`/api/gainers_loser_24h/?key=${coinKey}`);
            const histData = await histRes.json();
            const priceYesterday = histData.data?.[coinKey]?.histPrices?.["24H"]?.USD;
  
            let gainPercent = 0;
            if (priceYesterday && currentPrice) {
              gainPercent = ((currentPrice - priceYesterday) / priceYesterday) * 100;
            }
  
            return { coin, gainPercent };
          } catch (err) {
            console.error(`Error fetching hist data for ${coinKey}`, err);
            return { coin, gainPercent: 0 };
          }
        })
      );
  
      list.innerHTML = '';
      gainerData.forEach(({ coin, gainPercent }, i) => {
        const li = document.createElement('li');
        li.classList.add('gainer-item');
        li.innerHTML = `
          <div class="gainer-rank">${i + 1}</div>
          <img class="gainer-logo" src="${coin.image?.icon || coin.image}" alt="${coin.symbol}">
          <div class="gainer-info">
            <div><strong>${coin.name}</strong> <span class="symbol">${coin.symbol}</span></div>
            <div class="gainer-category">${coin.category?.name || '—'}</div>
          </div>
          <div class="gainer-change" style="color:green;">+${gainPercent.toFixed(1)}%</div>
        `;
        list.appendChild(li);
      });
    })
    .catch(err => {
      console.error('Failed to load gainers:', err);
      document.getElementById('gainers-list').innerHTML = '<li>Error loading data</li>';
    });
  
  
  
    fetch('/api/toplosers/')
    .then(res => res.json())
    .then(async data => {
      const losers = data.pageProps.fallbackData.slice(0, 5);
      const list = document.getElementById('losers-list');
  
      // Show loading state
      list.innerHTML = '<li>Loading...</li>';
  
      // Build an array of fetch promises
      const loserData = await Promise.all(
        losers.map(async (coin) => {
          const coinKey = coin.key;
          const currentPrice = coin.priceUsd || coin.price?.USD;
  
          try {
            const histRes = await fetch(`/api/gainers_loser_24h/?key=${coinKey}`);
            const histData = await histRes.json();
            const priceYesterday = histData.data?.[coinKey]?.histPrices?.["24H"]?.USD;
  
            let lossPercent = 0;
            if (priceYesterday && currentPrice) {
              lossPercent = ((currentPrice - priceYesterday) / priceYesterday) * 100;
            }
  
            return { coin, lossPercent };
          } catch (err) {
            console.error(`Error for ${coinKey}`, err);
            return { coin, lossPercent: 0 };
          }
        })
      );
  
      // Now that all are loaded, render them
      list.innerHTML = ''; // clear loading text
      loserData.forEach(({ coin, lossPercent }, i) => {
        const li = document.createElement('li');
        li.classList.add('loser-item');
        li.innerHTML = `
          <div class="loser-rank">${i + 1}</div>
          <img class="loser-logo" src="${coin.image}" alt="${coin.symbol}">
          <div class="loser-info">
            <div><strong>${coin.name}</strong> <span class="symbol">${coin.symbol}</span></div>
            <div class="loser-category">${coin.category?.name || '—'}</div>
          </div>
          <div class="loser-change" style="color:red;">${lossPercent.toFixed(1)}%</div>
        `;
        list.appendChild(li);
      });
    })
    .catch(err => {
      console.error('Failed to load losers:', err);
      document.getElementById('losers-list').innerHTML = '<li>Error loading data</li>';
    });
  
  
    const ctx = document.getElementById('btcDominanceChart').getContext('2d');
    const periodSelect = document.getElementById("period-select");
    const valueEl = document.getElementById("btc-dominance-value");
    const changeEl = document.getElementById("btc-dominance-change");
    let btcChart; // Global chart instance
  
    // Initial load
    fetchAndRenderChart(periodSelect.value || "7D");
  
    // Handle dropdown change
    periodSelect.addEventListener("change", () => {
      fetchAndRenderChart(periodSelect.value);
    });
  
    function fetchAndRenderChart(period) {
        const apiUrl = `/api/btc-dominance/?period=${period}`;
  
      fetch(apiUrl)
        .then(res => res.json())
        .then(json => {
          const timestamps = json.timestamps;
          const values = json.values;
  
          if (
            Array.isArray(timestamps) &&
            Array.isArray(values) &&
            timestamps.length === values.length
          ) {
            // Calculate change %
            const current = values[values.length - 1];
            const previous = values[values.length - 2];
            const change = ((current - previous) / previous) * 100;
            const sign = change >= 0 ? "+" : "";
            const direction = change >= 0 ? "↑" : "↓";
  
            valueEl.textContent = `${current.toFixed(2)}%`;
            changeEl.innerHTML = `${sign}${change.toFixed(2)}% <span class="arrow">${direction}</span>`;
            changeEl.style.color = change >= 0 ? "green" : "red";
  
            // Format labels (timestamps)
            const labels = timestamps.map(ts => new Date(ts));
  
            // Destroy old chart
            if (btcChart) btcChart.destroy();
  
            // Create new chart
            btcChart = new Chart(ctx, {
              type: 'line',
              data: {
                labels: labels,
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
                      callback: function (value) {
                        return value.toFixed(1) + "%";
                      },
                      color: "#aaa",
                      font: {
                        size: 10
                      },
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
        })
        .catch(err => {
          console.error('Error loading BTC dominance chart:', err);
        });
    }
   const slider = document.getElementById("featured-project-slider");
  let currentIndex = 0;
  let projects = [];
  
  function renderProject(index) {
  const proj = projects[index];
  
  const tag = proj.taskTypes?.[0] || '—';
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
  
  // Add navigation behavior to arrows and refresh
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
  
  
  function startSlider() {
    renderProject(currentIndex);
  
    setInterval(() => {
      currentIndex = (currentIndex + 1) % projects.length;
      renderProject(currentIndex);
    }, 30000); // 30 seconds
  }
  
  fetch('/api/featured-projects/') // change this to your proxy or real API
    .then(res => res.json())
    .then(data => {
      projects = data;
      if (projects.length > 0) startSlider();
      else slider.innerHTML = "<p>No projects found</p>";
    })
    .catch(err => {
      console.error("Failed to load projects:", err);
      slider.innerHTML = "<p>Error loading projects</p>";
    });
  });