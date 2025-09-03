import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
  const [topUsers, setTopUsers] = useState({ labels: [], datasets: [] });
  const [channels, setChannels] = useState({ labels: [], datasets: [] });
  const [flaggedUsers, setFlaggedUsers] = useState({ labels: [], datasets: [] });

  useEffect(() => {
    fetch("/api/top-users")
      .then(res => res.json())
      .then(data => setTopUsers({
        labels: data.map(d => d.author),
        datasets: [{ label: "Messages", data: data.map(d => d.count), backgroundColor: "rgba(75,192,192,0.6)" }]
      }));

    fetch("/api/messages-per-channel")
      .then(res => res.json())
      .then(data => setChannels({
        labels: data.map(d => d.channel),
        datasets: [{ label: "Messages", data: data.map(d => d.count), backgroundColor: "rgba(153,102,255,0.6)" }]
      }));

    fetch("/api/flagged-users")
      .then(res => res.json())
      .then(data => setFlaggedUsers({
        labels: data.map(d => d.author),
        datasets: [{ label: "Flagged Messages", data: data.map(d => d.count), backgroundColor: "rgba(255,99,132,0.6)" }]
      }));
  }, []);

  return (
    <div style={{ width: "800px", margin: "50px auto" }}>
      <h2>Top Active Users</h2>
      <Bar data={topUsers} />

      <h2>Messages per Channel</h2>
      <Bar data={channels} />

      <h2>Flagged Users</h2>
      <Bar data={flaggedUsers} />
    </div>
  );
}

export default App;
