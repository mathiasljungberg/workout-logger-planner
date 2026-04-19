import { ReactNode } from "react";

type Props = {
  isLoading: boolean;
  error: unknown;
  children: ReactNode;
  loadingLabel?: string;
};

export function QueryBoundary({ isLoading, error, children, loadingLabel = "Loading..." }: Props) {
  if (isLoading) {
    return <div className="query-state query-state--loading">{loadingLabel}</div>;
  }
  if (error) {
    const message = error instanceof Error ? error.message : String(error);
    return <div className="query-state query-state--error">Error: {message}</div>;
  }
  return <>{children}</>;
}
