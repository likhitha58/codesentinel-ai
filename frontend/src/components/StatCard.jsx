
function StatCard({ title, value, description, icon: Icon, tone }) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <span>{title}</span>
        <div className={`stat-icon ${tone}`}>
          <Icon size={19} />
        </div>
      </div>

      <div className="stat-value">{value}</div>
      <div className="stat-description">{description}</div>
    </div>
  );
}

export default StatCard;
