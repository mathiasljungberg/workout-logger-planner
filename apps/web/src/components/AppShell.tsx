import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/calendar", label: "Calendar" },
  { to: "/templates", label: "Templates" },
  { to: "/blocks", label: "Blocks" },
  { to: "/analytics", label: "Analytics" },
  { to: "/settings", label: "Settings" },
];

export function AppShell() {
  return (
    <div className="shell">
      <aside className="shell__sidebar">
        <div>
          <p className="eyebrow">Workout Tracker</p>
          <h1>Plan, log, review.</h1>
        </div>
        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav__link ${isActive ? "nav__link--active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="shell__content">
        <Outlet />
      </main>
      <nav className="mobile-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `mobile-nav__link ${isActive ? "mobile-nav__link--active" : ""}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

