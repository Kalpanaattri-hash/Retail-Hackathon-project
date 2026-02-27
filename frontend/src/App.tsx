import { useState, type ComponentType } from 'react';
import {
  BarChart3,
  Bot,
  ChevronRight,
  MessageCircle,
  Palette,
  ShoppingCart,
  Sparkles,
} from 'lucide-react';
import { ChatBox } from './components/ChatBox';
import './index.css';

type FeatureKey = 'sales-analytics' | 'social-media' | 'recommendations' | 'visual-styling';

function App() {
  const [activeFeature, setActiveFeature] = useState<FeatureKey>('sales-analytics');
  const [isSalesExpanded, setIsSalesExpanded] = useState(true);
  const [selectedSalesTab, setSelectedSalesTab] = useState<'qna-chatbot' | 'sales-analytic'>(
    'qna-chatbot'
  );

  const featureItems: Array<{
    key: FeatureKey;
    title: string;
    icon: ComponentType<{ className?: string }>;
    badge?: string;
  }> = [
    { key: 'sales-analytics', title: 'Sales Analytics', icon: BarChart3 },
    { key: 'social-media', title: 'Social Media Analytics', icon: MessageCircle, badge: 'Soon' },
    {
      key: 'recommendations',
      title: 'Personalized Recommendations',
      icon: ShoppingCart,
      badge: 'Soon',
    },
    { key: 'visual-styling', title: 'Visual AI Styling', icon: Palette, badge: 'Soon' },
  ];

  const getHeaderTitle = () => {
    if (activeFeature === 'sales-analytics') {
      return selectedSalesTab === 'qna-chatbot'
        ? 'Sales Analytics · QnA Chatbot'
        : 'Sales Analytics · Sales Analytic';
    }

    return featureItems.find((item) => item.key === activeFeature)?.title ?? 'Retail Intelligence Platform';
  };

  return (
    <div className="relative flex h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(79,70,229,0.22),transparent_38%),radial-gradient(circle_at_70%_100%,rgba(30,64,175,0.2),transparent_45%)]" />

      <aside className="relative z-10 w-80 border-r border-slate-700/60 bg-slate-900/80 p-5 backdrop-blur-xl">
        <div className="rounded-2xl border border-slate-700/50 bg-slate-900/70 p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 p-2.5 shadow-lg shadow-indigo-500/25">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">EComm Alchemy</p>
              <h1 className="text-lg font-semibold text-white">AI Intelligence Hub</h1>
            </div>
          </div>
        </div>

        <nav className="mt-5 space-y-3">
          {featureItems.map((item) => {
            const Icon = item.icon;
            const isSalesAnalytics = item.key === 'sales-analytics';
            const isActive = activeFeature === item.key;

            return (
              <div
                key={item.key}
                className={`rounded-2xl border p-3 ${
                  isActive
                    ? 'border-indigo-400/40 bg-indigo-500/10 shadow-lg shadow-indigo-900/25'
                    : 'border-slate-700/50 bg-slate-900/60'
                }`}
              >
                <button
                  type="button"
                  onClick={() => {
                    if (isSalesAnalytics) {
                      setActiveFeature('sales-analytics');
                      setIsSalesExpanded((prev) => !prev);
                      return;
                    }

                    setActiveFeature(item.key);
                  }}
                  className="flex w-full items-center justify-between"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <div
                      className={`rounded-lg p-2 ${
                        isActive ? 'bg-indigo-500/30 text-indigo-100' : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                    </div>
                    <p className={`text-left text-sm ${isActive ? 'font-semibold text-white' : 'text-slate-300'}`}>
                      {item.title}
                    </p>
                  </div>
                  {isSalesAnalytics ? (
                    <ChevronRight
                      className={`h-4 w-4 text-indigo-200 transition-transform ${isSalesExpanded ? 'rotate-90' : ''}`}
                    />
                  ) : (
                    item.badge && (
                      <span className="rounded-full border border-slate-600 px-2 py-0.5 text-[10px] uppercase tracking-wide text-slate-300">
                        {item.badge}
                      </span>
                    )
                  )}
                </button>

                {isSalesAnalytics && isSalesExpanded && (
                  <ul className="mt-3 ml-11 space-y-2 text-sm list-disc text-indigo-100/90">
                    <li className="list-none">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveFeature('sales-analytics');
                          setSelectedSalesTab('qna-chatbot');
                        }}
                        className={`w-full rounded-xl border px-3 py-2 text-left text-sm transition-colors ${
                          selectedSalesTab === 'qna-chatbot'
                            ? 'border-indigo-400/50 bg-indigo-500/20 font-semibold text-white'
                            : 'border-slate-700/60 bg-slate-900/60 text-slate-200 hover:border-slate-500 hover:text-white'
                        }`}
                      >
                        QnA Chatbot
                      </button>
                    </li>
                    <li className="list-none">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveFeature('sales-analytics');
                          setSelectedSalesTab('sales-analytic');
                        }}
                        className={`w-full rounded-xl border px-3 py-2 text-left text-sm transition-colors ${
                          selectedSalesTab === 'sales-analytic'
                            ? 'border-indigo-400/50 bg-indigo-500/20 font-semibold text-white'
                            : 'border-slate-700/60 bg-slate-900/60 text-slate-200 hover:border-slate-500 hover:text-white'
                        }`}
                      >
                        Sales Dashboard
                      </button>
                    </li>
                  </ul>
                )}
              </div>
            );
          })}
        </nav>
      </aside>

      <main className="relative z-10 flex min-h-0 flex-1 flex-col p-5">
        <header className="mb-4 rounded-2xl border border-slate-700/50 bg-slate-900/60 p-4 backdrop-blur-xl">
          <p className="text-xs uppercase tracking-[0.18em] text-indigo-200">Retail Intelligence Platform</p>
          <div className="mt-2 flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-white">{getHeaderTitle()}</h2>
            {activeFeature === 'sales-analytics' && selectedSalesTab === 'qna-chatbot' && (
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/50 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-100">
                <Bot className="h-3.5 w-3.5" />
                Live Assistant
              </div>
            )}
          </div>
        </header>

        <section className="min-h-0 flex-1 overflow-hidden rounded-2xl border border-slate-700/50 bg-white/95 shadow-2xl shadow-slate-950/40">
          {activeFeature === 'sales-analytics' ? (
            selectedSalesTab === 'qna-chatbot' ? (
              <ChatBox />
            ) : (
              <div className="flex h-full items-center justify-center bg-slate-50">
                <div className="text-center">
                  <h2 className="text-3xl font-semibold text-slate-800">Sales Analytic</h2>
                  <p className="mt-2 text-slate-500">Blank for now</p>
                </div>
              </div>
            )
          ) : (
            <div className="flex h-full items-center justify-center bg-slate-50">
              <div className="text-center">
                <h2 className="text-3xl font-semibold text-slate-800">
                  {featureItems.find((item) => item.key === activeFeature)?.title}
                </h2>
                <p className="mt-2 text-slate-500">This module is clickable and reserved for upcoming integration.</p>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
