import React, { useEffect } from "react";

const GoldMiniChart = () => {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol: "OANDA:XAUUSD",
      width: "100%",
      height: 250,
      locale: "en",
      dateRange: "1D",
      colorTheme: "dark",
      isTransparent: false,
      autosize: true,
    });

    const container = document.getElementById("gold-mini-chart");
    if (container) {
      container.innerHTML = "";
      container.appendChild(script);
    }
    return () => {
      if (container) container.innerHTML = "";
    };
  }, []);

  return (
    <div className="tradingview-widget-container">
      <div id="gold-mini-chart" className="tradingview-widget-container__widget"></div>
    </div>
  );
};

export default GoldMiniChart;
