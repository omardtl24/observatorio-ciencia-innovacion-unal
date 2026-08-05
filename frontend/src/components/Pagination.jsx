function getPageNumbers(currentPage, totalPages) {
  const delta = 1;
  const range = [];

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
      range.push(i);
    }
  }

  const withGaps = [];
  let previous;
  for (const page of range) {
    if (previous !== undefined && page - previous > 1) {
      withGaps.push("...");
    }
    withGaps.push(page);
    previous = page;
  }

  return withGaps;
}

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  if (totalPages <= 1) {
    return null;
  }

  const pages = getPageNumbers(currentPage, totalPages);

  return (
    <div className="flex items-center justify-end gap-1 px-6 py-3 border-t border-gray-100 bg-gray-50">
      <button
        type="button"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-2 py-1 rounded-md text-xs font-semibold border border-gray-300 text-gray-600 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition"
        aria-label="Pagina anterior"
      >
        Anterior
      </button>

      {pages.map((page, index) =>
        page === "..." ? (
          <span key={`ellipsis-${index}`} className="px-2 text-xs text-gray-400">
            ...
          </span>
        ) : (
          <button
            type="button"
            key={page}
            onClick={() => onPageChange(page)}
            aria-current={page === currentPage ? "page" : undefined}
            className={`px-3 py-1 rounded-md text-xs font-semibold border transition ${
              page === currentPage
                ? "bg-secondary-cyan-strong text-white border-secondary-cyan-strong"
                : "border-gray-300 text-gray-600 hover:bg-white"
            }`}
          >
            {page}
          </button>
        )
      )}

      <button
        type="button"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-2 py-1 rounded-md text-xs font-semibold border border-gray-300 text-gray-600 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition"
        aria-label="Pagina siguiente"
      >
        Siguiente
      </button>
    </div>
  );
}
