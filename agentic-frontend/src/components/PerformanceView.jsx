import { useEffect, useRef } from 'react'
import Highcharts from 'highcharts'

function PerformanceView({ data }) {
  const chartRef = useRef(null)

  console.log('PerformanceView received data:', data)

  useEffect(() => {
    if (data?.chart_data && chartRef.current) {
      console.log('Rendering chart with data:', data.chart_data)
      Highcharts.chart(chartRef.current, data.chart_data)
    }
  }, [data])

  if (!data) {
    return <div>No data available</div>
  }

  if (!data.metrics) {
    return <div>Invalid data structure: {JSON.stringify(Object.keys(data))}</div>
  }

  const { performance_table, account_table, chart_data, narrative } = data

  return (
    <div className="performance-view">
      <h2>📊 Performance Summary</h2>

      {/* Table 1: Household Performance */}
      {performance_table && (
        <div className="performance-table-section">
          <h3>Household Performance vs. S&P 500 Benchmark</h3>
          <table className="performance-table">
            <thead>
              <tr>
                <th></th>
                {performance_table.periods.map((period, i) => (
                  <th key={i}>{period}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Portfolio (Net of Fees)</strong></td>
                {performance_table.portfolio.map((val, i) => (
                  <td key={i} className={val && val >= 0 ? 'positive' : 'negative'}>
                    {val !== null && val !== undefined ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}%` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td><strong>S&P 500 Index</strong></td>
                {performance_table.benchmark.map((val, i) => (
                  <td key={i}>
                    {val !== null && val !== undefined ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}%` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td><strong>+/- vs Benchmark</strong></td>
                {performance_table.portfolio.map((pVal, i) => {
                  const bVal = performance_table.benchmark[i]
                  if (pVal === null || pVal === undefined || bVal === null || bVal === undefined) {
                    return <td key={i}>—</td>
                  }
                  const diff = pVal - bVal
                  return (
                    <td key={i} className={diff >= 0 ? 'positive' : 'negative'}>
                      {diff >= 0 ? '+' : ''}{diff.toFixed(2)}%
                    </td>
                  )
                })}}
              </tr>
            </tbody>
          </table>
          <p className="table-note">
            Returns for periods greater than one year are annualized. Net of advisory fees. 
            Benchmark: S&P 500 Total Return Index. ITD = Inception to Date.
          </p>
        </div>
      )}

      {/* Table 2: Performance by Account */}
      {account_table && (
        <div className="performance-table-section">
          <h3>Performance by Account</h3>
          <table className="performance-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Type</th>
                <th>Mkt Value</th>
                <th>QTD</th>
                <th>YTD</th>
                <th>Benchmark</th>
              </tr>
            </thead>
            <tbody>
              {account_table.accounts.map((acc, i) => (
                <tr key={i}>
                  <td><strong>{acc.name}</strong></td>
                  <td>{acc.type}</td>
                  <td>${acc.value.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</td>
                  <td className={acc.qtd >= 0 ? 'positive' : 'negative'}>
                    {acc.qtd >= 0 ? '+' : ''}{acc.qtd.toFixed(2)}%
                  </td>
                  <td className={acc.ytd >= 0 ? 'positive' : 'negative'}>
                    {acc.ytd >= 0 ? '+' : ''}{acc.ytd.toFixed(2)}%
                  </td>
                  <td>{acc.benchmark}</td>
                </tr>
              ))}
              <tr className="total-row">
                <td><strong>Total</strong></td>
                <td></td>
                <td><strong>${account_table.accounts.reduce((sum, acc) => sum + acc.value, 0).toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</strong></td>
                <td><strong>{account_table.accounts[0]?.qtd >= 0 ? '+' : ''}{account_table.accounts[0]?.qtd.toFixed(2)}%</strong></td>
                <td><strong>{account_table.accounts[0]?.ytd >= 0 ? '+' : ''}{account_table.accounts[0]?.ytd.toFixed(2)}%</strong></td>
                <td></td>
              </tr>
            </tbody>
          </table>
          <p className="table-note">
            Market values as of {new Date().toLocaleDateString('en-US', {month: 'long', day: 'numeric', year: 'numeric'})}. Returns are net of fees.
          </p>
        </div>
      )}

      {/* Chart */}
      {chart_data && (
        <div className="chart-container">
          <div ref={chartRef} style={{ width: '100%', height: '400px' }}></div>
        </div>
      )}

      {/* Narrative */}
      {narrative && (
        <div className="narrative">
          <h3>Summary</h3>
          <p>{narrative}</p>
        </div>
      )}

      <div className="actions">
        <button className="btn-download">📥 Download PDF</button>
        <button className="btn-export">📊 Export Data</button>
      </div>
    </div>
  )
}

export default PerformanceView
