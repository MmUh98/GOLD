import React, { useEffect } from "react";

const TickerTapeWidget = () => {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbols: [
        { proName: "OANDA:XAUUSD", title: "Gold Spot USD" },
        { proName: "OANDA:EURUSD", title: "EUR/USD" },
        { proName: "OANDA:USDJPY", title: "USD/JPY" },
      ],
      colorTheme: "dark",
      isTransparent: false,
      displayMode: "adaptive",
      locale: "en",
    });

    const container = document.getElementById("ticker-tape-container");
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
      <div id="ticker-tape-container" className="tradingview-widget-container__widget"></div>
    </div>
  );
};

export default TickerTapeWidget;
