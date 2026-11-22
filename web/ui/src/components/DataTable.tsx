import { useMemo, useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight, ChevronsUpDown, Search } from "lucide-react";
import type { DataTableInfo } from "../lib/types";
import { cn } from "../lib/utils";
import { Card } from "./ui";

export function DataTable({ table }: { table: DataTableInfo }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [query, setQuery] = useState("");

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return table.rows;
    return table.rows.filter((row) =>
      Object.values(row).some((value) => value.toLowerCase().includes(needle)),
    );
  }, [query, table.rows]);

  const columns = useMemo<ColumnDef<Record<string, string>>[]>(
    () =>
      table.columns.map((column) => ({
        accessorKey: column.key,
        header: column.label,
        cell: (context) => String(context.getValue() ?? ""),
      })),
    [table.columns],
  );

  const reactTable = useReactTable({
    data: rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 8 } },
  });

  return (
    <Card padded={false} className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">{table.label}</h2>
          <p className="mt-0.5 text-xs text-slate-500">
            {table.total} rows · click a header to sort
          </p>
        </div>
        <label className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter rows"
            className="form-control w-52 bg-slate-50 pl-8 focus:bg-white"
          />
        </label>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-xs">
          <thead className="bg-slate-50/80 text-3xs uppercase tracking-wider text-slate-500">
            {reactTable.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} className="whitespace-nowrap px-5 py-2.5 font-semibold">
                    <button
                      onClick={header.column.getToggleSortingHandler()}
                      className="inline-flex items-center gap-1 hover:text-slate-900"
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? (
                        <ArrowUp className="h-3 w-3" />
                      ) : header.column.getIsSorted() === "desc" ? (
                        <ArrowDown className="h-3 w-3" />
                      ) : (
                        <ChevronsUpDown className="h-3 w-3 opacity-40" />
                      )}
                    </button>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-slate-100">
            {reactTable.getRowModel().rows.map((row) => (
              <tr key={row.id} className="transition hover:bg-slate-50/70">
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className={cn(
                      "max-w-[380px] px-5 py-3 align-top leading-relaxed text-slate-700",
                      cell.column.id === "id" && "font-mono font-semibold text-slate-900",
                    )}
                  >
                    <div className="truncate" title={String(cell.getValue() ?? "")}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
            {!reactTable.getRowModel().rows.length && (
              <tr>
                <td colSpan={table.columns.length} className="px-5 py-10 text-center text-slate-400">
                  No matching rows.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-slate-100 px-5 py-3 text-2xs text-slate-500">
        <span>
          Page {reactTable.getState().pagination.pageIndex + 1} of {reactTable.getPageCount() || 1}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => reactTable.previousPage()}
            disabled={!reactTable.getCanPreviousPage()}
            className="content-icon-button border-slate-200 hover:bg-slate-50 disabled:opacity-40"
            aria-label="Previous page"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => reactTable.nextPage()}
            disabled={!reactTable.getCanNextPage()}
            className="content-icon-button border-slate-200 hover:bg-slate-50 disabled:opacity-40"
            aria-label="Next page"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </Card>
  );
}
