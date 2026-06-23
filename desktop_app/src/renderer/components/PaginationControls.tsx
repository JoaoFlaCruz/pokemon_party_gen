export function PaginationControls({ page, totalPages, onPageChange }: { page: number; totalPages: number; onPageChange(page: number): void }) {
  return (
    <div className="pagination">
      <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
        Anterior
      </button>
      <span>
        Pagina {page} de {totalPages}
      </span>
      <button disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
        Proxima
      </button>
    </div>
  );
}
