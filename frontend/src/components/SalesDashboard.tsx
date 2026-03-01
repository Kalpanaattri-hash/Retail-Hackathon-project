import { useEffect, useMemo, useState } from 'react';
import { Loader2, Maximize2, Minimize2 } from 'lucide-react';
import {
  apiClient,
  type DashboardChart,
  type DashboardDimension,
  type DashboardMeasure,
  type DashboardOptionsResponse,
} from '../api';

const dimensionLabel: Record<DashboardDimension, string> = {
  customer_gender: 'Customer Gender',
  customer_state: 'Customer State',
  product_category_name: 'Product Category',
};

export const SalesDashboard: React.FC = () => {
  const [options, setOptions] = useState<DashboardOptionsResponse | null>(null);
  const [charts, setCharts] = useState<DashboardChart[]>([]);
  const [measure, setMeasure] = useState<DashboardMeasure>('sales_value');
  const selectedDimensions: DashboardDimension[] = useMemo(
    () => ['customer_gender', 'customer_state', 'product_category_name'],
    []
  );
  const [selectedGenders, setSelectedGenders] = useState<string[]>([]);
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [isDimensionsOpen, setIsDimensionsOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<'gender' | 'state' | 'category' | null>(null);
  const [loading, setLoading] = useState(false);
  const [bootLoading, setBootLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isChartsFullScreen, setIsChartsFullScreen] = useState(false);

  const hasFilters = useMemo(
    () => selectedGenders.length > 0 || selectedStates.length > 0 || selectedCategories.length > 0,
    [selectedCategories.length, selectedGenders.length, selectedStates.length]
  );

  useEffect(() => {
    const initialize = async () => {
      setBootLoading(true);
      setError(null);
      try {
        const response = await apiClient.getDashboardOptions();
        setOptions(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard options');
      } finally {
        setBootLoading(false);
      }
    };

    initialize();
  }, []);

  useEffect(() => {
    if (!options) return;

    const loadCharts = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.getDashboardCharts({
          customer_genders: selectedGenders,
          customer_states: selectedStates,
          product_categories: selectedCategories,
          selected_dimensions: selectedDimensions,
          measure,
        });
        setCharts(response.charts);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard charts');
        setCharts([]);
      } finally {
        setLoading(false);
      }
    };

    loadCharts();
  }, [measure, options, selectedCategories, selectedDimensions, selectedGenders, selectedStates]);

  const toggleStringFilter = (
    setSelected: React.Dispatch<React.SetStateAction<string[]>>,
    value: string
  ) => {
    setSelected((prev) =>
      prev.includes(value) ? prev.filter((entry) => entry !== value) : [...prev, value]
    );
  };

  const renderDropdownFilter = (
    keyName: 'gender' | 'state' | 'category',
    title: string,
    values: string[],
    selectedValues: string[],
    setSelectedValues: React.Dispatch<React.SetStateAction<string[]>>
  ) => {
    const isOpen = openDropdown === keyName;

    return (
      <div className="rounded-xl border border-slate-200 bg-white">
        <button
          type="button"
          onClick={() => setOpenDropdown((prev) => (prev === keyName ? null : keyName))}
          className="flex w-full items-center justify-between px-3 py-2 text-left"
        >
          <div>
            <p className="text-sm font-semibold text-slate-800">{title}</p>
            <p className="text-xs text-slate-500">
              {selectedValues.length > 0 ? `${selectedValues.length} selected` : 'No selection'}
            </p>
          </div>
          <span className={`text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}>⌄</span>
        </button>

        {isOpen && (
          <div className="max-h-48 space-y-1 overflow-y-auto border-t border-slate-200 px-3 py-2 text-xs text-slate-700">
            {values.length > 0 ? (
              values.map((value) => (
                <label key={value} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(value)}
                    onChange={() => toggleStringFilter(setSelectedValues, value)}
                  />
                  <span>{value}</span>
                </label>
              ))
            ) : (
              <p className="py-1 text-slate-500">No options available</p>
            )}
          </div>
        )}
      </div>
    );
  };

  if (bootLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-slate-50">
        <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div
      className={`h-full overflow-y-auto bg-slate-100/70 p-4 ${
        isChartsFullScreen ? 'fixed inset-4 z-50 rounded-2xl border border-slate-300 bg-slate-100 shadow-2xl' : ''
      }`}
    >
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-300 bg-gradient-to-br from-white via-indigo-50/40 to-slate-50 p-4 shadow-sm">
          <div className="mb-1 flex items-start justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Dynamic Sales Dashboard</h3>
              <p className="text-sm text-slate-600">
                Filter by dimensions and choose a measure to update charts dynamically.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setIsChartsFullScreen((prev) => !prev)}
              className="rounded-lg border border-slate-300 bg-white/80 p-2 text-slate-700 hover:bg-indigo-50"
              aria-label={isChartsFullScreen ? 'Shrink dashboard' : 'Expand dashboard'}
              title={isChartsFullScreen ? 'Shrink dashboard' : 'Expand dashboard'}
            >
              {isChartsFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>
          </div>

          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-300 bg-slate-50/70 p-3">
              <button
                type="button"
                onClick={() => setIsDimensionsOpen((prev) => !prev)}
                className="flex w-full items-center justify-between rounded-lg border border-slate-300 bg-white/80 px-3 py-2 text-left"
              >
                <div>
                  <p className="text-sm font-semibold text-slate-800">Dimensions</p>
                  <p className="text-xs text-slate-500">Click to choose Gender, State and Product Category</p>
                </div>
                <span className={`text-slate-500 transition-transform ${isDimensionsOpen ? 'rotate-180' : ''}`}>
                  ⌄
                </span>
              </button>

              {isDimensionsOpen && (
                <div className="mt-3 space-y-2">
                  {renderDropdownFilter(
                    'gender',
                    dimensionLabel.customer_gender,
                    options?.customer_genders ?? [],
                    selectedGenders,
                    setSelectedGenders
                  )}
                  {renderDropdownFilter(
                    'state',
                    dimensionLabel.customer_state,
                    options?.customer_states ?? [],
                    selectedStates,
                    setSelectedStates
                  )}
                  {renderDropdownFilter(
                    'category',
                    dimensionLabel.product_category_name,
                    options?.product_categories ?? [],
                    selectedCategories,
                    setSelectedCategories
                  )}
                </div>
              )}
            </div>

            <div className="rounded-xl border border-slate-300 bg-slate-50/70 p-3">
              <p className="mb-2 text-sm font-semibold text-slate-800">Measures</p>
              <div className="space-y-2 text-sm text-slate-700">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="measure"
                    checked={measure === 'sales_value'}
                    onChange={() => setMeasure('sales_value')}
                  />
                  <span>Sales Value</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="measure"
                    checked={measure === 'sales_quantity'}
                    onChange={() => setMeasure('sales_quantity')}
                  />
                  <span>Sales Quantity</span>
                </label>
              </div>
              <p className="mt-3 text-xs text-slate-500">
                {hasFilters ? 'Filters applied' : 'No filters applied (showing full dataset)'}
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-300 bg-gradient-to-br from-white to-slate-50 p-4 shadow-sm">
          <div className={`mb-3 flex items-center justify-end ${isChartsFullScreen ? 'sticky top-0 z-10 bg-white pb-2' : ''}`}>
            <button
              type="button"
              onClick={() => setIsChartsFullScreen((prev) => !prev)}
              className="rounded-lg border border-slate-300 bg-white/80 p-2 text-slate-700 hover:bg-indigo-50"
              aria-label={isChartsFullScreen ? 'Shrink dashboard' : 'Expand dashboard'}
              title={isChartsFullScreen ? 'Shrink dashboard' : 'Expand dashboard'}
            >
              {isChartsFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
            </div>
          ) : charts.length > 0 ? (
            <div className="grid gap-4 lg:grid-cols-2">
              {charts.map((chart) => (
                <div key={chart.dimension} className="rounded-2xl border border-slate-300 bg-white/90 p-3 shadow-sm">
                  <p className="mb-2 text-sm font-semibold text-slate-800">{chart.title}</p>
                  <img
                    src={`data:image/png;base64,${chart.image_base64}`}
                    alt={chart.title}
                    className="w-full rounded-lg border border-slate-200"
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="py-14 text-center text-slate-500">No chart data available for selected filters.</div>
          )}
        </div>

        {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      </div>
    </div>
  );
};
