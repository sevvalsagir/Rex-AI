// ✅ Garanti çalışan format: dashboard.js
// Bu dosya, Rex'in grafiklerini, loglarını ve harita heatmap'ini CANLI olarak günceller.

const socket = io();

// Tüm olayları DOM yüklendikten sonra bağla
document.addEventListener("DOMContentLoaded", () => {
  console.log("🟢 Dashboard JS loaded and DOM ready.");

  // 🟣 Log için DOM alanı
  const logDiv = document.getElementById("request-log");
  const logQueue = [];

  // 🔵 Chart.js contextleri
  const attackCtx = document.getElementById('attackChart').getContext('2d');

  // 🔴 Chart state'leri
  const attackCounts = {};
  const normalCounts = {};

  const attackChart = new Chart(attackCtx, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Attack Requests', data: [], backgroundColor: 'crimson' }] },
    options: { scales: { y: { beginAtZero: true } } }
  });

  const normalCtx = document.getElementById("normalChart").getContext("2d");
  const normalChart = new Chart(normalCtx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: "Normal Requests",
        data: [],
        backgroundColor: "#4caf50"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  function updateNormalRequestsChart() {
    fetch("/api/normal-requests")
      .then(res => res.json())
      .then(data => {
        normalChart.data.labels = data.labels;
        normalChart.data.datasets[0].data = data.counts;
        normalChart.update();
      });
  }

// Her 10 saniyede bir güncelle
updateNormalRequestsChart();
setInterval(updateNormalRequestsChart, 10000);


  // 🧠 WebSocket bağlantı kontrol
  socket.on('connect', () => {
    console.log("🔗 Socket.IO connected to server.");
  });

  // 📩 Yeni istek geldiğinde
  socket.on("new_request", (req) => {
    console.log("📥 new_request received:", req);

    const { ip, url, timestamp, is_attack, label } = req;
    const labelEmoji = label || (is_attack ? "🚨 ATTACK" : "✅ NORMAL");
    
    const entry = document.createElement("div");
    entry.className = `latest-entry ${is_attack ? "attack-entry" : "normal-entry"}`;
    entry.innerText = `${timestamp} — ${ip} → ${url} → ${labelEmoji}`;
    
    logDiv.prepend(entry);
    if (logDiv.children.length > 5) logDiv.removeChild(logDiv.lastChild);
    
    // 📊 Grafiğe IP ekle
    if (is_attack) {
      attackCounts[ip] = (attackCounts[ip] || 0) + 1;
      const idx = attackChart.data.labels.indexOf(ip);
      if (idx >= 0) {
        attackChart.data.datasets[0].data[idx] = attackCounts[ip];
      } else {
        attackChart.data.labels.push(ip);
        attackChart.data.datasets[0].data.push(attackCounts[ip]);
      }
      attackChart.update();
    } else {
      normalCounts[ip] = (normalCounts[ip] || 0) + 1;
      const idx = normalChart.data.labels.indexOf(ip);
      if (idx >= 0) {
        normalChart.data.datasets[0].data[idx] = normalCounts[ip];
      } else {
        normalChart.data.labels.push(ip);
        normalChart.data.datasets[0].data.push(normalCounts[ip]);
      }
      normalChart.update();
    }
     
    const cssClass = is_attack ? "attack-entry" : "normal-entry";

    entry.className = `latest-entry ${cssClass}`;
    entry.innerText = `${timestamp} — ${ip} → ${url} → ${emoji}`;

    logDiv.prepend(entry);
    if (logDiv.children.length > 5) logDiv.removeChild(logDiv.lastChild);

    const chart = is_attack ? attackChart : normalChart;
    const countMap = is_attack ? attackCounts : normalCounts;

    countMap[ip] = (countMap[ip] || 0) + 1;
    const labelIndex = chart.data.labels.indexOf(ip);
    if (labelIndex >= 0) {
      chart.data.datasets[0].data[labelIndex] = countMap[ip];
    } else {
      chart.data.labels.push(ip);
      chart.data.datasets[0].data.push(countMap[ip]);
    }
    chart.update();
  });

  const pieCtx = document.getElementById("labelPieChart").getContext("2d");
    const pieChart = new Chart(pieCtx, {
      type: "pie",
      data: {
        labels: [],
        datasets: [{
          label: "Saldırı Türü",
          data: [],
          backgroundColor: [
            "#00ffc8", // Normal
            "#ff5c5c", // DDoS
            "#ffa500", // Brute-force
            "#3399ff", // Port Scan
            "#cc66ff", // SQLi
            "#999999"  // Other
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" }
        }
      }
    });
  
    function updatePieChart() {
      fetch("/api/label-distribution")
        .then(res => res.json())
        .then(data => {
          pieChart.data.labels = data.labels;
          pieChart.data.datasets[0].data = data.counts;
          pieChart.update();
        });
    }
  
    updatePieChart();
    setInterval(updatePieChart, 10000);
  // 🌡️ Saatlik grafik
  const hourlyCtx = document.getElementById("hourlyChart").getContext("2d");
  const hourlyChart = new Chart(hourlyCtx, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Hourly Attacks', backgroundColor: 'crimson', data: [] }] },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });

  function updateHourlyChart() {
    fetch("/api/hourly-attack-data")
      .then(res => res.json())
      .then(data => {
        hourlyChart.data.labels = data.labels;
        hourlyChart.data.datasets[0].data = data.counts;
        hourlyChart.update();
      });
  }
  updateHourlyChart();
  setInterval(updateHourlyChart, 10000);
});

function retrainModel() {
  fetch("/retrain")
      .then(res => res.text())
      .then(html => {
          document.getElementById("retrain-status").innerHTML = html;
      })
      .catch(err => {
          document.getElementById("retrain-status").innerText = "❌ Hata oluştu.";
      });
}


const stackedCtx = document.getElementById("hourlyStackedChart").getContext("2d");
const stackedChart = new Chart(stackedCtx, {
  type: "bar",
  data: {
    labels: [],
    datasets: []
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: "bottom" }
    },
    scales: {
      x: { stacked: true },
      y: { stacked: true }
    }
  }
});



function updateHourlyStackedChart() {
  fetch("/api/hourly-stacked-data")
    .then(res => res.json())
    .then(data => {
      stackedChart.data.labels = data.labels;
      stackedChart.data.datasets = data.datasets;
      stackedChart.update();
    });
}

updateHourlyStackedChart();
setInterval(updateHourlyStackedChart, 10000);
