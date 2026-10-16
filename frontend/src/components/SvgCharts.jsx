import React, { useState } from 'react';
import { formatINR, formatNumber } from '../services/api';

/**
 * Responsive Pure SVG Line + Area Trend Chart for Daily Volume & Value
 */
export function LineAreaTrendChart({ data = [], metricKey = 'tx_count', label = 'Transactions', height = 240, isCurrency = false }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  const validData = (data || []).filter(d => d && (d.tx_count > 0 || d.tx_value > 0 || d.avg_amount > 0));

  if (!validData || validData.length === 0) {
    return (
      <div className="chart-empty-state" style={{ minHeight: height }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>📈</div>
        <div className="chart-empty-state-title">No Trend Data Available</div>
        <div className="chart-empty-state-desc">
          Upload a transaction CSV dataset to visualize throughput and volume growth.
        </div>
      </div>
    );
  }

  const padding = { top: 20, right: 24, bottom: 35, left: 60 };
  const width = 800; // Scalable vector box
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const values = validData.map(d => Number(d[metricKey]) || 0);
  const maxVal = Math.max(...values, 1) * 1.15; // 15% headroom
  const minVal = 0;

  const points = validData.map((d, i) => {
    const x = padding.left + (i / Math.max(validData.length - 1, 1)) * innerWidth;
    const y = padding.top + innerHeight - ((Number(d[metricKey]) || 0) / maxVal) * innerHeight;
    return { x, y, data: d };
  });

  const pathD = points.reduce((acc, p, i) => {
    return i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
  }, '');

  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length - 1].x} ${padding.top + innerHeight} L ${points[0].x} ${padding.top + innerHeight} Z`
    : '';

  // Generate 4 horizontal grid lines
  const gridLines = [0, 0.33, 0.66, 1].map((pct) => {
    const y = padding.top + innerHeight - pct * innerHeight;
    const val = minVal + pct * (maxVal - minVal);
    return { y, val };
  });

  return (
    <div style={{ position: 'relative', width: '100%', height }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: '100%', overflow: 'visible' }}
        onMouseLeave={() => setHoverIndex(null)}
      >
        <defs>
          <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8A63F4" stopOpacity="0.32" />
            <stop offset="100%" stopColor="#8A63F4" stopOpacity="0.01" />
          </linearGradient>
        </defs>

        {/* Horizontal grid lines & Y labels */}
        {gridLines.map((g, idx) => (
          <g key={idx}>
            <line
              x1={padding.left}
              y1={g.y}
              x2={width - padding.right}
              y2={g.y}
              stroke="#ECE8E5"
              strokeDasharray="4 4"
            />
            <text
              x={padding.left - 10}
              y={g.y + 4}
              textAnchor="end"
              fontSize="12"
              fill="#77736F"
              fontFamily="var(--font-mono)"
            >
              {isCurrency ? `₹${(g.val / 1000).toFixed(0)}k` : formatNumber(Math.round(g.val))}
            </text>
          </g>
        ))}

        {/* Filled gradient area */}
        {areaD && <path d={areaD} fill="url(#trendGradient)" />}

        {/* Line path */}
        {pathD && (
          <path
            d={pathD}
            fill="none"
            stroke="#8A63F4"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Interactive points */}
        {points.map((p, i) => (
          <g key={i}>
            <circle
              cx={p.x}
              cy={p.y}
              r={hoverIndex === i ? 6 : 3.5}
              fill={hoverIndex === i ? '#8A63F4' : '#FFFFFF'}
              stroke="#8A63F4"
              strokeWidth="2.5"
              style={{ transition: 'all 0.15s ease' }}
            />
            {/* Invisible larger hit target */}
            <circle
              cx={p.x}
              cy={p.y}
              r={16}
              fill="transparent"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setHoverIndex(i)}
            />
            {/* X-axis labels */}
            {(i === 0 || i === Math.floor(points.length / 2) || i === points.length - 1) && (
              <text
                x={p.x}
                y={height - 8}
                textAnchor="middle"
                fontSize="12.5"
                fill="#77736F"
                fontWeight="600"
              >
                {p.data.tx_date ? p.data.tx_date.slice(5) : ''}
              </text>
            )}
          </g>
        ))}
      </svg>

      {/* Hover Tooltip */}
      {hoverIndex !== null && points[hoverIndex] && (
        <div
          style={{
            position: 'absolute',
            left: `${(points[hoverIndex].x / width) * 100}%`,
            top: `${Math.max(10, points[hoverIndex].y - 48)}px`,
            transform: 'translate(-50%, -100%)',
            background: '#20201F',
            color: '#FFFFFF',
            padding: '8px 14px',
            borderRadius: 8,
            fontSize: 13,
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
            zIndex: 10
          }}
        >
          <div style={{ fontWeight: 600, fontSize: 12.5, color: '#B9A0F5', marginBottom: 2 }}>
            {points[hoverIndex].data.tx_date}
          </div>
          <div>
            {label}:{' '}
            <strong className="mono">
              {isCurrency
                ? formatINR(points[hoverIndex].data[metricKey])
                : formatNumber(points[hoverIndex].data[metricKey])}
            </strong>
          </div>
          {points[hoverIndex].data.rolling_3day_avg && (
            <div style={{ fontSize: 12, color: '#A49F9B', marginTop: 2 }}>
              3-Day Avg: {formatNumber(points[hoverIndex].data.rolling_3day_avg)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * 24-Hour Diurnal Activity Bar Chart with Peak Hour Highlight
 */
export function BarHourlyChart({ data = [], height = 200 }) {
  const [hoverHour, setHoverHour] = useState(null);

  const hasAnyTx = (data || []).some(d => Number(d.tx_count || 0) > 0);

  if (!hasAnyTx) {
    return (
      <div className="chart-empty-state" style={{ minHeight: height }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>🕒</div>
        <div className="chart-empty-state-title">No Hourly Activity Recorded</div>
        <div className="chart-empty-state-desc">
          Upload a transaction CSV to compute 24-hour diurnal volume distribution.
        </div>
      </div>
    );
  }

  // Ensure full 24 hours (0..23) are represented
  const fullHours = Array.from({ length: 24 }, (_, h) => {
    const match = (data || []).find(d => Number(d.tx_hour) === h);
    return (
      match || {
        tx_hour: h,
        tx_count: 0,
        tx_value: 0,
        avg_amount: 0,
        volume_share_pct: 0
      }
    );
  });

  const maxCount = Math.max(...fullHours.map(h => Number(h.tx_count) || 0), 1);
  const peakHourItem = fullHours.reduce((prev, curr) => (curr.tx_count > prev.tx_count ? curr : prev), fullHours[0]);

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', height, gap: 5, paddingBottom: 28, paddingTop: 10 }}>
        {fullHours.map((item) => {
          const count = Number(item.tx_count) || 0;
          const barHeightPct = (count / maxCount) * 100;
          const isPeak = item.tx_hour === peakHourItem.tx_hour && count > 0;
          const isHovered = hoverHour === item.tx_hour;

          return (
            <div
              key={item.tx_hour}
              style={{
                flex: 1,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'flex-end',
                alignItems: 'center',
                cursor: 'pointer',
                position: 'relative'
              }}
              onMouseEnter={() => setHoverHour(item.tx_hour)}
              onMouseLeave={() => setHoverHour(null)}
            >
              {/* Bar */}
              <div
                style={{
                  width: '100%',
                  height: `${Math.max(barHeightPct, 4)}%`,
                  backgroundColor: isPeak
                    ? '#8A63F4'
                    : isHovered
                    ? '#A180F8'
                    : '#D6C7FB',
                  borderRadius: '4px 4px 1px 1px',
                  transition: 'all 0.15s ease'
                }}
              />
              {/* X-axis hour tick */}
              {(item.tx_hour % 4 === 0 || item.tx_hour === 23) && (
                <div
                  style={{
                    position: 'absolute',
                    bottom: -24,
                    fontSize: 12,
                    fontWeight: isPeak ? 700 : 500,
                    color: isPeak ? '#8A63F4' : '#77736F'
                  }}
                >
                  {item.tx_hour}h
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Tooltip */}
      {hoverHour !== null && fullHours[hoverHour] && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            right: 0,
            background: '#20201F',
            color: '#FFFFFF',
            padding: '8px 14px',
            borderRadius: 8,
            fontSize: 13,
            boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
            zIndex: 10
          }}
        >
          <strong>{hoverHour}:00 - {hoverHour}:59</strong>
          <div style={{ marginTop: 2 }}>
            Volume: <span className="mono">{formatNumber(fullHours[hoverHour].tx_count)}</span> txns ({fullHours[hoverHour].volume_share_pct}%)
          </div>
          <div>
            Value: <span className="mono">{formatINR(fullHours[hoverHour].tx_value)}</span>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Category Breakdown with Horizontal Distribution Bars & Share %
 */
export function CategoryDistributionBars({ data = [] }) {
  const validData = (data || []).filter(d => Number(d.tx_count || 0) > 0 || Number(d.tx_value || 0) > 0);

  if (!validData || validData.length === 0) {
    return (
      <div className="chart-empty-state">
        <div style={{ fontSize: 32, marginBottom: 8 }}>🏷️</div>
        <div className="chart-empty-state-title">No Category Data Available</div>
        <div className="chart-empty-state-desc">
          Upload a transaction CSV to observe volume by merchant category.
        </div>
      </div>
    );
  }

  const maxValue = Math.max(...validData.map(d => Number(d.tx_value) || 0), 1);

  const colors = [
    '#8A63F4', '#A180F8', '#B9A0F5', '#CBB9F7',
    '#7E57C2', '#5E35B1', '#9575CD', '#B39DDB'
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {validData.map((cat, idx) => {
        const val = Number(cat.tx_value) || 0;
        const widthPct = (val / maxValue) * 100;
        const color = colors[idx % colors.length];

        return (
          <div key={cat.category} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 14.5 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: color }} />
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{cat.category}</span>
                <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                  ({formatNumber(cat.tx_count)} txns)
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <strong className="mono" style={{ fontSize: 14.5, color: 'var(--text-main)' }}>{formatINR(val)}</strong>
                <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--primary)', minWidth: 44, textAlign: 'right' }}>
                  {cat.value_share_pct}%
                </span>
              </div>
            </div>
            {/* Progress track */}
            <div style={{ width: '100%', height: 8, backgroundColor: '#FAF6F2', borderRadius: 6, overflow: 'hidden', border: '1px solid #ECE8E5' }}>
              <div
                style={{
                  width: `${widthPct}%`,
                  height: '100%',
                  backgroundColor: color,
                  borderRadius: 6,
                  transition: 'width 0.4s ease'
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
