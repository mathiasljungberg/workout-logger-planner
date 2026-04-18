import { PropsWithChildren, ReactNode } from "react";

type PageProps = PropsWithChildren<{
  title: string;
  description?: string;
  action?: ReactNode;
}>;

export function Page({ title, description, action, children }: PageProps) {
  return (
    <section className="page">
      <header className="page__header">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h2>{title}</h2>
          {description ? <p className="page__description">{description}</p> : null}
        </div>
        {action}
      </header>
      {children}
    </section>
  );
}

