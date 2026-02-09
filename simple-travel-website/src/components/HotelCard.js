import { Bath, BedDouble, MessageSquare, Star, Users } from "lucide-react";
import { useMemo, useState } from "react";

const DESCRIPTION_LIMIT = 140;

const formatValue = (value, suffix = "") => {
  if (value === undefined || value === null || value === "") {
    return "N/A";
  }
  return `${value}${suffix}`;
};

const formatPrice = (value) => {
  if (value === undefined || value === null || value === "") {
    return "N/A";
  }
  const num = Number(value);
  if (Number.isNaN(num)) {
    return value;
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(num);
};

export default function HotelCard({ hotel }) {
  const [expandedDescription, setExpandedDescription] = useState(false);

  const stats = useMemo(
    () => [
      { label: "Bedrooms", value: formatValue(hotel.bedrooms), icon: BedDouble },
      { label: "Bathrooms", value: formatValue(hotel.bathrooms), icon: Bath },
      { label: "Beds", value: formatValue(hotel.beds), icon: BedDouble },
      { label: "Guests", value: formatValue(hotel.guests), icon: Users },
      {
        label: "Rating",
        value:
          hotel.stars !== undefined && hotel.stars !== null && hotel.stars !== ""
            ? Number(hotel.stars).toFixed(1)
            : "N/A",
        icon: Star,
      },
      { label: "Reviews", value: formatValue(hotel.reviewCount), icon: MessageSquare },
    ],
    [hotel]
  );

  const hasLongDescription = (hotel.description || "").length > DESCRIPTION_LIMIT;
  const shownDescription =
    expandedDescription || !hasLongDescription
      ? hotel.description
      : `${(hotel.description || "").slice(0, DESCRIPTION_LIMIT)}...`;

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md">
      <div className="grid grid-cols-1 md:grid-cols-[260px_1fr]">
        <img
          className="h-56 w-full object-cover md:h-full"
          src={hotel.imageUrl || "/beebrain.jpg"}
          alt={hotel.name || "Vacation rental"}
        />
        <div className="p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <a
              href={hotel.listingUrl}
              target="_blank"
              rel="noreferrer"
              className="text-xl font-semibold text-slate-900 hover:text-emerald-700"
            >
              {hotel.name}
            </a>
            <div className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">
              ${formatPrice(hotel.price)}
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
            {stats.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="rounded-xl border border-slate-200 bg-slate-50 p-2">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-slate-600" />
                    <span className="text-xs text-slate-600">{item.label}</span>
                  </div>
                  <div className="mt-1 text-sm font-semibold text-slate-900">{item.value}</div>
                </div>
              );
            })}
          </div>

          <p className="mt-4 text-sm leading-6 text-slate-600">
            {shownDescription || "No description available."}{" "}
            {hasLongDescription && (
              <button
                type="button"
                onClick={() => setExpandedDescription((current) => !current)}
                className="font-semibold text-emerald-700 hover:text-emerald-800"
              >
                {expandedDescription ? "See less" : "See more"}
              </button>
            )}
          </p>
        </div>
      </div>
    </article>
  );
}
