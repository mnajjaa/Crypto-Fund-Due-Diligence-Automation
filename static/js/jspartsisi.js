


fetch("/firstPage/api/launchpads-roi/")
  .then(res => res.json())
  .then(data => {
    if (!Array.isArray(data)) {
      console.error("Launchpad ROI data malformed:", data);
      return;
    }

    const topLaunchpads = data
      .sort((a, b) => b.currentRoiPercent - a.currentRoiPercent)
      .slice(0, 10);

    const labels = topLaunchpads.map(p => p.name);
    const roiData = topLaunchpads.map(p => p.currentRoiPercent);
    const barColors = roiData.map(v => v >= 0 ? '#00c49f' : '#ff5c5c');

    const iconImages = topLaunchpads.map(p => {
      const img = new Image();
      img.src = p.icon;
      return img;
    });

    const canvas = document.getElementById("launchpadChart");
    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'ROI',
          data: roiData,
          backgroundColor: barColors,
          borderRadius: 5,
          barThickness: 24
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 70 // ✅ ensures enough space for icons + text
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              callback: val => `${val}%`,
              font: { size: 12 }
            },
            grid: { color: '#eee' }
          },
          y: {
            ticks: {
              font: { size: 14 },
              padding: 10
            },
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => {
                const value = ctx.dataset.data[ctx.dataIndex];
                return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
              }
            }
          }
        }
      },
      plugins: [{
        id: "drawLaunchpadIcons",
        beforeDraw(chart) {
          const yAxis = chart.scales.y;
          const ctx = chart.ctx;

          topLaunchpads.forEach((p, i) => {
            const y = yAxis.getPixelForTick(i) - 12;
            const x = yAxis.left - 45;

            const icon = iconImages[i];
            ctx.drawImage(icon, x, y, 24, 24);
          });
        }
      }]
    });
  })
  .catch(err => console.error("Launchpad ROI chart error:", err));

  



 


  fetch("/firstPage/api/market-state/")
  .then(res => res.json())
  .then(data => {
    const rawGroups = data?.data?.children || [];
    const chartData = [];
    const categories = [];

    // Process the data into categories and coins
    rawGroups.forEach((group, i) => {
      const groupId = `group-${i}`;
      categories.push({ id: groupId, name: group.name });

      (group.children || []).forEach(coin => {
        const change = parseFloat(coin.percent) || 0;
        chartData.push({
          name: coin.name,
          parent: groupId,
          value: coin.value,
          price: coin.price,
          change,
          colorValue: change
        });
      });
    });

    let categoryLabels = [];

    Highcharts.chart('marketStateChartHighcharts', {
      chart: {
        type: 'treemap',
        backgroundColor: '#f5f5f5',
        style: {
          fontFamily: 'Poppins, sans-serif'
        },
        events: {
          render: function () {
            const chart = this;
            categoryLabels.forEach(l => l.destroy());
            categoryLabels = [];

            const cats = chart.series[0].data.filter(d => d.id && d.name && !d.parent);
            cats.forEach(category => {
              const node = category.node;
              if (!node) return;
              const x = node.x + 6;
              const y = node.y + 5;
              const label = chart.renderer.text(category.name, x, y)
                .css({
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#333'
                })
                .add();
              categoryLabels.push(label);
            });
          }
        }
      },

      title: { text: '' },

      credits: {
        enabled: false
      },

      colorAxis: {
        min: -10,
        max: 10,
        stops: [
          [0, '#ff6f61'],
          [0.5, '#e0e0e0'],
          [1, '#66bb6a']
        ],
        labels: {
          format: '{value}%'
        },
        minColor: '#ff6f61',
        maxColor: '#66bb6a'
      },

      tooltip: {
        useHTML: true,
        formatter: function () {
          return `
            <div style="padding:8px;font-size:13px;font-family:Poppins;">
              <strong>${this.point.name}</strong><br/>
              Market Cap: $${(this.point.value / 1e9).toFixed(2)}B<br/>
              Price: $${this.point.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}<br/>
              24H Change: ${this.point.change >= 0 ? '+' : ''}${this.point.change.toFixed(2)}%
            </div>
          `;
        }
      },

      plotOptions: {
        treemap: {
          layoutAlgorithm: 'squarified',
          borderColor: '#ffffff',
          borderWidth: 3, // Increased for more spacing
          pointPadding: 3, // Increased for more spacing between tiles
          levels: [
            {
              level: 1, // Category level
              dataLabels: {
                enabled: false
              }
            },
            {
              level: 2, // Coin level
              dataLabels: {
                enabled: true,
                useHTML: true,
                align: 'center',
                verticalAlign: 'middle',
                style: {
                  textOutline: 'none',
                  fontWeight: '500'
                },
                formatter: function () {
                  const area = this.point.node?.val || 0;
                  const name = this.point.name || '';
                  const price = this.point.price || 0;
                  const change = this.point.change || 0;
                  const sign = change >= 0 ? '+' : '';
                  const changeText = `${sign}${change.toFixed(2)}%`;
                  const priceText = `$${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

                  const fontColor = '#333';
                  const minFontSize = 8; // Reduced for smaller tiles
                  const maxFontSize = 14; // Reduced for better proportionality
                  const areaThreshold = 1000000; // Increased to hide text in smaller tiles

                  if (area < areaThreshold) return '';

                  const fontSize = Math.min(maxFontSize, minFontSize + Math.round(area * 0.00003)); // Adjusted scaling factor

                  return `
                    <div style="text-align:center; line-height:1.2;">
                      <div style="font-size:${fontSize}px; font-weight:600; color:${fontColor};">${name}</div>
                      <div style="font-size:${fontSize - 2}px; color:${change >= 0 ? '#4caf50' : '#f44336'};">${changeText}</div>
                      <div style="font-size:${fontSize - 2}px; color:${fontColor};">${priceText}</div>
                    </div>`;
                }
              }
            }
          ]
        }
      },

      series: [{
        type: 'treemap',
        layoutAlgorithm: 'squarified',
        allowDrillToNode: false,
        colorKey: 'colorValue',
        data: [...categories, ...chartData]
      }]
    });
  })
  .catch(err => console.error("Market state chart error:", err));







document.addEventListener("DOMContentLoaded", function () {
  // Function to render coins
  function renderCoins(containerId, coins) {
    const container = document.getElementById(containerId);
    if (!container) return; // Prevent null errors
    
    container.innerHTML = coins.map(coin => {
      // Ensure price is valid before using toFixed()
      const price = coin.price ?? 0; // Use 0 if price is null or undefined
      const change = coin.priceChange24h ?? 0; // Ensure priceChange24h is not undefined
      const isPositive = change > 0;
      const changeClass = isPositive ? 'positive' : 'negative';
      const formattedChange = `${isPositive ? '+' : ''}${change.toFixed(2)}%`;
  
      return `
        <li>
          <img src="${coin.icon}" alt="${coin.name}" />
          <div>
            <div class="coin-name">${coin.name}</div>
            <div class="coin-price">$ ${price.toFixed(4)}</div>
            <div class="coin-change ${changeClass}">${formattedChange}</div>
          </div>
        </li>`;
    }).join('');
  }
  
  // Tab Switching
  document.getElementById("trendingTab").addEventListener("click", () => {
    document.getElementById("trendingCoinsList").style.display = "flex";
    document.getElementById("recentCoinsList").style.display = "none";
    toggleActiveTab("trending");
  });

  document.getElementById("recentTab").addEventListener("click", () => {
    document.getElementById("trendingCoinsList").style.display = "none";
    document.getElementById("recentCoinsList").style.display = "flex";
    toggleActiveTab("recent");
  });

  function toggleActiveTab(tab) {
    document.getElementById("trendingTab").classList.toggle("active-tab", tab === "trending");
    document.getElementById("trendingTab").classList.toggle("inactive-tab", tab !== "trending");
    document.getElementById("recentTab").classList.toggle("active-tab", tab === "recent");
    document.getElementById("recentTab").classList.toggle("inactive-tab", tab !== "recent");
  }

  // Fetch Trending Coins
  fetch("/firstPage/api/trending-coins/")
    .then(res => res.json())
    .then(data => renderCoins("trendingCoinsList", data?.data || []));

  // Fetch Recently Listed
  fetch("/firstPage/api/recently-listed/")
    .then(res => res.json())
    .then(data => {
      console.log("Recently Listed Data:", data);  // log the data
      renderCoins("recentCoinsList", data?.data || []);
    });
});





document.addEventListener("DOMContentLoaded", function () {
  // Fetch Latest Insights and Reports
  fetch("/firstPage/api/articles/") // Replace with your actual Django view URL
    .then(res => res.json())
    .then(data => {
      const insightsContainer = document.querySelector('.insights-container');
      let articles = data.data;

      // Log the number of articles fetched
      console.log(`Fetched ${articles.length} articles`);

      // Ensure a minimum of 10 articles to trigger scrolling
      const minArticles = 10;
      if (articles.length < minArticles) {
        const repeatCount = Math.ceil(minArticles / articles.length);
        articles = Array(repeatCount).fill(articles).flat().slice(0, minArticles);
        console.log(`Expanded to ${articles.length} articles to ensure scrolling`);
      }

      // Clear the container before adding articles
      insightsContainer.innerHTML = '';

      // Add articles to the container
      articles.forEach(article => {
        const articleCard = `
          <div class="insight-card">
            <img src="${article.leadImage}" alt="${article.title}" class="insight-image" />
            <div class="insight-info">
              <h3><a href="https://cryptorank.io/articles/${article.slug}" class="article-title">${article.title}</a></h3>
              <div class="tags">
                ${article.tags.map(tag => `<span>${tag.name}</span>`).join('')}
              </div>
              <p class="author-info">
                <span>${new Date(article.date).toLocaleDateString()} | ${article.readingTimeMinutes.toFixed(1)} min read</span>
              </p>
            </div>
          </div>`;
        insightsContainer.innerHTML += articleCard;
      });
    })
    .catch(error => {
      console.error("Error fetching articles:", error);
      // Fallback: Add placeholder articles if the API fails
      const insightsContainer = document.querySelector('.insights-container');
      insightsContainer.innerHTML = '';
      for (let i = 1; i <= 10; i++) {
        const articleCard = `
          <div class="insight-card">
            <img src="https://via.placeholder.com/240x110" alt="Placeholder ${i}" class="insight-image" />
            <div class="insight-info">
              <h3><a href="#" class="article-title">Placeholder Article ${i}</a></h3>
              <div class="tags">
                <span>Tag ${i}</span><span>Tag ${i + 1}</span>
              </div>
              <p class="author-info">
                <span>${new Date().toLocaleDateString()} | 5.0 min read</span>
              </p>
            </div>
          </div>`;
        insightsContainer.innerHTML += articleCard;
      }
    });
});





document.addEventListener("DOMContentLoaded", function () {
  // Fetch 24h BTC Futures Volumes
  fetch("/firstPage/api/futures-exchange-volumes/") // Replace this with your actual Django view URL
    .then(res => res.json())
    .then(data => {
      if (!Array.isArray(data.data)) {
        console.error("Futures volume data malformed:", data);
        return;
      }

      // Get the top 10 exchanges sorted by volume
      const topExchanges = data.data.slice(0, 10);

      const exchangeNames = topExchanges.map(exchange => exchange.exchangeName);
      const volumes = topExchanges.map(exchange => exchange.volume);
      const exchangeIcons = topExchanges.map(exchange => exchange.exchangeIcon);

      // Get the canvas element for the chart
      const canvas = document.getElementById("futuresVolumeChart");
      const ctx = canvas.getContext("2d");

      // Helper function to format numbers into billions with $number+B format
      function formatVolume(volume) {
        const volumeInBillions = volume / 1e9;
        return `$${volumeInBillions.toFixed(1)}B`; // Format with one decimal place and 'B' for billions
      }

      // Set up the chart
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: exchangeNames,
          datasets: [{
            label: "24h Volume",
            data: volumes,
            backgroundColor: "#7db6f3", // Custom color for bars
            borderRadius: 5,
            barThickness: 24
          }]
        },
        options: {
          indexAxis: "y", // Horizontal bar chart
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              left: 70 // To leave space for icons and text
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              ticks: {
                callback: function (val) {
                  return formatVolume(val); // Format volume as $number+B
                },
                font: { size: 12 }
              },
              grid: { color: "#eee" }
            },
            y: {
              ticks: {
                font: { size: 14 },
                padding: 10
              },
              grid: { display: false }
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const value = context.dataset.data[context.dataIndex];
                  return formatVolume(value); // Format volume as $number+B
                }
              }
            }
          }
        },
        plugins: [{
          id: "drawExchangeIcons",
          beforeDraw(chart) {
            const yAxis = chart.scales.y;
            const ctx = chart.ctx;

            topExchanges.forEach((exchange, index) => {
              const y = yAxis.getPixelForTick(index) - 12;
              const x = yAxis.left - 45;

              const icon = new Image();
              icon.src = exchangeIcons[index];
              icon.onload = () => {
                ctx.drawImage(icon, x, y, 24, 24);
              };
            });
          }
        }]
      });
    })
    .catch(err => {
      console.error("Error fetching futures volume data:", err);
    });
});





document.addEventListener("DOMContentLoaded", function () {
  // Fetch 24h BTC Futures Open Interest
  fetch("/firstPage/api/futures-open-interest/") // Replace with your actual API endpoint
    .then(res => res.json())
    .then(data => {
      if (!Array.isArray(data.data)) {
        console.error("Futures open interest data malformed:", data);
        return;
      }

      // Prepare the data for the Futures Open Interest
      const interestData = data.data.map(exchange => ({
        name: exchange.exchangeName,
        interest: exchange.interest
      }));

      // Prepare the chart data for Futures Open Interest
      const labels = interestData.map(item => item.name);
      const interestValues = interestData.map(item => item.interest);

      // Display the chart
      const ctx = document.getElementById("futuresInterestChart").getContext("2d");

      new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "BTC Futures Open Interest",
            data: interestValues,
            backgroundColor: "#424961", // Blue color
            borderRadius: 8,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              display: false, // Hides the x-axis labels (exchange names)
            },
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return `$${(value / 1e9).toFixed(1)}B`; // Display values in billions
                },
                font: {
                  size: 12
                }
              },
              grid: {
                display: false
              }
            }
          },
          plugins: {
            legend: {
              display: false // Hides the legend
            },
            tooltip: {
              callbacks: {
                label: function(tooltipItem) {
                  const value = tooltipItem.raw;
                  return `$${(value / 1e9).toFixed(1)}B`; // Display tooltip in billions
                }
              }
            }
          }
        }
      });
    })
    .catch(err => {
      console.error("Error fetching futures open interest data:", err);
    });
});




fetch('/firstPage/api/new-ath/')
  .then(response => response.json())
  .then(data => {
    const athContainer = document.getElementById('new-ath-cards');

    if (data.error || !Array.isArray(data)) {
      athContainer.innerHTML = '<p>No ATH data available.</p>';
      return;
    }

    // Create two divs for the two columns
    const columnLeft = document.createElement('div');
    const columnRight = document.createElement('div');
    columnLeft.classList.add('ath-column');
    columnRight.classList.add('ath-column');

    // Loop through the data and create cards dynamically
    data.forEach((item, index) => {
      const card = document.createElement('div');
      card.classList.add('ath-card');

      // Map API data to the required format
      const name = item.name || 'Unknown';
      const symbol = item.symbol || '';
      const image = item.image || 'path/to/default-icon.png'; // Fallback image if none provided
      const currentPrice = item.price?.USD || 0;
      const athPrice = item.athPrice?.USD || 0;

      // Recalculate the percentage change
      let change = 0;
      if (currentPrice && athPrice && athPrice !== 0) {
        change = ((currentPrice - athPrice) / athPrice) * 100;
        change = parseFloat(change.toFixed(2)); // Round to 2 decimal places
      }

      // Format price to match the image (e.g., $3.25K for thousands)
      let formattedPrice = currentPrice;
      if (currentPrice >= 1000) {
        formattedPrice = `${(currentPrice / 1000).toFixed(2)}K`;
      } else if (currentPrice < 1) {
        formattedPrice = currentPrice.toFixed(4);
      } else {
        formattedPrice = currentPrice.toFixed(2);
      }

      card.innerHTML = `
        <img src="${image}" alt="${name}" class="ath-card-img" />
        <div class="ath-card-info">
          <h4 class="ath-name">${name} <span class="ath-symbol">${symbol}</span></h4>
          <div class="ath-price-change">
            <span class="ath-price">$${formattedPrice}</span>
            <span class="ath-change ${change >= 0 ? 'green' : 'red'}">${change >= 0 ? '+' : ''}${change}%</span>
          </div>
        </div>
      `;

      // Add the card to the appropriate column
      if (index < 3) {
        columnLeft.appendChild(card); // First 3 items in the left column
      } else {
        columnRight.appendChild(card); // Next 3 items in the right column
      }
    });

    // Append the columns to the container
    athContainer.appendChild(columnLeft);
    athContainer.appendChild(columnRight);
  })
  .catch(error => {
    const athContainer = document.getElementById('new-ath-cards');
    athContainer.innerHTML = '<p>Error loading ATH data.</p>';
    console.error('Error fetching ATH data:', error);
  });






  fetch('/firstPage/api/new-ath/')
  .then(response => response.json())
  .then(data => {
    const atlContainer = document.getElementById('new-atl-cards');

    if (data.error || !Array.isArray(data)) {
      atlContainer.innerHTML = '<p>No ATL data available.</p>';
      return;
    }

    // Create two divs for the two columns
    const columnLeft = document.createElement('div');
    const columnRight = document.createElement('div');
    columnLeft.classList.add('atl-column');
    columnRight.classList.add('atl-column');

    // Loop through the data and create cards dynamically
    data.forEach((item, index) => {
      const card = document.createElement('div');
      card.classList.add('atl-card');

      // Map API data to the required format
      const name = item.name || 'Unknown';
      const symbol = item.symbol || '';
      const image = item.image || 'path/to/default-icon.png'; // Fallback image if none provided
      const currentPrice = item.price?.USD || 0;
      const atlPrice = item.atlPrice?.USD || 0;

      // Calculate the percentage change relative to ATL price
      let change = 0;
      if (currentPrice && atlPrice && atlPrice !== 0) {
        change = ((currentPrice - atlPrice) / atlPrice) * 100;
        change = parseFloat(change.toFixed(2)); // Round to 2 decimal places
      }

      // Format price to match the style (e.g., $3.25K for thousands)
      let formattedPrice = currentPrice;
      if (currentPrice >= 1000) {
        formattedPrice = `${(currentPrice / 1000).toFixed(2)}K`;
      } else if (currentPrice < 1) {
        formattedPrice = currentPrice.toFixed(4);
      } else {
        formattedPrice = currentPrice.toFixed(2);
      }

      card.innerHTML = `
        <img src="${image}" alt="${name}" class="atl-card-img" />
        <div class="atl-card-info">
          <h4 class="atl-name">${name} <span class="atl-symbol">${symbol}</span></h4>
          <div class="atl-price-change">
            <span class="atl-price">$${formattedPrice}</span>
            <span class="atl-change ${change >= 0 ? 'green' : 'red'}">${change >= 0 ? '+' : ''}${change}%</span>
          </div>
        </div>
      `;

      // Add the card to the appropriate column
      if (index < 3) {
        columnLeft.appendChild(card); // First 3 items in the left column
      } else {
        columnRight.appendChild(card); // Next 3 items in the right column
      }
    });

    // Append the columns to the container
    atlContainer.appendChild(columnLeft);
    atlContainer.appendChild(columnRight);
  })
  .catch(error => {
    const atlContainer = document.getElementById('new-atl-cards');
    atlContainer.innerHTML = '<p>Error loading ATL data.</p>';
    console.error('Error fetching ATL data:', error);
  });












