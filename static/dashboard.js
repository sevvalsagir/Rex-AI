const socket = io();

// Chart setup
const ctx = document.getElementById('trafficChart').getContext('2d');
const ipCounts = {};
const chartData = {
  labels: [],
  datasets: [{
    label: 'Requests per IP',
    data: [],
    backgroundColor: 'rgba(0, 255, 200, 0.4)',
    borderColor: 'rgba(0, 255, 200, 1)',
    borderWidth: 1
  }]
};

const chart = new Chart(ctx, {
  type: 'bar',
  data: chartData,
  options: {
    responsive: true,
    animation: false,
    scales: {
      y: {
        beginAtZero: true,
        stepSize: 1
      }
    }
  }
});

socket.on('new_request', (req) => {
    const ip = req.ip;
    const time = req.timestamp;
    const url = req.url;
    const isAttack = req.is_attack;
  
    ipCounts[ip] = (ipCounts[ip] || 0) + 1;
  
    chartData.labels = Object.keys(ipCounts);
    chartData.datasets[0].data = Object.values(ipCounts);
    chart.update();
  
    const emoji = isAttack ? "🚨 ATTACK" : "✅ Normal";
    logQueue.unshift(`${time} — ${ip} → ${url} → ${emoji}`);
    if (logQueue.length > 5) logQueue.pop();
  
    logDiv.innerHTML = logQueue.map(entry => `<div class="latest-entry">${entry}</div>`).join('');
  });
  

// Latest request log
const logDiv = document.getElementById('request-log');
const logQueue = [];

socket.on('new_request', (req) => {
  const ip = req.ip;
  const time = req.timestamp;
  const url = req.url;

  // Update IP count
  ipCounts[ip] = (ipCounts[ip] || 0) + 1;

  chartData.labels = Object.keys(ipCounts);
  chartData.datasets[0].data = Object.values(ipCounts);
  chart.update();

  // Add to latest request log
  logQueue.unshift(`${time} — ${ip} → ${url}`);
  if (logQueue.length > 5) logQueue.pop();

  logDiv.innerHTML = logQueue.map(entry => `<div class="latest-entry">${entry}</div>`).join('');
});
