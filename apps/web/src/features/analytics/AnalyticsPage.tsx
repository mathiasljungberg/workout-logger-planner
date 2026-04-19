import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { QueryBoundary } from "../../components/QueryBoundary";
import { useAnalyticsSummary } from "../../lib/api/queries";

export function AnalyticsPage() {
  const { data: summary, isLoading, error } = useAnalyticsSummary();

  return (
    <Page title="Analytics" description="MVP analytics focus on adherence, completed work, and recent volume trend.">
      <QueryBoundary isLoading={isLoading} error={error} loadingLabel="Loading analytics...">
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
        ) : null}
      </QueryBoundary>
    </Page>
  );
}
