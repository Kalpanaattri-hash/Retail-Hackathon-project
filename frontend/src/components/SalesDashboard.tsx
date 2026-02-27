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
  const [selectedDimensions, setSelectedDimensions] = useState<DashboardDimension[]>([
    'customer_gender',
    'customer_state',
    'product_category_name',
  ]);
  const [selectedGenders, setSelectedGenders] = useState<string[]>([]);
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
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

  const toggleDimension = (dimension: DashboardDimension) => {
    setSelectedDimensions((prev) => {
      if (prev.includes(dimension)) {
        if (prev.length === 1) return prev;
        return prev.filter((item) => item !== dimension);
      }
      return [...prev, dimension];
    });
  };

  const renderCheckboxList = (
    title: string,
    values: string[],
    selectedValues: string[],
    setSelectedValues: React.Dispatch<React.SetStateAction<string[]>>
  ) => (
    <div className="rounded-xl border border-slate-200 bg-white p-3">
      <p className="mb-2 text-sm font-semibold text-slate-800">{title}</p>
      <div className="max-h-28 space-y-1 overflow-y-auto pr-1 text-xs text-slate-700">
        {values.map((value) => (
          <label key={value} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={selectedValues.includes(value)}
              onChange={() => toggleStringFilter(setSelectedValues, value)}
            />
            <span>{value}</span>
          </label>
        ))}
      </div>
    </div>
  );

  if (bootLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-slate-50">
        <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div
      className={`h-full overflow-y-auto bg-slate-50 p-4 ${
        isChartsFullScreen ? 'fixed inset-4 z-50 rounded-2xl border border-slate-200 shadow-2xl' : ''
      }`}
    >
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
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
              className="rounded-lg border border-slate-300 p-2 text-slate-700 hover:bg-slate-100"
              aria-label={isChartsFullScreen ? 'Shrink dashboard' : 'Expand dashboard'}
              title={isChartsFullScreen ? 'Shrink dashboard' : 'Expand dashboard'}
            >
              {isChartsFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>
          </div>

          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <p className="mb-2 text-sm font-semibold text-slate-800">Dimensions (View By)</p>
              <div className="space-y-1 text-xs text-slate-700">
                {(Object.keys(dimensionLabel) as DashboardDimension[]).map((dimension) => (
                  <label key={dimension} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={selectedDimensions.includes(dimension)}
                      onChange={() => toggleDimension(dimension)}
                    />
                    <span>{dimensionLabel[dimension]}</span>
                  </label>
                ))}
              </div>
            </div>

            {renderCheckboxList(
              'Customer Gender',
              options?.customer_genders ?? [],
              selectedGenders,
              setSelectedGenders
            )}

            {renderCheckboxList(
              'Customer State',
              options?.customer_states ?? [],
              selectedStates,
              setSelectedStates
            )}
          </div>

          <div className="mt-3 grid gap-3 lg:grid-cols-2">
            {renderCheckboxList(
              'Product Category',
              options?.product_categories ?? [],
              selectedCategories,
              setSelectedCategories
            )}

            <div className="rounded-xl border border-slate-200 bg-white p-3">
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

        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className={`mb-3 flex items-center justify-end ${isChartsFullScreen ? 'sticky top-0 z-10 bg-white pb-2' : ''}`}>
            <button
              type="button"
              onClick={() => setIsChartsFullScreen((prev) => !prev)}
              className="rounded-lg border border-slate-300 p-2 text-slate-700 hover:bg-slate-100"
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
                <div key={chart.dimension} className="rounded-2xl border border-slate-200 bg-white p-3">
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
