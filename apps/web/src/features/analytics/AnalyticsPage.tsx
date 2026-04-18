import { useEffect, useState } from "react";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { api } from "../../lib/api/client";
import { AnalyticsSummary } from "../../lib/api/types";

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    api.get<AnalyticsSummary>("/analytics/summary").then(setSummary).catch(console.error);
  }, []);

  return (
    <Page title="Analytics" description="MVP analytics focus on adherence, completed work, and recent volume trend.">
      {summary ? (
        <div className="grid grid--metrics">
          <Card>
            <p className="eyebrow">Adherence</p>
            <h3>{Math.round(summary.adherence_rate * 100)}%</h3>
          </Card>
          <Card>
            <p className="eyebrow">Planned</p>
            <h3>{summary.planned_count}</h3>
          </Card>
          <Card>
            <p className="eyebrow">Sessions</p>
            <h3>{summary.total_sessions}</h3>
          </Card>
          <Card>
            <p className="eyebrow">Completed sets</p>
            <h3>{summary.total_completed_sets}</h3>
          </Card>
          <Card>
            <p className="eyebrow">Volume</p>
            <h3>{summary.total_volume.toFixed(0)}</h3>
          </Card>
          <Card>
            <p className="eyebrow">Recent trend</p>
            <ul className="list">
              {summary.recent_volume.map((row) => (
                <li key={row.date}>
                  {row.date}: {row.volume.toFixed(0)}
                </li>
              ))}
            </ul>
          </Card>
        </div>
      ) : (
        <Card>Loading analytics...</Card>
      )}
    </Page>
  );
}

