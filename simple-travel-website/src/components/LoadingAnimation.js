const LoadingAnimation = ({
  title = "Finding your next stay...",
  subtitle = "Searching listings and matching your request.",
}) => (
  <div className="w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <div className="flex items-center gap-4">
      <div className="relative h-12 w-12">
        <div className="absolute inset-0 rounded-full border-4 border-slate-200" />
        <div className="absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-emerald-500" />
      </div>
      <div className="min-w-0">
        <p className="text-base font-semibold text-slate-900">{title}</p>
        <p className="text-sm text-slate-600">{subtitle}</p>
      </div>
    </div>
    <div className="mt-5 grid grid-cols-3 gap-3">
      <div className="h-2 animate-pulse rounded bg-slate-200" />
      <div className="h-2 animate-pulse rounded bg-slate-200" />
      <div className="h-2 animate-pulse rounded bg-slate-200" />
    </div>
  </div>
);

export default LoadingAnimation;
