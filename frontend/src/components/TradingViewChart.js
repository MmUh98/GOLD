import { useEffect, useRef } from "react";

// TradingView Advanced Chart Widget wrapper
// No extra npm package needed; we load the official tv.js script and instantiate the widget.
export default function TradingViewChart({
  symbol = "OANDA:XAUUSD", // Spot Gold by default (remove futures GC1!)
  interval = "D",        // Default 1D
  theme = "dark",
  height = 600
}) {
  const containerRef = useRef(null);
  const containerId = "tradingview_advanced_chart";

  useEffect(() => {
    function createWidget() {
      if (!window.TradingView || !containerRef.current) return;
      // Clear any previous render
      containerRef.current.innerHTML = "";
      /* global TradingView */
      new window.TradingView.widget({
        container_id: containerId,
        symbol,
        interval,
        timezone: "Etc/UTC",
        theme,
        style: "1", // standard
        withdateranges: true,
        hide_side_toolbar: false,
        allow_symbol_change: true,
        details: true,
        hotlist: false,
        calendar: true,
        autosize: true,
        locale: "en",
        // Show volume pane
        studies: ["Volume@tv-basicstudies"],
        // Keep core header tools (indicators, compare, fullscreen)
        enabled_features: [
          "header_indicators",
          "header_compare",
          "header_fullscreen_button"
        ],
        disabled_features: [],
        // Official host
        support_host: "https://www.tradingview.com"
      });
    }

    if (window.TradingView && window.TradingView.widget) {
      createWidget();
      return;
    }
    // Load script once
    const scriptId = "tradingview-widget-script";
    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.type = "text/javascript";
      script.async = true;
      script.src = "https://s3.tradingview.com/tv.js";
      script.onload = createWidget;
      document.body.appendChild(script);
    } else {
      // If script tag exists but widget not ready yet, attach a small delay
      const t = setTimeout(createWidget, 300);
      return () => clearTimeout(t);
    }
    return () => {
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [symbol, interval, theme]);

  return (
    <div
      ref={containerRef}
      id={containerId}
      style={{ width: "100%", height, borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 16px rgba(0,0,0,0.35)" }}
    />
  );
}
