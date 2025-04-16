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
  const normalCtx = document.getElementById('normalChart').getContext('2d');

  // 🔴 Chart state'leri
  const attackCounts = {};
  const normalCounts = {};

  const attackChart = new Chart(attackCtx, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Attack Requests', data: [], backgroundColor: 'crimson' }] },
    options: { scales: { y: { beginAtZero: true } } }
  });

  const normalChart = new Chart(normalCtx, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Normal Requests', data: [], backgroundColor: 'mediumseagreen' }] },
    options: { scales: { y: { beginAtZero: true } } }
  });

  // 🧠 WebSocket bağlantı kontrol
  socket.on('connect', () => {
    console.log("🔗 Socket.IO connected to server.");
  });

  // 📩 Yeni istek geldiğinde
  socket.on("new_request", (req) => {
    console.log("📥 new_request received:", req);

    const { ip, url, timestamp, is_attack } = req;
    const emoji = is_attack ? "🚨 ATTACK" : "✅ NORMAL";
    const cssClass = is_attack ? "attack-entry" : "normal-entry";

    const entry = document.createElement("div");
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