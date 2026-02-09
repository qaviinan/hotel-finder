import Head from 'next/head';
import { useEffect, useState } from 'react';
import { Search, Star } from 'lucide-react';
import HotelCard from '../components/HotelCard';
import LoadingAnimation from '../components/LoadingAnimation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";
const SUGGESTED_QUERIES = [
  'I want a 2 bed, 1 bath place under $250',
  'Show me rentals for 4 guests with strong reviews',
  'Find a private room with wifi and kitchen',
];

export default function Hotels() {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [hotelsPerPage] = useState(10);
  const [filters, setFilters] = useState([]);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');

  // Function to fetch hotels
  const fetchHotels = async (userInput) => {
    setLoading(true);
    setErrorMessage('');
    setCurrentPage(1);
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            query: userInput
        })
      });
      const data = await response.json();
      if (!response.ok) {
        setErrorMessage(data?.error?.message || 'Search failed. Please try again.');
      }
      setHotels((data.listings || []).map(item => ({
        id: item.idStr,
        imageUrl: item.image_url,
        listingUrl: item.url,
        name: item.name,
        description: item.description,
        stars: item.stars,
        price: item.price,
        bedrooms: item.bedroom_count,
        bathrooms: item.bathroom_count,
        beds: item.bed_count,
        guests: item.guest_capacity,
        reviewCount: item.review_count,
        city: item.city,
        roomType: item.room_type,
    })));
      setFilters(data.filters || []);
    } catch (error) {
      console.error('Error:', error);
      setHotels([]);
      setFilters([]);
      setErrorMessage('Backend unavailable. Make sure the backend is running on port 8001.');
    } finally {
      setLoading(false);
    }
  };

  // useEffect to handle the initial API call
  useEffect(() => {
    fetchHotels("firstcall");
  }, []);

  useEffect(() => {
    if (search.trim()) return;
    const intervalId = setInterval(() => {
      setPlaceholderIndex((current) => (current + 1) % SUGGESTED_QUERIES.length);
    }, 3500);
    return () => clearInterval(intervalId);
  }, [search]);

  // Handle search input changes
  const handleInputChange = (e) => {
    setSearch(e.target.value);
  };

  // Handle form submission
  const handleSearch = (e) => {
    e.preventDefault();
    fetchHotels(search.trim() || "firstcall");
  };

  // Pagination logic
  const indexOfLastHotel = currentPage * hotelsPerPage;
  const indexOfFirstHotel = indexOfLastHotel - hotelsPerPage;
  const currentHotels = hotels.slice(indexOfFirstHotel, indexOfLastHotel);
  const paginate = pageNumber => setCurrentPage(pageNumber);

  return (
    <>
      <Head>
        <title>Hotels in Bangkok</title>
      </Head>
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 px-4 py-8">
        <div className="mx-auto w-full max-w-6xl">
          <header className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2 text-emerald-700">
              <Star className="h-5 w-5" />
              <span className="text-sm font-semibold uppercase tracking-wider">Natural Search</span>
            </div>
            <h1 className="mt-2 text-3xl font-bold text-slate-900">Bangkok Vacation Rental Explorer</h1>
            <p className="mt-2 text-slate-600">
              Sort through vacation rentals in Bangkok with natural language.
            </p>
          </header>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <form onSubmit={handleSearch} className="flex w-full items-center gap-2">
              <div className="relative flex-grow">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder={SUGGESTED_QUERIES[placeholderIndex]}
                  className="w-full rounded-xl border border-slate-300 bg-slate-50 py-3 pl-10 pr-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:outline-none"
                  value={search}
                  onChange={handleInputChange}
                />
              </div>
              <button type="submit" className="rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-700">
                Search
              </button>
            </form>
            {filters.length > 0 && (
                <div className='mt-4 flex flex-wrap gap-2'>
                    {filters.map((filter, index) => (
                        <span key={index} id={`badge-dismiss-${index}`} className="inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800">
                            {filter}
                        </span>
                    ))}
                </div>
            )}
          </div>

          <section className="mt-6 space-y-4">
            {loading ? (
              <div className="flex justify-center py-8">
                <LoadingAnimation
                  title="Searching stays in Bangkok..."
                  subtitle="Matching your query against current listings."
                />
              </div>
            ) : currentHotels.length === 0 ? (
              <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
                <p className="text-lg font-semibold text-slate-900">No listings matched this search</p>
                <p className="mt-2 text-sm text-slate-600">
                  {errorMessage || "Try relaxing one constraint (price, rooms, or amenities) and search again."}
                </p>
              </div>
            ) : (
              <>
                {errorMessage && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                    {errorMessage}
                  </div>
                )}
                {currentHotels.map(hotel => (
                  <HotelCard key={hotel.id} hotel={hotel} />
                ))}
              </>
            )}
          </section>

          {hotels.length > hotelsPerPage && (
            <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
              <button
                onClick={() => paginate(currentPage - 1)}
                disabled={currentPage === 1}
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              {Array.from({ length: Math.ceil(hotels.length / hotelsPerPage) }, (_, index) => (
                <button
                  key={index + 1}
                  onClick={() => paginate(index + 1)}
                  className={`rounded-lg px-3 py-2 text-sm ${
                    index + 1 === currentPage
                      ? 'bg-emerald-600 text-white'
                      : 'border border-slate-300 bg-white text-slate-700'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
              <button
                onClick={() => paginate(currentPage + 1)}
                disabled={currentPage === Math.ceil(hotels.length / hotelsPerPage)}
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
