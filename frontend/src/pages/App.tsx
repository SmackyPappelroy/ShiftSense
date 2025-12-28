import { useEffect, useState } from 'react'
import { fetchWorkspaces, fetchFindings } from '../api/client'

const menuItems = ['Workspaces', 'Imports', 'Dashboards', 'Findings', 'Reports', 'Settings']

export default function App() {
  const [workspaces, setWorkspaces] = useState<string[]>([])
  const [findings, setFindings] = useState<string[]>([])

  useEffect(() => {
    fetchWorkspaces()
      .then(setWorkspaces)
      .catch(() => setWorkspaces(['Demo Workspace']))
    fetchFindings()
      .then(setFindings)
      .catch(() => setFindings(['Ingen data ännu']))
  }, [])

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>ShiftSense</h1>
        <nav>
          {menuItems.map((item) => (
            <button key={item} className="nav-button">
              {item}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">
        <section className="panel">
          <h2>Dashboard KPI</h2>
          <div className="kpi-grid">
            <div className="kpi-card">
              <p>Cykeltid P95</p>
              <strong>18.4 s</strong>
            </div>
            <div className="kpi-card">
              <p>Energi per cykel</p>
              <strong>1.2 kWh</strong>
            </div>
            <div className="kpi-card">
              <p>Alarm per timme</p>
              <strong>6.3</strong>
            </div>
            <div className="kpi-card">
              <p>Stoppminuter</p>
              <strong>42 min</strong>
            </div>
          </div>
        </section>
        <section className="panel">
          <h2>Workspaces</h2>
          <ul>
            {workspaces.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </section>
        <section className="panel">
          <h2>Senaste findings</h2>
          <ul>
            {findings.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  )
}
