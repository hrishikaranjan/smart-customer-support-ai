export default function Header({ title, subtitle, onMenuClick }) {
  return (
    <header className="top-header">
      <div className="top-header-left">
        <button className="icon-btn mobile-sidebar-toggle" onClick={onMenuClick} aria-label="Open menu">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
        </button>
        <div>
          <h1>{title}</h1>
          {subtitle && <div className="top-header-sub">{subtitle}</div>}
        </div>
      </div>
    </header>
  );
}
