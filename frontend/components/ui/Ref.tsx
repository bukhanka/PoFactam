import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// ... existing imports and code ...

function AIChatHistory() {
  // ... existing code ...

  // Register the required components for the bar chart
  ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

  // Prepare data for the bar chart
  const barChartData = {
    labels: ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5'],
    datasets: [
      {
        label: 'Sample Data',
        data: [12, 19, 3, 5, 2],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Bar Chart Example',
      },
    },
  };

  return (
    <div>
      {/* ... existing chart component ... */}
      
      <div style={{ width: '500px', height: '300px', margin: '20px auto' }}>
        <Bar data={barChartData} options={barChartOptions} />
      </div>
    </div>
  );
}

// ... rest of the existing code ...