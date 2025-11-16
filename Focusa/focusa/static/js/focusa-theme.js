const focusaTheme = {
    colors: [
        "#2C70B8", // Azul principal
        "#7FAFDD", // Azul suave
        "#303570", // Azul oscuro
        "#FFC048", // Amarillo suave
        "#4CAF50", // Verde éxito
        "#E6455C"  // Rojo prioridad alta
    ],
    
    chart: {
      toolbar: { show: false },
      zoom: { enabled: false },
      foreColor: '#303570',
      fontFamily: "Open Sans, sans-serif",
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 650,
      },
    },

    dataLabels: { enabled: false },

    grid: {
      borderColor: '#E5E7EB',
      strokeDashArray: 4,
      padding: { top: 10, right: 10, bottom: 0, left: 8 },
    },

    stroke: { width: 3, curve: 'smooth' },

    legend: { show: false },

    xaxis: {
      labels: {
        style: {
          fontSize: '12px',
          fontWeight: 600,
          colors: '#6B7280'
        }
      },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },

    yaxis: {
      labels: {
        style: {
          fontSize: '12px',
          fontWeight: 600,
          colors: '#6B7280'
        }
      }
    },

    tooltip: {
      theme: 'light',
      style: { fontSize: '12px', fontFamily: 'Open Sans, sans-serif' }
    }
};

