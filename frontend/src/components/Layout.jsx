import { NavLink, Outlet } from 'react-router-dom'

function Layout() {
  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <span className="brand-mark">EIS</span>
          <div className="brand-text">
            <h1>EIS Marks</h1>
            <p className="brand-tag">Class 6 results</p>
          </div>
        </div>
        <nav>
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? 'nav-link active' : 'nav-link'
            }
          >
            Students
          </NavLink>
          <NavLink
            to="/summary"
            className={({ isActive }) =>
              isActive ? 'nav-link active' : 'nav-link'
            }
          >
            Summary
          </NavLink>
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
