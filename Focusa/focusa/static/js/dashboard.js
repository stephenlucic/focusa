document.addEventListener('DOMContentLoaded', () => {
  const els = document.querySelectorAll('.focusa-chart');
  const sum = arr => arr.reduce((a, b) => a + b, 0);

  const makeOptions = (type, labels, series, stacked = false, height = 320) => {
    const base = {
      ...focusaTheme,
      chart: { ...focusaTheme.chart, type, height, toolbar: { show: false } },
      colors: focusaTheme.colors.slice(0, Math.max(series.length || 1, 1)),
      dataLabels: { enabled: false },
      grid: { strokeDashArray: 4 },
      legend: { position: 'top', horizontalAlign: 'right' }
    };

    if (type === 'area') {
      return {
        ...base,
        chart: { ...base.chart, stacked },
        stroke: { curve: 'smooth', width: 2 },
        series,
        xaxis: { ...focusaTheme.xaxis, categories: labels },
        fill: stacked
          ? { type: 'solid', opacity: 0.85 }
          : { type: 'gradient', gradient: { shadeIntensity: 0.5, opacityFrom: 0.9, opacityTo: 0.1, stops: [0,50,100] } }
      };
    }

    if (type === 'bar') {
      return {
        ...base,
        chart: { ...base.chart, stacked },
        series,
        xaxis: { ...focusaTheme.xaxis, categories: labels },
        plotOptions: {
          bar: { horizontal: false, columnWidth: '55%', borderRadius: 6, borderRadiusApplication: 'end' }
        },
        yaxis: { labels: { style: focusaTheme.xaxis.labels.style } }
      };
    }

    if (type === 'bar-horizontal') {
      return {
        ...base,
        chart: { ...base.chart, type: 'bar', stacked },
        series,
        xaxis: { categories: labels, labels: { style: focusaTheme.xaxis.labels.style } },
        plotOptions: {
          bar: { horizontal: true, barHeight: '60%', borderRadius: 6, borderRadiusApplication: 'end' }
        },
        dataLabels: { enabled: true, style: { colors: ['#fff'] } },
        tooltip: { theme: 'dark' }
      };
    }

    if (type === 'donut' || type === 'pie') {
      let pieLabels = labels;
      let pieSeries = series;
      if (Array.isArray(series) && typeof series[0] === 'object' && 'data' in series[0]) {
        pieLabels = series.map(s => s.name);
        pieSeries = series.map(s => sum(s.data));
      }
      return {
        ...base,
        chart: { ...base.chart, type },
        labels: pieLabels,
        series: pieSeries,
        legend: { position: 'bottom' }
      };
    }

    if (type === 'heatmap') {
      return {
        ...base,
        chart: { ...base.chart, type: 'heatmap' },
        series,
        plotOptions: {
          heatmap: {
            shadeIntensity: 0.5,
            colorScale: {
              ranges: [
                { from: 0, to: 10, color: focusaTheme.colors[2], name: 'Bajo' },
                { from: 11, to: 18, color: focusaTheme.colors[1], name: 'Medio' },
                { from: 19, to: 30, color: focusaTheme.colors[0], name: 'Alto' }
              ]
            }
          }
        },
        dataLabels: { enabled: true, style: { colors: ['#fff'] } }
      };
    }

    if (type === 'line') {
      return {
        ...base,
        stroke: { curve: 'smooth', width: 3 },
        series,
        xaxis: { ...focusaTheme.xaxis, categories: labels }
      };
    }

    // Fallback
    return { ...base, series, xaxis: { ...focusaTheme.xaxis, categories: labels } };
  };

  els.forEach(el => {
    const type = el.dataset.type || 'bar';
    const labels = JSON.parse(el.dataset.labels || '[]');
    const seriesRaw = el.dataset.series || '[]';
    let series;
    try { series = JSON.parse(seriesRaw); } catch { series = []; }
    const stacked = (el.dataset.stacked || 'false') === 'true';
    const height = parseInt(el.dataset.height || 320, 10);

    // Para donut/pie si series es simple array de números
    if ((type === 'donut' || type === 'pie') && Array.isArray(series)) {
      // si es solo números ya sirve; si es array de objetos con data se transforma dentro
    }

    const options = makeOptions(type, labels, series, stacked, height);
    new ApexCharts(el, options).render();
  });
});