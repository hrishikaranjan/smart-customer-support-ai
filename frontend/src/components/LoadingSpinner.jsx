export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="spinner-page">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  );
}
