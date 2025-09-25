import React, { useEffect } from "react";

const GoldPriceWidget = () => {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol: "OANDA:XAUUSD",
      width: 350,
      colorTheme: "dark",
      isTransparent: false,
      locale: "en",
    });

    const container = document.getElementById("gold-widget-container");
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
      <div id="gold-widget-container" className="tradingview-widget-container__widget"></div>
    </div>
  );
};

export default GoldPriceWidget;
